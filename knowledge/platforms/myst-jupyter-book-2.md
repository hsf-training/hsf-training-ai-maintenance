# MyST / Jupyter Book 2

Lessons built with [Jupyter Book 2](https://jupyterbook.org/), a thin wrapper
around the [MyST-MD](https://mystmd.org/) engine. It is **not** Sphinx.
Deployed to GitHub Pages by a workflow. This is the direction newer lessons
are moving in.

## Repos *(as of 2026-10-28)*

| Repo | `myst.yml` location | Content | Env | CI build command |
|---|---|---|---|---|
| `hsf-training-scikit-hep-webpage` | repo root | `skhep-tutorial/*.ipynb`, `README.md`, `setup.md` | `environment.yml` + `pip install --pre "jupyter-book==2.*"` | `jupyter book build --execute --strict --html --ci` |
| `hsf-training-scikit-hep-webpage-es` | repo root | `skhep-tutorial/` (Spanish translation of the above) | same | same |
| `hsf-training-databases-basics` | repo root | `_episodes/*.md` (kept from its Jekyll days) | `requirements.txt` (`jupyter-book>2.1`) | `jupyter-book build --html --ci` |
| `hsf-training-llms-for-hep` | `book/` | `book/` | `requirements.txt` (`jupyter-book>=2.1,<3`) | `jupyter book build --execute --html --strict` (from `book/`) |

`hsf-training-llms-for-hep` has an `AGENTS.md` with detailed, accurate JB2
notes. Read it when working on any JB2 lesson.

## Layout

| Path | What it is |
|---|---|
| `myst.yml` | The single config file. `project.toc` is the table of contents (a page not listed there is not built, and the first entry is the landing page). `project.github`, `project.bibliography`, `site.template` live here too. |
| Pages listed in `project.toc` | **Content.** MyST Markdown and notebooks. |
| `references.bib` | Bibliography. |
| `environment.yml` / `requirements.txt` | Build and runtime deps. |
| `.github/workflows/deploy.yml` | Build with `BASE_URL=/<repo>`, upload `_build/html`, deploy. |

Episodes follow the HSF/Carpentries pattern using MyST directives. That means
an overview admonition with questions and objectives, exercise admonitions with
dropdown solutions, and a key points admonition at the end. Nested directives
need more colons or backticks on the outer fence than on the inner one.

## Build locally

JB2 needs **Node.js ≥ 18** on the `PATH` in addition to the Python package.

```bash
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
# (or create the conda env from environment.yml and pip install "jupyter-book==2.*")

cd <dir containing myst.yml>
jupyter book start --execute                    # live dev server (http://localhost:3000)
jupyter book build --execute --html --strict    # static site in _build/html/
jupyter book clean --all                        # wipe caches, including the execution cache
```

Run with the environment *activated*. MyST launches `jupyter server` from
whichever `jupyter` is first on `PATH`, and a kernel from a different
environment fails with import errors.

## Deploy

`deploy.yml` builds on PRs and on pushes to the default branch, but only
deploys on push (`build_type: workflow`). `BASE_URL` must be set to
`/<repo-name>` for GitHub Pages sub-path hosting, or links and assets break on
the deployed site even though the local preview looks fine.

## Pitfalls

- Sphinx-only roles and directives from JB1 aren't available. Check
  <https://mystmd.org/guide/directives> before using anything unusual.
- Notebooks only execute with `--execute`. Outputs are cached in
  `_build/execute/`.
- Without `--strict`, errors are only warnings. Read the warning summary at
  the end of the build output.
- Static output is one folder per page, and numeric prefixes are stripped
  from slugs (`01-intro.md` → `/intro/`). Links to the old Jekyll URLs of a
  migrated lesson will break.
- `jupyter book` (space) is the documented CLI. `jupyter-book` also works.
