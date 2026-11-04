#!/usr/bin/env python3
"""Check the external links in a lesson's sources.

Finds http(s) URLs in Markdown, notebooks, reStructuredText, config and code
files, requests each unique URL once, and sorts them into:

  broken    404/410, unknown host, or other definite failures
  moved     permanently redirected (301/308) to a different page
  check     inconclusive: blocked (401/403/429), server errors, timeouts
  ok        reachable (trivial redirects such as http->https are ok)

Only "broken" and "moved" are findings. "check" needs a manual look, since
many sites block scripted requests.

Usage:
  python3 check_links.py PATH ... [--exclude REGEX ...] [--json FILE]

Exits with 1 if any link is broken.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

EXTENSIONS = {".md", ".markdown", ".ipynb", ".rst", ".txt", ".yml", ".yaml", ".toml", ".py", ".cfg", ".tex", ".html"}
SKIP_DIRS = {".git", "_site", "_build", "node_modules", ".venv", "venv", ".vendor", "vendor", ".jekyll-cache", "__pycache__", "public"}
URL_RE = re.compile(r"https?://[^\s<>\"'`\\)\]}|]+")
TRAILING = ".,;:!?*_"
SKIP_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "example.com", "example.org", "www.example.com"}
USER_AGENT = "Mozilla/5.0 (compatible; hsf-training-link-check)"
# GitHub pages that answer 404 to anyone not logged in.
GITHUB_LOGIN_ONLY = re.compile(r"^/(issues|pulls|search|notifications|settings|codespaces|new|organizations/[^/]+/repositories/new)(/|$)")


def find_urls(paths: list[Path], exclude: list[re.Pattern[str]]) -> dict[str, list[str]]:
    """Return {url: ["file:line", ...]}."""
    found: dict[str, list[str]] = {}
    files = []
    for path in paths:
        if path.is_file():
            files.append(path)
        else:
            files += [p for p in path.rglob("*") if p.is_file() and p.suffix in EXTENSIONS and not SKIP_DIRS & set(p.parts)]
    for file in sorted(files):
        try:
            lines = file.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(lines, 1):
            for match in URL_RE.finditer(line):
                url = match.group().rstrip(TRAILING)
                # uproot-style "file.root:tree" paths.
                url = re.sub(r"(\.root):[\w./-]*$", r"\1", url)
                # Unbalanced ")" from Markdown links whose URL contains "(".
                if url.count("(") < url.count(")"):
                    url = url[: url.rfind(")")]
                host = urlsplit(url).hostname or ""
                if not host or "." not in host or host in SKIP_HOSTS or "{" in url or "<" in url:
                    continue
                if any(p.search(url) for p in exclude):
                    continue
                found.setdefault(url, []).append(f"{file}:{number}")
    return found


class RecordRedirects(urllib.request.HTTPRedirectHandler):
    def __init__(self) -> None:
        self.codes: list[int] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        self.codes.append(code)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def normalize(url: str) -> str:
    """Drop differences that don't matter: scheme, www., trailing slash, fragment."""
    parts = urlsplit(url)
    host = (parts.hostname or "").removeprefix("www.")
    return urlunsplit(("", host, parts.path.rstrip("/"), parts.query, ""))


def request(url: str, method: str, timeout: float) -> tuple[int, str, list[int]]:
    redirects = RecordRedirects()
    opener = urllib.request.build_opener(redirects)
    req = urllib.request.Request(url.split("#")[0], method=method, headers={"User-Agent": USER_AGENT})
    try:
        with opener.open(req, timeout=timeout) as resp:
            return resp.status, resp.geturl(), redirects.codes
    except urllib.error.HTTPError as err:
        return err.code, err.geturl() or url, redirects.codes


def check(url: str, timeout: float) -> dict[str, object]:
    result: dict[str, object] = {"url": url}
    try:
        status, final, codes = request(url, "HEAD", timeout)
        if status >= 400:  # many servers mishandle HEAD
            status, final, codes = request(url, "GET", timeout)
    except urllib.error.URLError as err:
        reason = err.reason
        if isinstance(reason, socket.gaierror):
            return result | {"status": "broken", "detail": "unknown host"}
        if isinstance(reason, TimeoutError | socket.timeout):
            return result | {"status": "check", "detail": "timeout"}
        return result | {"status": "check", "detail": str(reason)}
    except (TimeoutError, socket.timeout):
        return result | {"status": "check", "detail": "timeout"}
    except Exception as err:  # noqa: BLE001 - report anything else as inconclusive
        return result | {"status": "check", "detail": f"{type(err).__name__}: {err}"}

    result["code"] = status
    parts = urlsplit(url)
    if status == 404 and parts.hostname == "github.com" and GITHUB_LOGIN_ONLY.match(parts.path):
        return result | {"status": "check", "detail": "404, needs a GitHub login"}
    if status in (404, 410):
        return result | {"status": "broken", "detail": str(status)}
    if status in (401, 403, 429) or status >= 400:
        return result | {"status": "check", "detail": str(status)}
    if re.search(r"/(login|signin|sign_in|auth)\b", urlsplit(final).path, re.IGNORECASE):
        return result | {"status": "check", "detail": f"redirects to a login page: {final}"}
    if any(code in (301, 308) for code in codes) and normalize(final) != normalize(url):
        return result | {"status": "moved", "detail": final}
    return result | {"status": "ok", "detail": final if final != url else ""}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("paths", nargs="+", type=Path, help="files or directories to scan")
    parser.add_argument("--exclude", action="append", default=[], metavar="REGEX", help="skip URLs matching REGEX (repeatable)")
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--json", type=Path, metavar="FILE", help="also write all results as JSON")
    args = parser.parse_args()

    urls = find_urls(args.paths, [re.compile(e) for e in args.exclude])
    print(f"Checking {len(urls)} unique URLs...", file=sys.stderr)
    with ThreadPoolExecutor(args.workers) as pool:
        results = list(pool.map(lambda u: check(u, args.timeout), urls))
    for r in results:
        r["locations"] = urls[str(r["url"])]

    for status in ("broken", "moved", "check"):
        group = [r for r in results if r["status"] == status]
        if not group:
            continue
        print(f"\n## {status} ({len(group)})\n")
        for r in sorted(group, key=lambda r: str(r["url"])):
            print(f"- {r['url']}  [{r['detail']}]")
            for loc in r["locations"][:5]:  # type: ignore[index]
                print(f"    {loc}")
    ok = sum(r["status"] == "ok" for r in results)
    print(f"\n{ok} ok, {len(results) - ok} to look at.")

    if args.json:
        args.json.write_text(json.dumps(results, indent=2) + "\n")
    return 1 if any(r["status"] == "broken" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
