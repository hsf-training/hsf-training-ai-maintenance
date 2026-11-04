---
name: org-triage
description: Survey open issues and pull requests across the hsf-training organization - unanswered first-time contributors, PRs waiting for review, bot PRs piling up, stale issues, failing scheduled CI - and draft responses or next steps for the operator. Read-only unless the operator approves each post. Use for "what needs attention in the org?" or regular triage sessions.
---

# Triage the organization

The stale and welcome bots only ping. This skill finds what actually needs a
human, and drafts the next step.

## Gather

```bash
# Open PRs, oldest first
gh search prs --owner hsf-training --state open --archived=false --sort created --order asc --limit 1000 \
  --json repository,number,title,author,createdAt,updatedAt,labels,isDraft

# Open issues, recently active first
gh search issues --owner hsf-training --state open --archived=false --sort updated --limit 1000 \
  --json repository,number,title,author,createdAt,updatedAt,labels,commentsCount

# Threads without any comments. The welcome bot's comment counts as one, so also
# look for threads in the lists above whose only comments come from bots.
gh search prs --owner hsf-training --state open --archived=false --comments 0 --json repository,number,title,author,createdAt
gh search issues --owner hsf-training --state open --archived=false --comments 0 --json repository,number,title,author,createdAt
```

For CI health, run `python3 scripts/audit.py` and look at
`ci-failing`, `workflow-disabled` and `bot-prs-pending`.

## Classify

- **Needs a reply:** human-authored issues or PRs with no response from a
  maintainer, especially from first-time contributors. Highest priority.
- **Needs review:** human PRs with green checks waiting for review. Find
  the lesson's active maintainers (`git log`, recent merged PRs) to suggest
  reviewers.
- **Bot PRs:** green Dependabot/pre-commit.ci PRs can be recommended for
  merge in a batch. Red ones need a look (`update-dependencies`).
- **Stale:** issues marked stale that are obsolete (e.g. about removed
  content, already fixed, or about archived tooling). Suggest closing them
  with a short explanation.
- **Broken:** failing default-branch CI or Pages builds. Hand off to
  `build-and-preview`.

## Report and act

- Give the operator a short table per class with links. Lead with "needs a
  reply".
- Draft replies for the operator to review. Keep them friendly and specific,
  and thank contributors. Mention specific maintainers or
  `@hsf-training/training-conveners` only when that helps move things along.
- Post, label, close or merge **only with explicit approval for each
  action**, and with the AI disclosure line on anything written by the agent.
