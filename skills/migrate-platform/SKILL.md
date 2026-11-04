---
name: migrate-platform
description: Plan and carry out moving an hsf-training lesson from one build platform to another - mainly Jekyll/Carpentries or Jupyter Book 1 to MyST/Jupyter Book 2 - preserving content, URLs where possible, and the learner experience. Use when maintainers decide to migrate a lesson, or to estimate what a migration would involve. Each migration is a per-repo project, not a bulk change.
---

# Migrate a lesson to another platform

Migrations are big, visible changes. Only start one when the lesson's
maintainers want it. Before writing any code, give them a short plan to
agree on.

## 1. Assess

- Clone (`workspace-setup`) and build the current site (`build-and-preview`).
  Keep this build as the reference.
- Inventory the content:
  - pages and their order,
  - custom markup (Carpentries blockquote classes, Liquid tags, Sphinx-only
    directives),
  - includes, figures and data,
  - executable code,
  - any custom CSS/JS.
- Note the URLs of every page (sitemap or `_site/`/`_build/html/` listing).
  Links to the old URLs exist in slides, Indico pages and other lessons.
- Check the targets: the lessons already migrated (`hsf-training-scikit-hep-webpage`,
  `hsf-training-databases-basics` for Jekyll→JB2) and `cookiecutter-jupyter-book`.

## 2. Plan

Write down and agree with the maintainers:

- the target platform and version (e.g. Jupyter Book 2, pinned `<3`),
- the content mapping, e.g. Carpentries `{: .challenge}` blockquotes → MyST
  `exercise`/`admonition` directives with dropdown solutions, and episode
  front matter (questions, objectives, keypoints) → admonitions,
- the URL strategy. JB2 strips numeric prefixes from slugs. Decide whether
  to keep the old URLs working (redirect stubs) or accept breakage and fix
  known inbound links,
- what happens to legacy files (theme, Gemfile, Makefile, `_config.yml`,
  `_toc.yml`),
- the deploy change (branch build → `deploy.yml` workflow with
  `actions/deploy-pages` and `BASE_URL`) and the Pages settings switch. The
  latter is an admin action, so confirm it with the operator.

## 3. Migrate

- Work on a branch. Convert mechanically where possible (a small script for
  repetitive markup is fine, but don't commit it unless useful), then review
  every page by hand.
- For JB1 → JB2, Jupyter Book 2 can convert legacy configs (`_config.yml` +
  `_toc.yml` → `myst.yml`). Check the current docs at <https://jupyterbook.org/>
  for the exact command, and then review the result.
- Follow the target platform doc in `knowledge/platforms/`, and add a
  `deploy.yml` that builds on PRs and deploys on push.
- Build with `--strict` and execution enabled. Compare every page with the
  reference build: content, exercises/solutions, figures, code output, links.

## 4. Propose

- Open a **draft PR** with:
  - a page-by-page checklist of what was compared,
  - known differences,
  - the URL strategy,
  - the admin steps needed at merge time (switch the Pages source to "GitHub
    Actions", possibly change the default branch).
- After merging: update `knowledge/repos.toml` (run `repo-inventory`), the
  Training Center entry if the URL changed, and the platform docs in this
  repo.
