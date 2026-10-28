# Templates

Blueprints for files shared across `hsf-training` repositories. They are
**starting points, not files to copy verbatim**. Tailor each one to the target
repo as described in
[Tailoring templates](../knowledge/standards.md#tailoring-templates), and fill
in every `<PLACEHOLDER>`.

| File | Use |
|---|---|
| `.pre-commit-config.yaml` | Baseline hooks (required). |
| `codespell.txt` | Ignore-list for codespell, one word per line. Empty in the template, but it must exist because the pre-commit config passes it with `-I`. |
| `.github/dependabot.yml` | GitHub Actions updates, plus ecosystems the repo uses. |
| `.github/stale.yml`, `.github/config.yml` | Stale and welcome bots, which mention `@hsf-training/training-conveners`. |
| `.github/workflows/check-links.yml` | Link checking with lychee (recommended for lessons). |
| `LICENSE` | CC BY 4.0, for instructional material. |
| `LICENSE-CODE` | BSD-3-Clause, for code in **new** modules. |
| `LICENSE-CODE-MIT` | MIT, copied as `LICENSE-CODE` into **existing** lessons whose Carpentries license already put code under MIT. |
| `CONTRIBUTING.md` | Contribution guide for lessons. |
| `README.md` | README skeleton for lessons. |

This file is called `TEMPLATES.md`, not `README.md`, because `README.md` is
itself a template.
