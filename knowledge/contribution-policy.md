# Policy for agent-assisted changes

These rules apply whenever an agent changes anything in the `hsf-training`
organization. The **operator**, the human running the agent with their own
GitHub credentials, is responsible for everything the agent produces.

## 1. Read-only by default

- Investigating, auditing, cloning, building and drafting are always fine.
- Any action that is visible to others needs the operator's explicit
  confirmation each time. That includes pushing, opening or editing PRs and
  issues, commenting, labeling, closing, changing repo settings, and triggering
  workflows or Pages builds. Approval for one action does not carry over to the
  next one, or to the same action on other repos.
- Never modify archived repositories.
- Never push directly to a default branch. All changes go through a PR from a
  branch, in the org repo if the operator has write access, or from a fork
  otherwise.

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
