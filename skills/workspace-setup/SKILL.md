---
name: workspace-setup
description: Clone or update hsf-training repositories into the local workspace (../hsf-workspace) on a fresh work branch, so changes can be made, built and reviewed locally. Use before making any change to a lesson or other org repo, or when a task needs a local copy of one or more repos.
---

# Set up the local workspace

All changes to other repos are made in local clones under `../hsf-workspace/`
(next to this repo), never inside this repo.

## Steps

1. Pick the target repos. Use names from `knowledge/repos.toml`, or filter by
   kind or platform. Archived repos are refused.

2. Clone or update them, optionally creating a work branch from each repo's
   **default branch**, which is often `gh-pages` or `master`, not `main`:

   ```bash
   python3 scripts/workspace.py hsf-training-matplotlib hsf-training-docker --branch chore/sync-shared-files
   python3 scripts/workspace.py --all --platform jekyll-carpentries --branch fix/remove-makefile
   python3 scripts/workspace.py --all --kind lesson          # just update, no branch
   ```

   - Existing clones are fetched and fast-forwarded. Clones with uncommitted
     changes are **skipped** and reported. Ask the operator what to do with
     them, and never discard someone's local work.
   - If the branch already exists locally, it is checked out but not reset.
     Check `git log` to see whether it holds earlier work.

3. Branch names: `<type>/<short-description>`, with the type from Conventional
   Commits (`fix`, `chore`, `docs`, `ci`, ...). For a campaign, use the same
   branch name in every repo.

4. Before building, read the repo's platform doc
   (`knowledge/platforms/`) and any `AGENTS.md`/`CONTRIBUTING.md` in the repo
   itself.

## Notes

- Pushing uses the operator's permissions. If they can't push to the org repo,
  `gh pr create` offers to push to a fork. Accept that instead of pushing
  elsewhere.
- Use `--dir` to put the workspace somewhere else. Tell the operator where.
