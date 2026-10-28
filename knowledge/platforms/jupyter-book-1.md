# Jupyter Book 1

Lessons built with [Jupyter Book 1](https://jupyterbook.org/v1/) (Sphinx-based),
with Markdown/MyST pages and notebooks, deployed to GitHub Pages by a workflow.

## Repos *(as of 2026-10-28)*

| Repo | Book directory | Env | Build command in CI |
|---|---|---|---|
| `array-oriented-programming` | `array-oriented-programming/` | `environment.yml` (`jupyter-book<2`) | `jupyter-book build -W array-oriented-programming` |
| `deep-learning-intro-for-hep` | `deep-learning-intro-for-hep/` | `environment.yml` (**unpinned** `jupyter-book`) | `jupyter-book build -W deep-learning-intro-for-hep` |
| `hsf-training-unix-shell` | `hsf-training-unix-shell/` | `requirements.txt` (**unpinned**) + `bash_kernel` | run from `hsf-training-unix-shell/filesystem/Users/nelle` (see below) |
| `hsf-training-ssh-webpage` | `ssh-tutorial/` | `environment.yml` + `pip install "jupyter-book < 2.0"` in CI | `jupyter book build ssh-tutorial` |
| `cookiecutter-jupyter-book` (template) | `book/` | `requirements.txt` (`jupyter-book==1.0.4`) | CI renders the template and runs `jupyter-book build -W --keep-going` on it |

## Layout

| Path | What it is |
|---|---|
| `<book>/_toc.yml` | Table of contents. A page that isn't listed here isn't built. |
| `<book>/_config.yml` | Book config: title, execution settings, Sphinx extensions, bibtex. |
| `<book>/*.md`, `<book>/*.ipynb` | **Content.** MyST Markdown pages and notebooks. |
| `<book>/references.bib` | Bibliography, cited with `` {cite}`key` ``. |
| `<book>/img/`, `data/`, `fig/` | **Content.** Assets. |
| `environment.yml` / `requirements.txt` | Build and runtime deps. Notebooks run with exactly these. |
| `.github/workflows/deploy.yml` | Build + `actions/upload-pages-artifact` + `actions/deploy-pages`. |

Exercises and solutions use MyST admonitions or directives, such as
`` ```{admonition} `` blocks and dropdowns. Follow the conventions already used
in the book.

## Build locally

```bash
# conda/mamba/micromamba (repos with environment.yml)
micromamba create -f environment.yml -n <repo> && micromamba activate <repo>
# or pip (repos with requirements.txt)
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

jupyter-book build -W <book-dir>   # -W turns warnings into errors, as in CI
open <book-dir>/_build/html/index.html
jupyter-book clean <book-dir>      # wipe the build cache, e.g. to force re-execution
```

`hsf-training-unix-shell` executes its notebooks with a bash kernel inside a
fake filesystem, so it must be built from that directory:

```bash
pip install -r requirements.txt && python -m bash_kernel.install
cd hsf-training-unix-shell/filesystem/Users/nelle
jupyter-book build ../../../../hsf-training-unix-shell
```

## Deploy

`deploy.yml` runs on pushes to the default branch, and in some repos also on PRs
(build only) and on a schedule. It uploads `<book>/_build/html` as a Pages
artifact (`build_type: workflow`).

## Pitfalls

- **An unpinned `jupyter-book` now installs Jupyter Book 2,** which does not
  build a Jupyter Book 1 project (`_config.yml`/`_toc.yml`) as-is. Pin
  `jupyter-book<2` unless you're migrating the lesson to JB2 (see
  [myst-jupyter-book-2.md](myst-jupyter-book-2.md)).
- The CLI is `jupyter-book` in JB1. `jupyter book` (with a space) also
  works in recent JB1 versions, but don't mix the two up with JB2 docs.
- Scheduled deploys (`deep-learning-intro-for-hep` builds daily) stop after
  60 days without repo activity. Check `gh run list` to see whether the
  published site is actually current.
- Notebook execution can be slow or need hardware the CI runner doesn't have
  (e.g. GPU notebooks). Check `_config.yml` `execute:` settings
  (`execute_notebooks: off|auto|force|cache`, `exclude_patterns`) before
  assuming a notebook runs in CI.
