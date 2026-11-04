---
name: content-review
description: Review the content of an hsf-training lesson (or some of its episodes) for code that no longer runs, outdated software and APIs, deprecated practices, broken or moved links, wrong statements and examples that could be better. Starts from evidence (an executing build, a link check), verifies every finding, and delivers clear-cut fixes as a PR and judgment calls as one prioritized issue. Use when asked to review, check, update or modernize what a lesson teaches.
---

# Review lesson content

The goal is a short list of **verified** findings that a volunteer maintainer
can act on, not a long list of plausible ones. Every finding needs evidence
that you produced or looked at in this session.

Files in this skill:

- [`references/review-guide.md`](references/review-guide.md): categories,
  what counts as evidence, priorities, PR vs issue, and what is *not* a
  finding. Read it before step 3.
- [`scripts/check_links.py`](scripts/check_links.py): link checker for the
  lesson sources (stdlib Python).
- [`assets/issue-template.md`](assets/issue-template.md): body of the review
  issue.

## Ground rules

- **Preserve the lesson.** Don't restructure it or change its learning
  objectives or difficulty. Physics content and pedagogy are the
  maintainers' call: raise questions, don't rewrite.
- **Match the lesson's style:** markup, voice, level of detail.
- **Respect the timetable.** If the lesson is about to be taught (Training
  Center, the events list in `HSF/hsf.github.io` `_data/training-schools.yml`,
  open issues), propose only fixes for broken things.
- **Read-only until approved.** Pushing and posting follow the
  [contribution policy](../../knowledge/contribution-policy.md).

## Steps

1. **Scope.** Agree with the operator on the lesson and on the episodes to
   review (whole lesson, or the ones being taught next). Note the commit you
   review. Check what's already known, so you don't report it again:

   ```bash
   gh issue list -R hsf-training/<repo> --state open
   gh pr list -R hsf-training/<repo> --state open
   ```

2. **Collect evidence before reading.** Clone with `workspace-setup`, then:
   - Build **with code execution** (`build-and-preview`). For JB1 and JB2
     that's the normal build with execution on. For Jekyll lessons, the code
     blocks are not run by the build: run them yourself in the environment
     from `setup.md`, episode by episode. Save the log and collect every
     error and deprecation warning, with its file.
   - Check the links:

     ```bash
     python3 <this skill>/scripts/check_links.py ../hsf-workspace/<repo> \
       --json <scratch>/links.json
     ```

     It reports `broken`, `moved` and `check` (inconclusive). Add
     `--exclude REGEX` for URLs that are meant to be placeholders.
   - List the versions the lesson states: `grep -rnE '[0-9]+\.[0-9]+'` in
     the setup page and environment files, plus what actually got installed
     (`pip freeze`, `conda list`).

3. **Read the episodes in order, as a learner would,** with the evidence at
   hand. Record each candidate finding in a findings file **outside the
   repo** (e.g. `<scratch>/<repo>-review.md`), so the review survives long
   sessions:

   ```markdown
   ## <short title>
   - category: broken | outdated | practice | links | accuracy | example | new
   - location: <file>, section "<heading>"
   - status: candidate
   - evidence:
   - proposed change:
   ```

   For a long lesson, review one episode at a time. If your harness can run
   subagents, you can give each one an episode, the findings format and the
   review guide, but you verify everything they report (step 4).

4. **Verify every candidate,** using the evidence rules for its category in
   the [review guide](references/review-guide.md). Try to prove the finding
   wrong: run the "fixed" code, open the replacement link, read the release
   note. Then set `status` to `verified`, `dropped` (with the reason) or
   `unverified`. Only verified findings go further.

5. **Check difficulty** for each verified change (questions in the review
   guide). A change that adds concepts, prerequisites or teaching time is a
   judgment call.

6. **Sort and prioritize:**
   - **PR:** clear-cut and verified fixes, one PR per theme (e.g. "fix code
     for awkward 2", "update moved links"). Make the change, rebuild with
     execution, and check the rendered pages.
   - **Issue:** everything else, as one issue per repo from
     [`assets/issue-template.md`](assets/issue-template.md), grouped by
     priority. Each item has a location, a suggested change and its
     evidence.
   - If the main problem is versions, hand over to `update-dependencies`.
     If it's the platform, hand over to `migrate-platform`.

7. **Report to the operator:**
   - the PR diff(s) and the issue text,
   - counts: verified, dropped, unverified, and the unverified items with
     what would be needed to check them (GPU, credentials, large data),
   - links already known from open issues and PRs, which you left out.

   Push, open the PR and create the issue only after approval
   ([Pushing and opening PRs](../../knowledge/contribution-policy.md#pushing-and-opening-prs);
   `gh issue create -R hsf-training/<repo> --body-file <file>`).

## Gotchas

- Jekyll lessons store code as Markdown blocks with hand-written output. The
  build passes even when every code block is broken. Run them.
- Notebooks with stored outputs can hide breakage. Execute them; don't trust
  the outputs in the file.
- Many sites block scripts (`403`, `429`) or need a login. Those come back as
  `check`. Open a few by hand, and report the rest as unverified.
- `hsf-training.github.io/<lesson>/` links point to other lessons that may
  have been renamed or restructured. Check them against `knowledge/repos.toml`.
- Org-wide files (`CODE_OF_CONDUCT.md`, `.github/config.yml`,
  `CONTRIBUTING.md`) also show up in the link check. Leave them to
  `sync-shared-files` and `legacy-cleanup`, and keep the review on the lesson.
