---
name: update-dependencies
description: Update the software versions an hsf-training lesson depends on (environment.yml, requirements.txt, Gemfile, Docker images, setup instructions, build tools like Jupyter Book), re-run the lesson's code and notebooks, rebuild the site, and report or fix what breaks. Use for build-tool-unpinned findings, failing scheduled builds, stale bot dependency PRs, or when asked to modernize a lesson's environment.
---

# Update a lesson's dependencies

## Steps

1. Clone (`workspace-setup`) and build the lesson **as is**
   (`build-and-preview`). Record which versions actually got installed
   (`pip freeze`, `conda list`, `bundle list`). That's the baseline.

2. Find every place versions are stated:
   - environment files: `environment.yml`, `requirements*.txt`,
     `pyproject.toml`, `Gemfile`, `package.json`, `Dockerfile`s,
     `.devcontainer/`,
   - CI workflows (`python-version`, `setup-*` actions, container images),
   - setup instructions and text in the lesson (`setup.md`, episodes). They
     often hardcode versions or show `pip install` lines and expected output.

3. Choose targets:
   - **Build tools:** pin the major version that the lesson's layout needs,
     e.g. `jupyter-book<2` for a JB1 book (`build-tool-unpinned`). Moving to
     a new major version is a migration (`migrate-platform`), not an update.
   - **Lesson libraries:** move to current releases, but keep APIs the lesson
     teaches working. If a new major version changes APIs the lesson
     teaches, that's a content change. Raise it with `content-review`.
   - **Python, Ruby and Node versions:** use a currently supported version.
     For Jekyll, stay close to the GitHub Pages versions
     (<https://pages.github.com/versions/>).
   - Prefer lower bounds or compatible-release pins in environment files, and
     keep the existing pinning style.

4. Update, rebuild with execution (`--execute`/`-W`), and run any code tests
   the repo has. Fix breakage:
   - API changes in code cells: update the code *and* any text or output
     shown in the lesson.
   - Changed outputs (numbers, plots, warnings): update stored outputs where
     the lesson shows them.

5. Also handle pending bot PRs in the repo: Dependabot and pre-commit.ci PRs
   that are green can be recommended for merging. Say why if one shouldn't be
   merged.

6. Show the operator the diff. After approval, open one PR ([Pushing and opening PRs](../../knowledge/contribution-policy.md#pushing-and-opening-prs)). Its body
   includes:
   - a table of old → new versions,
   - what broke and how it was fixed,
   - how it was verified (build command, notebooks executed).

   List anything not verified, e.g. notebooks that need a GPU or large data.
