---
name: repo-audit
description: Audit one, several or all hsf-training repositories against knowledge/standards.md (licenses, shared tooling, legacy files, CI health, settings, stale branches, Training Center listing) and write a prioritized report with suggested fixes. Read-only. Use to answer "what needs maintenance?", before planning a campaign, or to check a single repo's health.
---

# Audit repositories

The audit is **read-only**. It reports, and it never changes anything.

## Steps

1. Make sure the inventory is current. Run the `repo-inventory` skill if
   repos may have been added or archived since `knowledge/repos.toml` was
   last updated.

2. Gather the mechanical findings (takes about 30 s for the whole org):

   ```bash
   python3 scripts/audit.py                                  # all active repos
   python3 scripts/audit.py hsf-training-matplotlib          # specific repos
   python3 scripts/audit.py --kind lesson --platform jekyll-carpentries
   python3 scripts/audit.py --json audit.json --markdown audit.md
   ```

   Write output files outside this repo (or delete them afterwards). They're
   snapshots and shouldn't be committed.

   Every check id maps to a rule in
   [`knowledge/standards.md`](../../knowledge/standards.md). Read the rule
   before acting on a finding. Checks listed in a repo's `ignore_checks` in
   `repos.toml` are skipped, and the report says so.

   `stale-branches` leaves out the default branch, the Pages source, branches
   with an open PR, and Workbench branches. A branch counts as merged only if
   its current tip is what got merged. Still review the list before deleting
   anything (`repo-settings`).

3. **Verify the high-severity findings** before reporting them. Look at the
   failing run's log (`gh run view <id> --log-failed -R hsf-training/<repo>`),
   the Pages build, or the file in question. Drop false positives, and if a
   check is wrong, fix `scripts/audit.py`.

4. If asked for a deeper audit of specific repos, also do content-level checks
   that the script can't do. Clone them first with the `workspace-setup` skill.
   - Build the site locally per the platform doc (`build-and-preview` skill).
   - `grep -rn '^~~~' --include='*.md'` for old-style fences.
   - Check what the README says about local previews against what actually
     works.
   - Skim for obviously outdated setup instructions (Python 2, CentOS 7,
     unmaintained packages). Leave the thorough review to the
     `content-review` skill.

5. Write the report for the operator:
   - Lead with what's **broken** (failing builds and deploys, unpinned build
     tools, workflows disabled for inactivity) before hygiene items.
   - Group the remaining findings into **campaigns**: the same fix across many
     repos, e.g. "28 repos still mention individuals in bot configs →
     `sync-shared-files`". Name the skill that handles each.
   - Mention checks skipped via `ignore_checks` (the report lists them), and
     don't present them as problems.

6. Only if the operator asks, post the report as a tracking issue in
   `hsf-training/hsf-training-ai-maintenance`. Start the body with the AI
   disclosure line from the contribution policy, and use one checkbox per
   campaign or per repo so progress can be tracked.
