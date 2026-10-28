---
name: past-events
description: Find the workshops, schools and training events where an hsf-training module was taught and add or update a "Past events" section in the lesson's README (and its landing page where practical). Use when asked to list where a lesson was taught, or to resolve the "past workshops in README" request (hsf-training/maintenance#12).
---

# Add past events to a lesson

## Sources

- **HSF training events:** `_data/training-schools.yml` in
  [`HSF/hsf.github.io`](https://github.com/HSF/hsf.github.io). Each entry has
  `title`, `date`, `end_date`, `source` (usually an Indico URL) and `tags`
  (`HSF` = organized or supported by HSF). It does **not** say which modules
  were taught.

  ```bash
  gh api repos/HSF/hsf.github.io/contents/_data/training-schools.yml --jq .content | base64 -d
  ```

- **Indico timetables** of those events (the `source` URL, often
  `.../timetable/`). These are the evidence for which modules were taught.
- **The lesson repo itself:** README, `index.md`/landing page, issues and PRs
  mentioning events, branches or tags named after events (e.g. `2017.08`).
- **Other sources:** event-specific repos and the Training Center entry's
  `videos` link.

## Steps

1. Clone the lesson (`workspace-setup`) and look for existing event lists to
   extend rather than duplicate.

2. Collect candidate events from `training-schools.yml` whose title or timing
   plausibly matches the module. For each one, open the Indico timetable and
   confirm that the module (or a session clearly based on it) was taught.
   Record the evidence (timetable URL and session title). Drop anything you
   can't confirm, or list it separately as "unconfirmed" for the operator.

3. Add a "Past events" section to the README, following
   `templates/README.md`: newest first, one line per event with month, year
   and a link to the event page:

   ```markdown
   ## Past events

   - 2026-08 [HSF/IRIS-HEP Machine Learning Training - Intermediate Level](https://indico.cern.ch/event/1706524/)
   ```

4. Optionally add the same list to the site's landing page, using the
   platform's markup (`index.md` for Jekyll, the landing page in the TOC for
   Jupyter Book). Build it (`build-and-preview`).

5. Show the operator the diff and the evidence. After approval, open one PR
   per lesson ([Pushing and opening PRs](../../knowledge/contribution-policy.md#pushing-and-opening-prs)) with the evidence list in the PR body, so maintainers
   can check it and add events the sources missed.
