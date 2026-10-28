---
name: build-and-preview
description: Build an hsf-training lesson locally the same way its CI does, to check that it renders and that a change didn't break it, and diagnose failing builds or deploys. Covers Jekyll, Jupyter Book 1 and 2, Hugo, JupyterLite and the other platforms, plus triggering a GitHub Pages rebuild. Use before proposing any change to a lesson, when an audit reports ci-failing or pages-errored, or when asked whether a lesson still builds.
---

# Build and preview a lesson

## Steps

1. Find the platform in `knowledge/repos.toml` and read its doc in
   [`knowledge/platforms/`](../../knowledge/platforms/README.md). Also read the
   repo's own `AGENTS.md`/`README.md`/`CONTRIBUTING.md`, which may be more
   specific.

2. **Mirror CI.** Read the repo's build workflow in `.github/workflows/` and use
   the same tool versions, install commands and build command. If the
   platform doc and the workflow disagree, the workflow wins, and the doc
   should be fixed.

3. Use an isolated environment per repo: a `.venv`, a conda/micromamba env
   named after the repo, or `bundle config set --local path .vendor/bundle`
   for Ruby. Don't install packages globally without asking.

4. Build with warnings as errors where CI does, e.g. `jupyter-book build -W`,
   `jupyter book build --strict`. Save the full log, and read the warning
   summary, not just the exit code.

5. Preview: open the built HTML or run the dev server. Check the pages
   affected by the change, plus the landing page and navigation. For
   Jekyll/JB1→JB2 or theme changes, compare against the live site
   (`site` in `repos.toml`).

6. Report: built with which command and versions, what was checked, and what
   could not be checked (e.g. GPU notebooks, notebooks needing credentials or
   large downloads).

## Diagnosing CI and deploy failures

- `gh run list -R hsf-training/<repo> --branch <default-branch>` and
  `gh run view <id> --log-failed -R hsf-training/<repo>`.
- Reproduce locally with the same versions. Common causes:
  - an unpinned tool's new major version (Jupyter Book 2, Sphinx, Ruby/Jekyll),
  - a package removed from conda-forge/PyPI,
  - a dataset URL that moved,
  - a deprecated GitHub Action.
- `workflow-disabled`: GitHub disabled a scheduled workflow after 60 days of
  repo inactivity. Fix the build first. Then re-enabling
  (`gh workflow enable <name> -R hsf-training/<repo>`) is an outward-facing
  action that needs confirmation.

## Triggering a Pages rebuild

For branch-built (legacy) Jekyll sites, e.g. after a change to
`hsf-training-theme`. This is outward-facing, so confirm first:

```bash
gh api -X POST repos/hsf-training/<repo>/pages/builds
```

For workflow-deployed sites, re-run the deploy workflow instead (also after
confirmation). `gh workflow run <workflow> -R hsf-training/<repo>` only works
if the workflow has a `workflow_dispatch` trigger and isn't disabled.
Otherwise re-run its latest run with
`gh run rerun <run-id> -R hsf-training/<repo>`.
