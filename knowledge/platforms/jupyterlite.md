# JupyterLite

Interactive lessons that run entirely in the browser via
[JupyterLite](https://jupyterlite.readthedocs.io/) (Pyodide kernel). Learners
need no installation.

## Repos *(as of 2026-10-28)*

- `array-oriented-puzzles`. Served at
  <https://hsf-training.github.io/array-oriented-puzzles/lab/index.html?path=tutorial.ipynb>.

## Layout

| Path | What it is |
|---|---|
| `site/files/` | **Content.** Notebooks and data shown in the JupyterLite file browser. |
| `site/requirements.txt`, `site/jupyter-lite.json` | Build requirements and JupyterLite config. |
| `.github/workflows/jupyterlite.yml` | Builds with `jupyter lite build --output-dir dist` in `site/` and deploys `site/dist` to Pages. |
| `.github/workflows/test-solutions.yml` | Runs the puzzle solutions in regular Python to check them. |

## Build locally

```bash
cd site
pip install -r requirements.txt
jupyter lite build --output-dir dist
python -m http.server -d dist       # then open http://localhost:8000/lab/
```

## Pitfalls

- Code runs in **Pyodide**, not CPython. Only packages with Pyodide builds,
  pure-Python wheels, or packages bundled in the Pyodide distribution are
  available, and their versions follow the Pyodide release, not PyPI. A
  solution that passes `test-solutions.yml` locally can still fail in the
  browser. Check in the built site.
- Browsers cache the JupyterLite site aggressively, including notebooks
  stored in browser storage. When checking a deployed change, use a private
  window.
