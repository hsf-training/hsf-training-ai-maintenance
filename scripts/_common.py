"""Shared helpers for the maintenance scripts (Python standard library only).

All GitHub access goes through the `gh` CLI, so the operator's existing
authentication is used and no tokens are handled here.
"""

from __future__ import annotations

import base64
import json
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

ORG = "hsf-training"
ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "knowledge" / "repos.toml"

if sys.version_info < (3, 11):
    sys.exit("These scripts need Python >= 3.11 (for tomllib).")


class GhError(RuntimeError):
    pass


def gh_api(path: str, *, method: str = "GET", fields: dict[str, str] | None = None) -> Any:
    """Call the GitHub REST API via `gh api` and return parsed JSON.

    Returns None for 404s, raises GhError for other failures.
    """
    cmd = ["gh", "api", "-X", method, path]
    for key, value in (fields or {}).items():
        cmd += ["-f", f"{key}={value}"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        if "HTTP 404" in proc.stderr or '"status":"404"' in proc.stdout:
            return None
        raise GhError(f"{' '.join(cmd)}: {proc.stderr.strip() or proc.stdout.strip()}")
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def gh_graphql(query: str, **variables: str | int) -> Any:
    """Run a GraphQL query via `gh api graphql` and return the `data` field."""
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        flag = "-F" if isinstance(value, int) else "-f"
        cmd += [flag, f"{key}={value}"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise GhError(f"graphql: {proc.stderr.strip() or proc.stdout.strip()}")
    return json.loads(proc.stdout)["data"]


def fetch_file(repo: str, path: str, ref: str | None = None) -> str | None:
    """Return the text of a file in ORG/repo, or None if it doesn't exist."""
    url = f"repos/{ORG}/{repo}/contents/{path}"
    if ref:
        url += f"?ref={ref}"
    data = gh_api(url)
    if not isinstance(data, dict) or "content" not in data:
        return None
    return base64.b64decode(data["content"]).decode("utf-8", errors="replace")


def repo_tree(repo: str, ref: str) -> dict[str, str]:
    """Map every path in ORG/repo at ref to its type ("blob" or "tree")."""
    data = gh_api(f"repos/{ORG}/{repo}/git/trees/{ref}?recursive=1")
    if not data:
        return {}
    if data.get("truncated"):
        print(f"warning: tree of {repo} is truncated", file=sys.stderr)
    return {entry["path"]: entry["type"] for entry in data.get("tree", [])}


def load_inventory() -> list[dict[str, Any]]:
    if not INVENTORY.exists():
        return []
    with INVENTORY.open("rb") as f:
        return tomllib.load(f).get("repo", [])


def toml_value(value: Any) -> str:
    """Serialize the small subset of TOML values used in the inventory."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # JSON string escapes are valid TOML basic-string escapes.
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(v) for v in value) + "]"
    raise TypeError(f"unsupported TOML value: {value!r}")
