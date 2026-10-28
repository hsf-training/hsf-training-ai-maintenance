#!/usr/bin/env python3
"""Clone or update hsf-training repos in a local workspace.

Each repo ends up at <dir>/<repo> on an up-to-date default branch, or on a new
work branch created from it with --branch. Repos with uncommitted changes are
left alone.

Usage:
  python3 scripts/workspace.py REPO ... [--branch NAME] [--dir DIR]
  python3 scripts/workspace.py --all [--kind KIND] [--platform PLATFORM] ...

The default workspace is ../hsf-workspace next to this repository.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from _common import ORG, ROOT, load_inventory


def git(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)


def prepare(entry: dict[str, Any], workspace: Path, branch: str | None) -> tuple[str, str, str]:
    """Return (repo, status, current branch)."""
    name, default = entry["name"], entry.get("default_branch", "")
    path = workspace / name
    if not path.exists():
        proc = subprocess.run(["gh", "repo", "clone", f"{ORG}/{name}", str(path), "--", "--quiet"], capture_output=True, text=True)
        if proc.returncode != 0:
            return name, f"clone failed: {proc.stderr.strip()}", ""
        status = "cloned"
    else:
        if git(path, "status", "--porcelain").stdout.strip():
            current = git(path, "branch", "--show-current").stdout.strip()
            return name, "skipped: uncommitted changes", current
        if git(path, "fetch", "--prune", "--quiet", "origin").returncode != 0:
            return name, "fetch failed", ""
        status = "updated"

    default = default or git(path, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").stdout.strip().removeprefix("origin/")
    for args in (("switch", "--quiet", default), ("merge", "--ff-only", "--quiet", f"origin/{default}")):
        proc = git(path, *args)
        if proc.returncode != 0:
            return name, f"git {args[0]} failed: {proc.stderr.strip()}", default

    if branch:
        if git(path, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0:
            git(path, "switch", "--quiet", branch)
            status += f", existing branch {branch} (not reset)"
        else:
            git(path, "switch", "--quiet", "-c", branch)
    return name, status, git(path, "branch", "--show-current").stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repos", nargs="*", help="repo names")
    parser.add_argument("--all", action="store_true", help="all active repos in the inventory")
    parser.add_argument("--kind", help="only repos of this kind (with --all)")
    parser.add_argument("--platform", help="only repos on this platform (with --all)")
    parser.add_argument("--branch", help="create (or switch to) this work branch from the default branch")
    parser.add_argument("--dir", type=Path, default=ROOT.parent / "hsf-workspace", help="workspace directory")
    args = parser.parse_args()

    inventory = {e["name"]: e for e in load_inventory()}
    if args.all:
        targets = [
            e
            for e in inventory.values()
            if not e.get("archived")
            and (not args.kind or e.get("kind") == args.kind)
            and (not args.platform or e.get("platform") == args.platform)
        ]
    elif args.repos:
        targets = [inventory.get(r, {"name": r}) for r in args.repos]
        archived = [e["name"] for e in targets if e.get("archived")]
        if archived:
            sys.exit(f"Archived repos are read-only: {', '.join(archived)}")
    else:
        parser.error("give repo names or --all")

    args.dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda e: prepare(e, args.dir, args.branch), targets))

    width = max(len(r[0]) for r in results)
    for name, status, branch in sorted(results):
        print(f"{name:<{width}}  {branch:<20}  {status}")
    print(f"\nWorkspace: {args.dir.resolve()}")
    if any(not r[1].startswith(("cloned", "updated")) for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
