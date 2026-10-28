---
name: content-review
description: Review the content of an hsf-training lesson (or one episode) for outdated software versions and APIs, deprecated practices, broken or moved links, technical inaccuracies and examples that could be better - verifying every finding by running code, checking releases and following links - then turn clear-cut fixes into a PR and judgment calls into an issue. Use when asked to review, update or modernize lesson content.
---

# Review lesson content

This replaces the earlier Gemini-based analysis tool. Its review categories
carry over. The difference is that **every finding must be verified** before
it is reported.

## Ground rules

- **Preserve the lesson.** Don't restructure it, change its learning
  objectives, or change its difficulty level. Suggest incremental improvements
  with a clear benefit for learners.
- **Respect the timetable.** Check whether the lesson is about to be taught
  (Training Center, the events list in `HSF/hsf.github.io`
  `_data/training-schools.yml`, open issues). If it is, propose only fixes for
  things that are broken.
- **Match the lesson's style:** markup, voice, and level of detail.
- Physics content and pedagogy are the maintainers' call. Raise questions,
  don't rewrite.

## Steps

1. Clone (`workspace-setup`) and build the lesson (`build-and-preview`).
   Note every warning, and every cell or code block that fails.

2. Read the lesson (or the requested episodes) in order, as a learner would.
   Look for:
   1. **Software updates**: outdated versions in setup instructions,
      environment files and text. Deprecated or removed APIs. Tools that have
      been superseded.
   2. **Best practices**: practices the community has moved away from (e.g.
      Python 2 idioms, `pip install` without environments, `setup.py`-only
      packaging, deprecated CI actions).
   3. **Recent developments**: newer tools or approaches in HEP or scientific
      computing that the lesson should at least mention.
   4. **Resource updates**: broken or moved links, outdated documentation
      references, dead datasets.
   5. **Technical accuracy**: statements that are wrong or no longer true.
   6. **Example improvements**: clearer or more current examples and
      exercises.

3. **Verify each finding** before keeping it:
   - Versions and APIs: check the package's changelog or releases
     (PyPI/conda-forge, `gh api repos/<owner>/<repo>/releases/latest`), and
     run the updated code in the lesson's environment with the new version.
   - Links: fetch them, and find the new location of moved pages.
   - Claims: cite a source (official docs, release notes, paper).
   - Drop anything you can't verify, or label it explicitly as unverified.

4. Check that each proposed change keeps the difficulty level. Does it
   introduce new concepts without explanation? Does it change prerequisites?
   If so, it's a judgment call for the maintainers.

5. Sort the findings:
   - **PR (clear-cut):** broken code fixed with a verified change, version
     bumps that build cleanly, dead links with a verified replacement, typos.
     One PR per theme, e.g. "update links" or "fix code for awkward 2.x".
     Verify with a full build.
   - **Issue (judgment calls):** one issue per repo with a checklist grouped
     by category. Each item gives the location (file and section),
     what and why, the suggested change, and the evidence (links, versions,
     error output). Mark priority (high: broken or wrong, medium: outdated,
     low: nice to have).

6. Show the operator the PR diff and the issue text. Push and post only after
   approval ([Pushing and opening PRs](../../knowledge/contribution-policy.md#pushing-and-opening-prs); issues with `gh issue create -R hsf-training/<repo>`).
   Both carry the AI disclosure from the contribution policy.
