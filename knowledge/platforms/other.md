# Other platforms

Repos that don't fit the main lesson stacks. *(as of 2026-10-28)*

## Sphinx via LHCb starterkit-ci: `analysis-essentials`

- Sphinx site (`conf.py`, `index.md`, topic folders like `python/`, `shell/`,
  `git/`, `snakemake/`, `advanced-python/`), shared with the LHCb Starterkit.
- Env: `environment.yml`. CI installs
  `git+https://github.com/lhcb/starterkit-ci.git@cburr-gh-actions` and runs
  `starterkit_ci build`. It deploys with `starterkit_ci deploy` to the
  `gh-pages` branch on pushes to `master` (`build_type: legacy`).
- Local build: create the conda env, install starterkit-ci the same way, and
  run `starterkit_ci build`. For a fast iteration loop, temporarily remove
  heavy sections, as the comments in `build.yml` suggest. Don't commit that.
- Pitfall: CI depends on a branch of an external repo, so check that it still
  exists before debugging the lesson itself.

## LaTeX slides + exercises: `cpluspluscourse`

- C++ course: Beamer slides in `talk/`, C++ exercises in `exercises/`,
  Docker images in `docker/`. Default branch `master`, no Pages site.
- CI: `build-slides.yml` / `publish-slides.yml` use `xu-cheng/latex-action`,
  and `build-exercises.yml` compiles the exercises. Read the workflows for the
  exact commands and compilers.
- Licensed Apache-2.0, and has its own maintainer teams (`cplusplusteam`,
  `cpluscplusadmin`).

## Carpentries Workbench (sandpaper): `git-novice`

- Fork of `mambelli/git-novice`, which is a fork of `swcarpentry/git-novice`.
  Both are active, so check both before syncing and ask the operator which one
  to follow.
- It uses the Carpentries Workbench (`config.yaml`, `episodes/`, `learners/`,
  `instructors/`, `profiles/`), built with the R package `sandpaper`.
- The workflows (`sandpaper-main.yaml`, `pr-*.yaml`, `update-*.yaml`) are
  owned by upstream. Don't modify them. Sync from upstream instead.
- *(as of 2026-10-28)* GitHub Actions has never run on this fork (no
  registered workflows, no runs), so the published site is not rebuilt
  automatically. Enabling Actions is an admin decision (audit check
  `actions-not-running`).
- The Workbench uses the branches `gh-pages`, `md-outputs` and
  `md-outputs-PR-*`. They are not stale branches.
- Local build: in R, `sandpaper::build_lesson()` or `sandpaper::serve()`.

## Astro site: `training-center`

- The Training Center catalog website. `npm ci && npm run dev` (dev server at
  `http://localhost:4321/training-center/`), and `npm run build`. Deployed by
  `build-and-deploy.yml`, with lychee link checking, to
  <https://hsf-training.org/training-center/> (`base: "/training-center"` in
  `astro.config.mjs`).
- Content lives in `data/data.yaml` (all modules) and `data/curricula.yaml`
  (curated curriculum). Both are validated at build time.

## Plain code / notebook repos

`hsf-training-cms-analysis` (C++/Python analysis used by the CMS analysis
lesson), `hsf_matplotlib_notebooks` (notebooks for the matplotlib lesson),
`python-lesson`, `participation-analysis`, `learner-certificates` (fork of
`carpentries/learner-certificates`), `PyHEP-resources`.

- There's no site to build. Verify changes by running what the README or CI
  runs, e.g. `test-analysis.yml` in `hsf-training-cms-analysis`.
- Companion repos are referenced from lesson text. Paths, file names and
  outputs used in the lesson must not change without updating the lesson.
