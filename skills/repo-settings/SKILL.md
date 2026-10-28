---
name: repo-settings
description: Inspect and (with confirmation and admin rights) change GitHub repository settings of hsf-training repos - delete-branch-on-merge, description, homepage, topics - and clean up stale branches. Use for audit findings delete-branch-on-merge-off, description-missing, homepage-missing, stale-branches, or when asked about repo settings. Does not manage branch protection.
---

# Repository settings and branches

Settings changes take effect immediately and aren't reviewed through a PR, so
**every change needs the operator's explicit confirmation**. Show the exact
command and the before and after values first. Changing settings requires
admin rights on the repo. If the operator lacks them, prepare the list for an
org owner instead.

**Branch protection is out of scope.** It was decided (2026-10-28) not to
require it, because there are too few maintainers. Don't add or remove
protections.

## Inspect

```bash
gh repo view hsf-training/<repo> --json description,homepageUrl,repositoryTopics,deleteBranchOnMerge,defaultBranchRef
```

## Change (after confirmation)

```bash
# Automatically delete head branches after merge
gh repo edit hsf-training/<repo> --delete-branch-on-merge

# Description and homepage (homepage = the Pages site from knowledge/repos.toml)
gh repo edit hsf-training/<repo> --description "<one line>" --homepage "<site url>"

# Topics (only if the operator wants them, there's no org-wide convention yet)
gh repo edit hsf-training/<repo> --add-topic <topic>
```

For many repos, list all intended changes in one table, get approval for
the whole table, and then apply them. Report anything that failed.

For descriptions, reuse the module's description from
`training-center/data/data.yaml` if there is one, stripped of HTML. Otherwise
summarize the README in one line.

## Stale branches

`scripts/audit.py` reports branches that are merged, or that have no commits
in over a year (`stale-branches`).

1. List them for the operator with their last commit date, last author, and
   whether they have an open PR:

   ```bash
   gh pr list -R hsf-training/<repo> --head <branch> --state all
   ```

2. Keep anything that looks deliberate: workshop or event snapshots (e.g.
   `2017.08`), old default branches others may link to (e.g. `master` in a
   repo that moved to `gh-pages`), backups, and branches with open PRs.
3. Delete only the branches the operator approves:

   ```bash
   gh api -X DELETE repos/hsf-training/<repo>/git/refs/heads/<branch>
   ```

4. Never delete the default branch or the Pages source branch.

This resolves old issue
[hsf-training/maintenance#11](https://github.com/hsf-training/maintenance/issues/11),
together with turning on delete-branch-on-merge.
