# AGENTS.md

This file guides coding agents (Claude Code, Codex, Gemini CLI, Copilot,
Cursor, ...) that use this repository to maintain the repositories of the
[`hsf-training`](https://github.com/hsf-training) GitHub organization.

This repo contains no application code. It is a knowledge base plus a library
of maintenance procedures. You, the agent, do the work in clones of the
*target* repositories, with the operator's own `gh` credentials, and the
operator reviews everything before it leaves their machine.

## Read first

1. [`knowledge/contribution-policy.md`](knowledge/contribution-policy.md):
   **mandatory** rules for any change you make in the org (read-only by default,
   confirm every outward-facing action, AI disclosure, verify before proposing).
   **Never delete, transfer or rename a repository, and never archive one
   without a human's explicit approval for that repo.**
2. [`knowledge/org-overview.md`](knowledge/org-overview.md): what is in the org,
   infrastructure repos, bots, and common surprises (e.g. many lessons use
   `gh-pages` as the default branch).
   [`knowledge/repos.toml`](knowledge/repos.toml) is the per-repo inventory.
3. [`knowledge/platforms/`](knowledge/platforms/README.md): before touching a
   lesson, identify its platform and read that doc to learn how to build it
   and which files are content.
4. [`knowledge/standards.md`](knowledge/standards.md): what a healthy repo looks
   like, and the [`templates/`](templates/TEMPLATES.md) for shared files.

[`PLAN.md`](PLAN.md) describes the roadmap and the decisions behind it.

## Setup

- `gh auth status` must succeed. The operator's account determines what you can
  do. Most write actions need org membership, and repo settings need admin.
  Operators can restrict the agent with a fine-grained token; see
  [Limiting what the agent's credentials can do](knowledge/contribution-policy.md#limiting-what-the-agents-credentials-can-do).
- Clone target repos **outside** this repo, e.g. into a sibling
  `../hsf-workspace/<repo>`, and work on a new branch based on the repo's
  default branch (`gh repo view hsf-training/<repo> --json defaultBranchRef`).
- Install build tools per platform (Ruby/Bundler for Jekyll, conda or pip for
  Jupyter Book, Node.js for JB2 and Astro, Hugo + Go for Hugo). Use isolated
  environments and don't install globally without asking.

## Skills

Maintenance procedures live in [`skills/`](skills/) in the
[Agent Skills](https://agentskills.io) format. `.claude/skills` and
`.agents/skills` are symlinks to it, so harnesses that support skills discover
them automatically. Otherwise, open the `SKILL.md` that matches the task.

| Skill | Use it to |
|---|---|
| [`repo-inventory`](skills/repo-inventory/SKILL.md) | Refresh `knowledge/repos.toml` |
| [`workspace-setup`](skills/workspace-setup/SKILL.md) | Clone or update target repos in `../hsf-workspace` on a work branch |
| [`repo-audit`](skills/repo-audit/SKILL.md) | Check repos against `knowledge/standards.md` (read-only) |
| [`build-and-preview`](skills/build-and-preview/SKILL.md) | Build a lesson like CI does, diagnose failing builds |
| [`bulk-change`](skills/bulk-change/SKILL.md) | Roll one change out to many repos safely |
| [`sync-shared-files`](skills/sync-shared-files/SKILL.md) | Align pre-commit, dependabot, bot configs, ... with `templates/` |
| [`legacy-cleanup`](skills/legacy-cleanup/SKILL.md) | Remove legacy files, split Carpentries licenses |
| [`repo-settings`](skills/repo-settings/SKILL.md) | Repo settings and stale branches |
| [`content-review`](skills/content-review/SKILL.md) | Review lesson content for outdated or wrong material |
| [`update-dependencies`](skills/update-dependencies/SKILL.md) | Update a lesson's software versions and fix breakage |
| [`org-triage`](skills/org-triage/SKILL.md) | Find issues and PRs that need a human |
| [`past-events`](skills/past-events/SKILL.md) | List where a lesson was taught in its README |
| [`write-repo-agents-md`](skills/write-repo-agents-md/SKILL.md) | Add an `AGENTS.md` to a lesson repo |
| [`migrate-platform`](skills/migrate-platform/SKILL.md) | Move a lesson to another platform (e.g. to Jupyter Book 2) |

The helper scripts in [`scripts/`](scripts/) (`inventory.py`, `audit.py`,
`workspace.py`) need Python ≥ 3.11 and only the standard library.

## Working on this repository itself

- Keep facts verifiable. When a doc states the current state of the org (which
  repos use what, versions, settings), mark it *(as of YYYY-MM-DD)* and get it
  from `gh`/the GitHub API, not from memory.
- Prefer short, scannable Markdown: tables for inventories, numbered steps for
  procedures. Link to upstream docs instead of copying them.
- Run `prek -a` (or `pre-commit run -a`) before committing.
- The same contribution policy applies here: work on a branch, add the
  `Assisted-by:` trailer, and open a PR.
- Docs are CC BY 4.0 ([`LICENSE`](LICENSE)) and code is BSD-3-Clause
  ([`LICENSE-CODE`](LICENSE-CODE)).
