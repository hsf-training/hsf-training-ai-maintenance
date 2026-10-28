#!/usr/bin/env python3
"""Refresh knowledge/repos.toml from GitHub.

Derived fields are overwritten from the GitHub API. Curated fields (`kind`,
`companion_of`, `notes`) are kept from the existing file. Prints a summary of
repos that need curation and of mismatches with the Training Center catalog.

Usage: python3 scripts/inventory.py [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from _common import INVENTORY, ORG, fetch_file, gh_api, gh_graphql, load_inventory, repo_tree, toml_value

CURATED = ("kind", "companion_of", "notes")
DERIVED = ("archived", "fork_of", "default_branch", "platform", "pages", "site", "training_center", "description")
KINDS = ("lesson", "companion", "infra", "fork", "other")

HEADER = f"""\
# Inventory of the {ORG} repositories.
#
# Regenerate with `python3 scripts/inventory.py` (see skills/repo-inventory).
#
# Curated fields, edited by hand and kept by the script:
#   kind          one of: {", ".join(KINDS)}
#   companion_of  for companion repos, the lesson repo they belong to
#   notes         anything an agent should know before touching the repo
#
# Derived fields, overwritten by the script:
#   archived, fork_of, default_branch, description
#   platform         see knowledge/platforms/README.md
#   pages            GitHub Pages build type ("legacy:<branch>", "workflow" or "")
#   site             GitHub Pages URL
#   training_center  ids of the modules in training-center/data/data.yaml
#                    whose repository is this repo
"""

REPOS_QUERY = """
query($org: String!, $cursor: String) {
  organization(login: $org) {
    repositories(first: 100, after: $cursor, orderBy: {field: NAME, direction: ASC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name isArchived isFork description
        parent { nameWithOwner }
        defaultBranchRef { name }
      }
    }
  }
}
"""

SKIP_DIRS = ("_vendor/", "node_modules/", "_build/", ".git/")


def detect_platform(paths: list[str]) -> str:
    """Guess the lesson platform from the repository file tree."""
    paths = [p for p in paths if not p.startswith(SKIP_DIRS)]
    names = set(paths)

    def exists_shallow(filename: str, max_depth: int = 1) -> bool:
        return any(
            (p == filename or p.endswith("/" + filename)) and p.count("/") <= max_depth for p in paths
        )

    if exists_shallow("myst.yml"):
        return "myst-jupyter-book-2"
    if "hugo.toml" in names or ("config.toml" in names and "go.mod" in names):
        return "hugo"
    if "astro.config.mjs" in names:
        return "astro"
    if "config.yaml" in names and "episodes" in names:
        return "sandpaper"
    if "_config.yml" in names and "_episodes" in names:
        return "jekyll-carpentries"
    if exists_shallow("_toc.yml", max_depth=2):
        return "jupyter-book-1"
    if "site/jupyter-lite.json" in names:
        return "jupyterlite"
    if "conf.py" in names:
        return "sphinx"
    if any(p.endswith(".tex") for p in paths):
        return "latex"
    return "none"


def training_center_modules() -> list[dict[str, str]]:
    """Parse id/repository/status of each module in training-center/data/data.yaml.

    The file is a flat YAML list of mappings, so a line-based parser is enough
    and keeps this script free of dependencies.
    """
    text = fetch_file("training-center", "data/data.yaml") or ""
    modules: list[dict[str, str]] = []
    for line in text.splitlines():
        m = re.match(r"^(- |  )(\w+):\s*(.*)$", line)
        if not m:
            continue
        if m.group(1) == "- ":
            modules.append({})
        if modules:
            modules[-1][m.group(2)] = m.group(3).strip().strip("'\"")
    return modules


def repo_key(url: str) -> str | None:
    m = re.match(rf"https?://github\.com/{ORG}/([^/#?]+)", url, flags=re.IGNORECASE)
    return m.group(1).removesuffix(".git").lower() if m else None


def list_repos() -> list[dict[str, Any]]:
    repos, cursor = [], ""
    while True:
        variables = {"org": ORG}
        if cursor:
            variables["cursor"] = cursor
        page = gh_graphql(REPOS_QUERY, **variables)["organization"]["repositories"]
        repos += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            return repos
        cursor = page["pageInfo"]["endCursor"]


def derive(node: dict[str, Any]) -> dict[str, Any]:
    name = node["name"]
    branch = (node.get("defaultBranchRef") or {}).get("name", "")
    entry: dict[str, Any] = {
        "archived": node["isArchived"],
        "fork_of": (node.get("parent") or {}).get("nameWithOwner", ""),
        "default_branch": branch,
        "description": node.get("description") or "",
        "platform": "",
        "pages": "",
        "site": "",
    }
    if node["isArchived"] or not branch:
        return entry
    entry["platform"] = detect_platform(repo_tree(name, branch))
    pages = gh_api(f"repos/{ORG}/{name}/pages")
    if pages:
        if pages.get("build_type") == "legacy":
            entry["pages"] = f"legacy:{(pages.get('source') or {}).get('branch', '')}"
        else:
            entry["pages"] = pages.get("build_type") or ""
        entry["site"] = pages.get("html_url") or ""
    return entry


def write_inventory(entries: list[dict[str, Any]]) -> None:
    lines = [HEADER]
    for e in entries:
        lines.append("[[repo]]")
        lines.append(f"name = {toml_value(e['name'])}")
        for key in CURATED + DERIVED:
            value = e.get(key)
            if value in (None, "", []) and (e.get("archived") or key not in ("kind", "notes")):
                continue
            if e.get("archived") and key in ("platform", "pages", "site", "default_branch", "description"):
                continue
            lines.append(f"{key} = {toml_value(value if value is not None else '')}")
        lines.append("")
    INVENTORY.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="print the summary but don't write the file")
    args = parser.parse_args()

    old = {e["name"]: e for e in load_inventory()}
    nodes = list_repos()
    with ThreadPoolExecutor(max_workers=8) as pool:
        derived = dict(zip((n["name"] for n in nodes), pool.map(derive, nodes)))

    modules = training_center_modules()
    by_repo: dict[str, list[str]] = {}
    for mod in modules:
        key = repo_key(mod.get("repository", ""))
        if key:
            by_repo.setdefault(key, []).append(mod.get("id", "?"))

    entries = []
    for node in nodes:
        name = node["name"]
        entry = {"name": name, **{k: old.get(name, {}).get(k, "") for k in CURATED}, **derived[name]}
        if not entry["kind"] and entry["fork_of"]:
            entry["kind"] = "fork"
        entry["training_center"] = sorted(by_repo.get(name.lower(), []))
        entries.append(entry)
    entries.sort(key=lambda e: (e["archived"], e["name"].lower()))

    # Summary for the operator / agent.
    active = [e for e in entries if not e["archived"]]
    names = {e["name"].lower() for e in entries}
    print(f"{len(active)} active and {len(entries) - len(active)} archived repos in {ORG}.")
    gone = sorted(set(old) - {e["name"] for e in entries})
    if gone:
        print("\nNo longer in the org (removed from inventory):", ", ".join(gone))
    uncurated = [e["name"] for e in active if e["kind"] not in KINDS]
    if uncurated:
        print("\nNeed a curated `kind`:", ", ".join(uncurated))
    listed_archived = [f"{e['name']} ({', '.join(e['training_center'])})" for e in entries if e["archived"] and e["training_center"]]
    if listed_archived:
        print("\nArchived but listed in the Training Center:", "; ".join(listed_archived))
    unlisted = [e["name"] for e in active if e["kind"] == "lesson" and not e["training_center"]]
    if unlisted:
        print("\nActive lessons missing from the Training Center:", ", ".join(unlisted))
    dangling = sorted(
        f"{m.get('id')} -> {m.get('repository')}"
        for m in modules
        if (key := repo_key(m.get("repository", ""))) and key not in names
    )
    if dangling:
        print(f"\nTraining Center entries pointing to non-existent {ORG} repos:", "; ".join(dangling))

    if args.dry_run:
        print("\n(dry run, inventory not written)")
    else:
        write_inventory(entries)
        print(f"\nWrote {INVENTORY.relative_to(INVENTORY.parent.parent)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
