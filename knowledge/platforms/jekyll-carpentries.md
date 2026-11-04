# Jekyll + Carpentries lessons

Lessons originally built from the Carpentries lesson template, rendered by Jekyll
on GitHub Pages. This is the oldest and most common lesson format in the org.

## Repos *(as of 2026-10-28)*

- **Using the remote theme** (`remote_theme: hsf-training/hsf-training-theme`):
  `hsf-training-matplotlib`, `-cicd`, `-cmake-webpage`, `-docker`,
  `-generators-webpage`, `-ml-gpu-webpage`, `-reana-webpage`,
  `-singularity-webpage`.
- **Still vendoring the full Carpentries theme** (`_layouts/`, `_includes/`,
  `assets/`, `bin/`, no `remote_theme`): `hsf-training-advanced-git-webpage`,
  `-advanced-cpp-bits-webpage`, `-cms-analysis-webpage`, `-ml-webpage`.

## Layout

| Path | What it is |
|---|---|
| `_episodes/NN-slug.md` | **Content.** One file per episode, ordered by number prefix. |
| `_extras/` | **Content.** Extra pages (e.g. `about.md`, `guide.md`, `figures.md`). |
| `index.md`, `setup.md`, `reference.md` | **Content.** Landing page, setup instructions, glossary. |
| `fig/`, `code/`, `data/`, `files/` | **Content.** Assets referenced by episodes. |
| `_config.yml` | Site config. `title`, `carpentry: "hsf"`, `life_cycle`, `remote_theme`, and Carpentries URL variables. |
| `Gemfile` (+ `Gemfile.lock`) | Ruby deps: `github-pages` and the theme gem from git. |
| `_includes/`, `_layouts/`, `assets/`, `bin/` | Theme files. Repos on the remote theme should have none of these, or only small overrides in `_includes/`. |
| `aio.md`, `404.md` | Boilerplate pages ("all in one", not found). |
| `Makefile` | The upstream Carpentries Makefile. Many targets depend on `bin/` scripts that were removed. |
| `_episodes_rmd/` | R Markdown episodes from the template, usually empty. |
| `LICENSE.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `AUTHORS`, `CITATION` | Template boilerplate rendered as site pages (they have YAML front matter). |

## Episode format

Each episode starts with YAML front matter:

```yaml
---
title: "Introduction"
teaching: 60        # minutes
exercises: 30       # minutes
questions:
- "..."
objectives:
- "..."
keypoints:
- "..."
---
```

The body is kramdown Markdown. Callouts, exercises and solutions are blockquotes
followed by a class attribute line:

```markdown
> ## Exercise title
> Do the thing.
>
> > ## Solution
> > The answer.
> {: .solution}
{: .challenge}
```

Common classes are `.challenge`, `.solution`, `.callout`, `.prereq`,
`.discussion`, `.keypoints`, `.checklist`, `.testimonial`, and for code blocks
`.source`, `.output`, `.error`, `.language-python`, `.language-bash`.
Fenced code uses ```` ```lang ```` (older lessons use `~~~` with a
`{: .language-xxx}` line after the fence). Keep the existing style inside a
file. The question/objective/keypoint lists appear on the landing page and the
summary, so keep them in sync with the episode body.

## Build locally

Requires Ruby and Bundler.

```bash
bundle config set --local path .vendor/bundle
bundle install
bundle exec jekyll serve      # http://127.0.0.1:4000/<repo>/
bundle exec jekyll build      # one-off build into _site/
```

`make serve` comes from the Carpentries Makefile and may be broken. Don't rely
on it.

The `github-pages` gem pins a specific Jekyll version and plugin set. If
`bundle install` fails on a recent Ruby, try a Ruby version close to the one
listed at <https://pages.github.com/versions/> (e.g. via `mise` or `rbenv`)
before changing the `Gemfile`.

## Deploy

- Pages builds from a branch (`build_type: legacy`): usually the **default
  branch, `gh-pages`**, and for `hsf-training-generators-webpage` it's `master`.
  There's no deploy workflow. The build shows up as `pages-build-deployment`
  in the Actions tab.
- The remote theme is fetched at build time, so lessons only pick up
  `hsf-training-theme` changes on their next build. To force a rebuild without
  a commit: `gh api -X POST repos/hsf-training/<repo>/pages/builds` (needs
  write access, and counts as an outward-facing action).
- Some repos also have CI that tests the lesson's example code (e.g.
  `hsf-training-cmake-webpage` `ci.yml`) or checks links.

## Pitfalls

- PRs target `gh-pages`, not `main`, in most of these repos.
- Pages only allows the plugins of the `github-pages` gem. Adding a Jekyll
  plugin to the `Gemfile` works locally but is ignored, or fails, on Pages.
- `_config.yml` often has the template placeholder
  `repository: <USERNAME>/<PROJECT>`. The theme gets the repo from Pages
  metadata when deployed, so it renders fine on Pages but may produce odd links
  locally.
- `hsf-training-theme`'s navbar uses `{% link LICENSE.md %}` and
  `{% link CODE_OF_CONDUCT.md %}`. Jekyll's `link` tag fails the build if the
  target is missing, so both files must stay, with their front matter.
- Before removing vendored theme files, check `_includes/` for lesson-specific
  files. `all_figures.html` and `figure.html` must be kept if present, and
  custom includes should be kept or moved to `files/`. Rebuild and compare
  pages afterwards.
