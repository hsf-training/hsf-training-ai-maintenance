# Lesson platforms

HSF Training lessons are built with several different stacks. Identify a repo's
platform before changing it, because the build, the deploy, and which files are
content versus boilerplate all depend on it.

| Platform | How to recognize it | Doc |
|---|---|---|
| Jekyll + Carpentries | `_config.yml` with `carpentry: "hsf"`, `_episodes/`, `Gemfile` | [jekyll-carpentries.md](jekyll-carpentries.md) |
| Jupyter Book 1 | `_config.yml` + `_toc.yml` in a book directory, `jupyter-book` < 2 | [jupyter-book-1.md](jupyter-book-1.md) |
| MyST / Jupyter Book 2 | `myst.yml` | [myst-jupyter-book-2.md](myst-jupyter-book-2.md) |
| Hugo | `hugo.toml`, `go.mod`, `content/` | [hugo.md](hugo.md) |
| JupyterLite | `site/` built with `jupyter lite build` | [jupyterlite.md](jupyterlite.md) |
| Anything else | LaTeX slides, Carpentries Workbench (sandpaper), Astro, Sphinx via starterkit-ci, plain code/notebook repos | [other.md](other.md) |

`myst.yml` takes precedence. A repo can keep Jekyll-era files such as
`_episodes/` after moving to MyST (e.g. `hsf-training-databases-basics`).

## Things to check for every platform

- **Default branch and Pages source.** Run
  `gh api repos/hsf-training/<repo>/pages --jq '{build_type, source}'`.
  `build_type: legacy` means Pages builds directly from a branch.
  `build_type: workflow` means a GitHub Actions workflow uploads the site.
- **What CI runs on PRs**, so you can run the same thing locally before
  proposing a change.
- **Version pins.** An unpinned build tool that has had a major release since
  the lesson last built is the most common cause of a broken site.
