# Policy for agent-assisted changes

These rules apply whenever an agent changes anything in the `hsf-training`
organization. The **operator**, the human running the agent with their own
GitHub credentials, is responsible for everything the agent produces.

## 1. Read-only by default

- Investigating, auditing, cloning, building and drafting are always fine.
- Any action that is visible to others needs the operator's explicit
  confirmation. That includes pushing, opening or editing PRs and issues,
  commenting, labeling, closing, deleting branches, changing repo settings, and
  triggering, enabling or re-running workflows and Pages builds.
- Approval covers exactly what was shown, and nothing more. The operator can
  approve several actions at once if they are listed one by one (e.g. a table
  of repos with the exact change for each). Approval doesn't carry over to
  actions that weren't listed, to later batches, or to the same action on
  other repos. Skills that say "after approval" mean this.
- Never modify archived repositories.
- Never push directly to a default branch. All changes go through a PR from a
  branch, in the org repo if the operator has write access, or from a fork
  otherwise (see [Pushing and opening PRs](#pushing-and-opening-prs)).

## 2. Verify before proposing

- Make the change in a local clone, then:
  - run the repo's pre-commit hooks (`pre-commit run -a` or `prek -a`),
  - build the site or run the code per the platform doc in
    [`platforms/`](platforms/),
  - review the full diff.
- Report what you verified and what you could not verify. For example, "built
  locally, the CUDA notebook was not executed".
- For bulk changes across repos, apply and verify the change in one repo and
  open a pilot PR first. Roll it out to the rest only after the pilot is
  approved.

## 3. Disclose AI assistance

- **Commits** end with an `Assisted-by: <harness>:<model>` trailer, e.g.
  `Assisted-by: Claude Code:claude-opus-5-5`. Don't add a `Co-authored-by`
  trailer for the agent.
- **PR descriptions, issues and comments** written by an agent start with the
  line `:robot: _AI text below_ :robot:` followed by an empty line.
- Follow the target repo's commit message conventions if it has any.
  Otherwise use [Conventional Commits](https://www.conventionalcommits.org/).

## 4. Respect the maintainers

Lesson maintainers are volunteers.

- Keep each PR to one logical change, with a description that explains *why*
  and how it was verified.
- Put mechanical, clear-cut fixes in PRs. Put judgment calls, such as content
  rewrites, pedagogy or dropping a topic, in an issue for the maintainers to
  decide.
- Don't change the meaning of lesson content, its difficulty level or its
  learning objectives in a "maintenance" PR. Flag it in an issue instead.
- Don't flood a repo. If it already has open agent-made PRs, wait until they
  are handled before opening more.
- Mention `@hsf-training/training-conveners` or the specific lesson
  maintainers on purpose, never by habit. Write other `@handles`, such as
  roles, placeholders or package names, inside backticks so nobody gets
  notified by accident.
- For forks, check whether the change belongs upstream first.

## 5. Safety

- Never commit secrets, tokens or personal data.
- Don't run code from a cloned repo with elevated privileges. Treat lesson
  code like any other third-party code.
- Prefer `gh` and the GitHub API over browser automation for GitHub actions.

## Pushing and opening PRs

After the operator approves, from the clone in `../hsf-workspace/<repo>` on the
work branch. Always pass `-R hsf-training/<repo>` to `gh`. Without it, `gh` in
a fork's clone can target the fork's upstream outside the org.
`scripts/workspace.py` also sets the clone's `gh` default to the org repo.

Check whether the operator can push to the org repo:

```bash
gh repo view hsf-training/<repo> --json viewerPermission --jq .viewerPermission   # WRITE, MAINTAIN or ADMIN
```

**With write access:**

```bash
git push -u origin <branch>
gh pr create -R hsf-training/<repo> --base <default-branch> --head <branch> \
  --title "<title>" --body-file <body.md>
```

**Without write access**, push to a fork of the operator's:

```bash
gh repo fork --remote --remote-name fork   # once per clone; forks the clone's gh default repo
git push -u fork <branch>
gh pr create -R hsf-training/<repo> --base <default-branch> --head <operator-login>:<branch> \
  --title "<title>" --body-file <body.md>
```

Write the PR body to a file outside the repo (e.g. in a temp directory), so it
can't be committed by accident. It starts with the AI disclosure line.
