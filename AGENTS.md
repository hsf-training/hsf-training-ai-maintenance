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
2. [`knowledge/org-overview.md`](knowledge/org-overview.md): what is in the org,
   infrastructure repos, bots, and common surprises (e.g. many lessons use
   `gh-pages` as the default branch).
3. [`knowledge/platforms/`](knowledge/platforms/README.md): before touching a
   lesson, identify its platform and read that doc to learn how to build it
   and which files are content.

[`PLAN.md`](PLAN.md) describes the roadmap and the decisions behind it.

## Setup

- `gh auth status` must succeed. The operator's account determines what you can
  do. Most write actions need org membership, and repo settings need admin.
- Clone target repos **outside** this repo, e.g. into a sibling
  `../hsf-workspace/<repo>`, and work on a new branch based on the repo's
  default branch (`gh repo view hsf-training/<repo> --json defaultBranchRef`).
- Install build tools per platform (Ruby/Bundler for Jekyll, conda or pip for
  Jupyter Book, Node.js for JB2 and Astro, Hugo + Go for Hugo). Use isolated
  environments and don't install globally without asking.
- Helper scripts in this repo use only the Python standard library. Run them
  with `python3`.

## Skills

Maintenance procedures will live in `skills/` in the
[Agent Skills](https://agentskills.io) format (`skills/<name>/SKILL.md`).
None exist yet. They are added starting in phase 2 of `PLAN.md`. Until then,
follow the knowledge docs and the contribution policy directly.

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
