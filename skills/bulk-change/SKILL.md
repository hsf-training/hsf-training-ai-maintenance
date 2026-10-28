---
name: bulk-change
description: Run a maintenance campaign that applies the same kind of change to many hsf-training repositories - pick targets, open a tracking issue, verify locally, pilot one PR, then roll out with consistent PRs and track them. Use whenever a change should go to more than one or two repos (e.g. syncing shared files, removing legacy files, license fixes). Replaces the old multi-gitter workflow.
---

# Run a campaign across repos

A campaign is one logical change applied to many repos. The other skills
(`sync-shared-files`, `legacy-cleanup`, `update-dependencies`, ...) define
*what* to change. This skill defines *how* to roll it out safely.

## 1. Define the campaign

- **What** changes, and **why**. Link the rule in `knowledge/standards.md`, or
  the issue that motivates it.
- **Which repos.** Start from `python3 scripts/audit.py --json ...` findings
  or from `knowledge/repos.toml` (`kind`, `platform`). Exclude archived repos,
  forks (unless the change is fork-safe), and repos that record a deliberate
  deviation (`ignore_checks` and `notes`).
- A **branch name** (`<type>/<description>`), a **PR title** (Conventional
  Commits style) and a **PR body template**, all shared by every repo. The body
  explains the why, says how it was verified, and links the tracking issue.

Show this to the operator and get agreement before going further.

## 2. Open a tracking issue (with confirmation)

Open it in `hsf-training/hsf-training-ai-maintenance`. Include:

- the AI disclosure line,
- what and why,
- a checklist with one item per target repo: `- [ ] hsf-training/<repo>`.

The PR links get added to that checklist later. Anyone, with any agent, can
pick the campaign up from this issue.

## 3. Pilot

1. `python3 scripts/workspace.py <one-repo> --branch <branch>`. Pick a
   representative repo, ideally one with an active maintainer.
2. Apply the change, tailoring it to the repo (see the skill that defines the
   change).
3. Verify:
   - `pre-commit run -a` (or `prek -a`),
   - build the site (`build-and-preview` skill),
   - review `git diff`.
4. Show the diff and verification results to the operator. After approval,
   commit with the `Assisted-by:` trailer, then push and open the PR as
   described in [Pushing and opening PRs](../../knowledge/contribution-policy.md#pushing-and-opening-prs) (it covers both operators with write access and
   operators who need a fork).

5. Add the PR link to the tracking issue. **Wait for the pilot PR to be
   reviewed or merged** before rolling out, and fold any feedback into the
   change.

## 4. Roll out

- Prepare all remaining repos:
  `python3 scripts/workspace.py <repos...> --branch <branch>`.
- For each repo, apply, tailor, verify and diff as in the pilot. Mechanical
  changes still need a per-repo look, because repos differ.
- Present the diffs to the operator, in batches is fine. Push and open PRs
  only after approval. Approval for one batch doesn't cover the next.
- Skip any repo that doesn't build *before* the change, and note why in the
  tracking issue.
- Don't open a PR in a repo that already has open agent-made PRs waiting for
  review (contribution policy).

## 5. Track

- Update the tracking issue checklist with each PR link
  (`gh issue edit <n> --body-file ...`).
- Later: list the campaign's open PRs with
  `gh search prs --owner hsf-training --state open --head <branch>`. Answer
  review comments, rebase when needed, and tick off merged PRs.
- Close the tracking issue when every item is merged, declined, or explicitly
  skipped with a reason.
