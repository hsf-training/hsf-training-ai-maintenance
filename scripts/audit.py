#!/usr/bin/env python3
"""Audit hsf-training repositories against knowledge/standards.md.

Gathers facts through the GitHub API (no cloning) and runs the mechanical
checks whose ids are documented in knowledge/standards.md. Content-level
checks (e.g. outdated code in lessons) are left to the agent.

Usage:
  python3 scripts/audit.py [REPO ...] [--kind KIND] [--platform PLATFORM]
                           [--json FILE] [--markdown FILE]

Without REPO arguments, all active repos in knowledge/repos.toml are audited
(run scripts/inventory.py first). The Markdown report goes to stdout unless
--markdown is given.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import PurePosixPath
from typing import Any

from _common import ORG, GhError, fetch_file, gh_api, gh_graphql, load_inventory, repo_tree

SEVERITIES = ("high", "medium", "low", "info")
TEAM = f"@{ORG}/training-conveners"
NOW = datetime.now(timezone.utc)
STALE_BRANCH_AGE = timedelta(days=365)
BOT_PR_AGE = timedelta(days=30)
BOT_AUTHORS = ("dependabot", "pre-commit-ci", "app/dependabot", "app/pre-commit-ci")
ORG_DEFAULT_FILES = (
    ".github/ISSUE_TEMPLATE.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/FUNDING.yml",
    "ISSUE_TEMPLATE.md",
    "PULL_REQUEST_TEMPLATE.md",
)
LICENSE_RE = re.compile(r"^(LICEN[CS]E|COPYING)([-.][\w.-]+)?$", re.IGNORECASE)
TRACKED_HOOKS = ("pre-commit/pre-commit-hooks", "codespell-project/codespell")
# Branches the Carpentries Workbench (sandpaper) creates and uses itself.
SANDPAPER_BRANCHES = re.compile(r"^(md-outputs.*|legacy/.*)$")

REPO_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    deleteBranchOnMerge description homepageUrl
    refs(refPrefix: "refs/heads/", first: 100) {
      nodes {
        name
        target { ... on Commit { committedDate oid } }
        openPRs: associatedPullRequests(states: [OPEN]) { totalCount }
        mergedPRs: associatedPullRequests(first: 20, states: [MERGED]) { nodes { headRefOid } }
      }
    }
    pullRequests(states: OPEN, first: 100) {
      nodes { number createdAt author { login } }
    }
  }
}
"""


@dataclass
class Finding:
    check: str
    severity: str
    message: str


@dataclass
class RepoReport:
    name: str
    kind: str
    platform: str
    findings: list[Finding] = field(default_factory=list)
    ignored: list[str] = field(default_factory=list)
    error: str = ""

    def add(self, check: str, severity: str, message: str) -> None:
        self.findings.append(Finding(check, severity, message))


def latest_hook_versions() -> dict[str, str]:
    versions = {}
    for repo in TRACKED_HOOKS:
        release = gh_api(f"repos/{repo}/releases/latest")
        if release:
            versions[repo] = release["tag_name"]
    return versions


def parse_precommit_revs(text: str) -> dict[str, str]:
    """Map 'owner/repo' -> rev for each repo in a .pre-commit-config.yaml."""
    revs, current = {}, None
    for line in text.splitlines():
        if m := re.match(r"\s*-\s*repo:\s*https://github\.com/([^\s]+?)(?:\.git)?\s*$", line):
            current = m.group(1).lower()
        elif (m := re.match(r"\s*rev:\s*['\"]?([^'\"\s]+)", line)) and current:
            revs[current] = m.group(1)
            current = None
    return revs


def jupyter_book_pinned_below_2(texts: list[str]) -> bool | None:
    """True if any jupyter-book requirement is capped below 2, None if not mentioned."""
    specs = [
        m.group(1)
        for text in texts
        for m in re.finditer(r"jupyter[-_]book\s*([^\n\"'#]*)", text, flags=re.IGNORECASE)
    ]
    if not specs:
        return None
    # "<2", "<2.0", "==1.x", "~=1.x", or a conda-style "=1.x" pin (but not ">=0.15").
    return any(re.search(r"<\s*2(\.0)*\b|==\s*[01]\.|~=\s*[01]\.|(?<![<>!~=])=\s*[01]\.", s) for s in specs)


def mentions(text: str) -> set[str]:
    found = set(re.findall(r"(?<![\w.])@([\w-]+(?:/[\w-]+)?)", text))
    return found - {"mention", "mentions", "username", "githubname"}  # prose, not handles


def audit_repo(entry: dict[str, Any], hook_versions: dict[str, str]) -> RepoReport:
    name = entry["name"]
    kind = entry.get("kind") or "uncurated"
    platform = entry.get("platform", "")
    report = RepoReport(name, kind, platform)
    try:
        _audit(report, entry, hook_versions)
    except GhError as exc:
        report.error = str(exc)
    ignore = set(entry.get("ignore_checks", []))
    report.ignored = sorted({f.check for f in report.findings if f.check in ignore})
    report.findings = [f for f in report.findings if f.check not in ignore]
    return report


def _audit(report: RepoReport, entry: dict[str, Any], hook_versions: dict[str, str]) -> None:
    name, kind, platform = report.name, report.kind, report.platform
    branch = entry.get("default_branch", "")
    is_fork = kind == "fork"
    is_lesson = kind == "lesson"
    is_jekyll = platform == "jekyll-carpentries"

    if kind == "uncurated":
        report.add("inventory-uncurated", "info", "No curated `kind` in knowledge/repos.toml; checks assume a non-lesson repo.")

    tree = repo_tree(name, branch)
    paths = list(tree)
    blobs = [p for p, kind_ in tree.items() if kind_ == "blob"]
    pathset = set(paths)
    root_files = {p for p in paths if "/" not in p}
    meta = gh_graphql(REPO_QUERY, owner=ORG, name=name)["repository"]

    def text(path: str) -> str:
        return (fetch_file(name, path, branch) or "") if path in pathset else ""

    workflow_paths = [p for p in paths if re.match(r"\.github/workflows/[^/]+\.ya?ml$", p)]
    workflow_texts = {p: text(p) for p in workflow_paths}
    precommit = text(".pre-commit-config.yaml")
    dependabot = text(".github/dependabot.yml") or text(".github/dependabot.yaml")
    stale_cfg = text(".github/stale.yml")
    welcome_cfg = text(".github/config.yml")
    # Shared files at any depth, e.g. inside a cookiecutter template directory.
    shared = {
        p: text(p)
        for p in blobs
        if p.endswith((".pre-commit-config.yaml", ".github/dependabot.yml", ".github/stale.yml", ".github/config.yml"))
    }
    readme = next((p for p in root_files if p.lower() == "readme.md"), None)

    # --- Licensing and community files -------------------------------------
    if not is_fork:
        licenses = sorted(p for p in root_files if LICENSE_RE.match(p))
        if not licenses:
            report.add("license-missing", "high", "No license file. Ask the authors to choose one (default: CC BY 4.0 + BSD-3-Clause).")
        elif any("Software Carpentry" in text(p) for p in licenses):
            report.add(
                "license-carpentries",
                "medium",
                f"Carpentries-derived license text in {', '.join(licenses)}. Split into LICENSE (CC BY 4.0) + LICENSE-CODE (MIT).",
            )
        if not readme:
            report.add("readme-missing", "high", "No README.md.")
        if name != ".github":
            dupes = [p for p in ORG_DEFAULT_FILES if p in pathset]
            if dupes:
                report.add("org-file-duplicate", "low", f"Per-repo copies of org-wide files: {', '.join(dupes)}.")
        if {"CONDUCT.md", "CODE_OF_CONDUCT.md"} <= root_files:
            report.add("conduct-duplicate", "low", "Both CONDUCT.md and CODE_OF_CONDUCT.md exist.")
        if ".travis.yml" in pathset:
            report.add("travis", "low", "Leftover .travis.yml (Travis CI is no longer used).")
        headers = sorted(p for p, t in shared.items() if "CENTRALLY MAINTAINED FILE" in t)
        if headers:
            report.add("legacy-header", "low", f"Old CENTRALLY MAINTAINED FILE header in {', '.join(headers)}.")

    # --- Jekyll specifics ----------------------------------------------------
    if is_jekyll:
        config = text("_config.yml")
        if not re.search(r"^remote_theme:", config, flags=re.M):
            report.add("jekyll-vendored-theme", "medium", "No remote_theme; the full Carpentries theme is vendored. Needs migration to hsf-training-theme.")
        else:
            leftovers = [d for d in ("_layouts", "assets", "bin") if d in pathset]
            if leftovers:
                report.add("jekyll-theme-leftovers", "low", f"Uses remote_theme but still has {', '.join(leftovers)}/.")
        if "Commands for both workshop and lesson websites" in text("Makefile"):
            report.add("carpentries-makefile", "low", "Carpentries Makefile (depends on removed bin/ scripts).")
        if "_episodes_rmd" in pathset and not any(
            p.startswith("_episodes_rmd/") and not p.endswith(".gitkeep") for p in blobs
        ):
            report.add("empty-episodes-rmd", "low", "Empty _episodes_rmd/ directory.")
        if "<USERNAME>/<PROJECT>" in config:
            report.add("config-placeholder", "low", "_config.yml has `repository: <USERNAME>/<PROJECT>`.")

    # --- Tooling -------------------------------------------------------------
    if not is_fork:
        if not precommit:
            report.add("precommit-missing", "medium", "No .pre-commit-config.yaml.")
        else:
            revs = parse_precommit_revs(precommit)
            behind = [
                f"{repo} {revs[repo]} (latest {latest})"
                for repo, latest in hook_versions.items()
                if repo in revs and revs[repo].lstrip("v") != latest.lstrip("v")
            ]
            if behind:
                report.add("precommit-outdated", "low", f"Outdated hooks (is pre-commit.ci autoupdate running?): {'; '.join(behind)}.")
        if workflow_paths and not dependabot:
            report.add("dependabot-missing", "medium", "Has workflows but no .github/dependabot.yml.")
        elif dependabot and "github-actions" not in dependabot:
            report.add("dependabot-no-actions", "low", "dependabot.yml doesn't update github-actions.")
        missing_bots = [f for f, t in ((".github/stale.yml", stale_cfg), (".github/config.yml", welcome_cfg)) if not t]
        if missing_bots and name != ".github":
            report.add("bots-missing", "low", f"Missing bot config: {', '.join(missing_bots)}.")
        bot_files = {p: t for p, t in shared.items() if p.endswith((".github/stale.yml", ".github/config.yml"))}
        people = sorted({m for t in bot_files.values() for m in mentions(t) if f"@{m}" != TEAM})
        if people:
            where = ", ".join(sorted(p for p, t in bot_files.items() if any(f"@{m}" in t for m in people)))
            report.add("bots-individual-mentions", "medium", f"Bot messages in {where} mention individuals ({', '.join('@' + p for p in people)}) instead of {TEAM}.")

    # --- Build ---------------------------------------------------------------
    if platform == "jupyter-book-1":
        env_texts = [
            text(p)
            for p in paths
            if PurePosixPath(p).name in ("requirements.txt", "environment.yml", "environment.yaml") and p.count("/") <= 1
        ]
        env_pinned = jupyter_book_pinned_below_2(env_texts)
        ci_pinned = jupyter_book_pinned_below_2(list(workflow_texts.values()))
        if env_pinned is False and ci_pinned:
            report.add("build-tool-unpinned", "medium", "CI caps jupyter-book below 2, but the environment files don't, so local builds get JB2, which can't build this JB1 book.")
        elif env_pinned is False or (env_pinned is None and ci_pinned is False):
            report.add("build-tool-unpinned", "high", "Jupyter Book 1 project, but jupyter-book is not capped below 2 (a fresh install gets JB2, which can't build it).")

    workflows = gh_api(f"repos/{ORG}/{name}/actions/workflows?per_page=100") or {}
    disabled = [w["name"] for w in workflows.get("workflows", []) if w.get("state") == "disabled_inactivity"]
    if disabled:
        report.add("workflow-disabled", "medium", f"Workflows disabled for inactivity: {', '.join(disabled)}.")
    if workflow_paths and not workflows.get("total_count"):
        report.add("actions-not-running", "medium", f"{len(workflow_paths)} workflow file(s), but GitHub has no workflows registered: Actions is probably disabled (common for forks).")

    runs = (gh_api(f"repos/{ORG}/{name}/actions/runs?branch={branch}&per_page=100&exclude_pull_requests=true") or {}).get("workflow_runs", [])
    latest_runs: dict[str, dict[str, Any]] = {}
    for run in runs:  # newest first
        latest_runs.setdefault(run.get("path") or run["name"], run)
    failing, dependabot_failing = [], []
    for path, run in latest_runs.items():
        if run.get("conclusion") not in ("failure", "timed_out", "startup_failure"):
            continue
        label = f"{run['name']} ({run['created_at'][:10]})"
        if path.startswith("dynamic/dependabot"):
            dependabot_failing.append(label)
        elif path.startswith("dynamic/pages") and entry.get("pages") == "workflow":
            continue  # leftover from before the repo switched to workflow deploys
        elif path.startswith("dynamic/") or path in pathset:  # skip workflows that were deleted since
            failing.append(label)
    if failing:
        report.add("ci-failing", "high", f"Latest run on {branch} failed: {', '.join(failing)}.")
    if dependabot_failing:
        report.add("dependabot-failing", "low", f"Latest Dependabot update job failed: {', '.join(dependabot_failing)}.")

    pages = gh_api(f"repos/{ORG}/{name}/pages")
    if pages and pages.get("status") == "errored":
        report.add("pages-errored", "high", "GitHub Pages reports status `errored`.")
    if pages and pages.get("build_type") == "legacy" and any("actions/deploy-pages" in t for t in workflow_texts.values()):
        report.add("pages-source-mismatch", "medium", "Pages builds from a branch, but a workflow also deploys with actions/deploy-pages: two deploys race on every push. Switch the Pages source to GitHub Actions.")

    if not is_fork:
        all_workflows = "\n".join(workflow_texts.values())
        if "github-action-markdown-link-check" in all_workflows:
            report.add("link-check-deprecated", "low", "Uses the unmaintained gaurav-nelson markdown-link-check action; switch to lychee.")
        elif is_lesson and not re.search(r"lychee|link-check|linkcheck", all_workflows + precommit):
            report.add("no-link-check", "info", "No automated link checking.")

    # --- Settings and hygiene ------------------------------------------------
    if not meta["deleteBranchOnMerge"]:
        report.add("delete-branch-on-merge-off", "low", "Automatically delete head branches is off.")
    if not is_fork and not (meta["description"] or "").strip():
        report.add("description-missing", "low", "Repository description is empty.")
    site = entry.get("site", "")
    if site and not (meta["homepageUrl"] or "").strip():
        report.add("homepage-missing", "low", f"Homepage is not set (site: {site}).")

    pages_branch = entry.get("pages", "").removeprefix("legacy:") if entry.get("pages", "").startswith("legacy:") else ""
    stale = []
    for ref in meta["refs"]["nodes"]:
        if ref["name"] in (branch, pages_branch) or ref["openPRs"]["totalCount"]:
            continue  # deleting the head of an open PR would close it
        if platform == "sandpaper" and SANDPAPER_BRANCHES.match(ref["name"]):
            continue
        target = ref.get("target") or {}
        date = target.get("committedDate")
        # Merged only if the branch tip is what got merged, not just "a PR from this name was merged".
        merged = target.get("oid") in {pr["headRefOid"] for pr in ref["mergedPRs"]["nodes"]}
        old = date and NOW - datetime.fromisoformat(date.replace("Z", "+00:00")) > STALE_BRANCH_AGE
        if merged or old:
            stale.append(f"{ref['name']} ({'merged' if merged else 'last commit ' + date[:10]})")
    if stale:
        report.add("stale-branches", "low", f"{len(stale)} stale branch(es): {', '.join(stale)}.")

    bot_prs = [
        pr["number"]
        for pr in meta["pullRequests"]["nodes"]
        if (pr.get("author") or {}).get("login", "") in BOT_AUTHORS
        and NOW - datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00")) > BOT_PR_AGE
    ]
    if bot_prs:
        report.add("bot-prs-pending", "low", f"Bot PRs open for more than {BOT_PR_AGE.days} days: {', '.join('#' + str(n) for n in bot_prs)}.")

    # --- Training Center -----------------------------------------------------
    if is_lesson and not entry.get("training_center"):
        report.add("training-center-missing", "medium", "Not listed in training-center/data/data.yaml.")


def org_findings(inventory: list[dict[str, Any]]) -> list[Finding]:
    return [
        Finding("training-center-archived", "medium", f"{e['name']} is archived but listed in the Training Center ({', '.join(e['training_center'])}).")
        for e in inventory
        if e.get("archived") and e.get("training_center")
    ]


def markdown(reports: list[RepoReport], org: list[Finding]) -> str:
    def counts(r: RepoReport) -> list[int]:
        return [sum(f.severity == s for f in r.findings) for s in SEVERITIES]

    lines = [f"# Audit of {ORG} ({NOW:%Y-%m-%d})", ""]
    lines += ["| Repo | Kind | Platform | " + " | ".join(SEVERITIES) + " |", "|---|---|---|" + "---|" * len(SEVERITIES)]
    for r in sorted(reports, key=lambda r: [-c for c in counts(r)]):
        cells = ["error"] * len(SEVERITIES) if r.error else [str(c) for c in counts(r)]
        lines.append(f"| {r.name} | {r.kind} | {r.platform} | " + " | ".join(cells) + " |")
    if org:
        lines += ["", "## Organization", ""] + [f"- **{f.severity}** `{f.check}`: {f.message}" for f in org]
    for r in sorted(reports, key=lambda r: r.name.lower()):
        if not r.findings and not r.error and not r.ignored:
            continue
        lines += ["", f"## {r.name}", ""]
        if r.error:
            lines.append(f"- **error**: {r.error}")
        if r.ignored:
            lines.append(f"- ignored via `ignore_checks` in repos.toml: {', '.join(r.ignored)}")
        order = {s: i for i, s in enumerate(SEVERITIES)}
        lines += [f"- **{f.severity}** `{f.check}`: {f.message}" for f in sorted(r.findings, key=lambda f: order[f.severity])]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repos", nargs="*", help="repo names (default: all active repos in the inventory)")
    parser.add_argument("--kind", help="only audit repos of this kind")
    parser.add_argument("--platform", help="only audit repos on this platform")
    parser.add_argument("--json", help="write facts and findings as JSON to this file")
    parser.add_argument("--markdown", help="write the Markdown report to this file instead of stdout")
    args = parser.parse_args()

    inventory = load_inventory()
    if not inventory:
        sys.exit("knowledge/repos.toml is missing; run scripts/inventory.py first.")
    by_name = {e["name"]: e for e in inventory}
    unknown = [r for r in args.repos if r not in by_name]
    if unknown:
        sys.exit(f"Not in the inventory: {', '.join(unknown)} (run scripts/inventory.py?)")
    targets = [by_name[r] for r in args.repos] or [e for e in inventory if not e.get("archived")]
    targets = [
        e
        for e in targets
        if (not args.kind or e.get("kind") == args.kind) and (not args.platform or e.get("platform") == args.platform)
    ]

    hook_versions = latest_hook_versions()
    with ThreadPoolExecutor(max_workers=6) as pool:
        reports = list(pool.map(lambda e: audit_repo(e, hook_versions), targets))
    org = org_findings(inventory) if not args.repos else []

    if args.json:
        with open(args.json, "w") as f:
            json.dump({"date": NOW.isoformat(), "org": [asdict(x) for x in org], "repos": [asdict(r) for r in reports]}, f, indent=2)
    report = markdown(reports, org)
    if args.markdown:
        with open(args.markdown, "w") as f:
            f.write(report)
    else:
        sys.stdout.write(report)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
