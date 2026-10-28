---
name: legacy-cleanup
description: Remove legacy cruft from hsf-training repos - vendored Jekyll theme files, the Carpentries Makefile, .travis.yml, per-repo copies of org-wide files, duplicate code-of-conduct files, empty _episodes_rmd, _config.yml placeholders - and split Carpentries-derived licenses into LICENSE + LICENSE-CODE. Use for audit findings jekyll-theme-leftovers, jekyll-vendored-theme, carpentries-makefile, travis, org-file-duplicate, conduct-duplicate, empty-episodes-rmd, config-placeholder, license-carpentries.
---

# Clean up legacy files

Each item below is a separate, self-contained change. Keep **one kind of
cleanup per PR** so maintainers can review and revert them independently. For
more than one or two repos, run this inside `bulk-change`.

Always build the site before and after the change
([`build-and-preview`](../build-and-preview/SKILL.md)). If it didn't build
before, stop and report that instead.

## Org-wide duplicates and dead CI (`org-file-duplicate`, `travis`, `conduct-duplicate`)

- Delete `.github/ISSUE_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE.md`,
  `.github/FUNDING.yml` (and root-level copies) **unless** they differ
  meaningfully from the org's `.github` repo. Compare first. If they're
  deliberately different, record that in `repos.toml` notes instead.
- Delete `.travis.yml`.
- Duplicate `CONDUCT.md` + `CODE_OF_CONDUCT.md`: keep `CODE_OF_CONDUCT.md`
  (Jekyll lessons **must** keep it), delete `CONDUCT.md`, and fix any links to
  it.

## Jekyll theme leftovers (`jekyll-theme-leftovers`)

The repo already uses `remote_theme: hsf-training/hsf-training-theme` but still
carries theme files.

- Delete `_layouts/`, `assets/` (check for lesson-specific CSS or images
  first), `bin/`.
- In `_includes/`, keep lesson-specific files and `all_figures.html` /
  `figure.html` if present. Delete copies of theme includes, which you can
  identify by comparing with `hsf-training-theme/_includes/`.
- Build, and compare a few pages (landing page, an episode, setup, the
  navbar) with the live site.

## Jekyll vendored theme (`jekyll-vendored-theme`)

The repo doesn't use the remote theme at all. This is a **migration**. Handle
it as a per-repo project, not as part of a cleanup campaign:

1. Add `remote_theme: hsf-training/hsf-training-theme` to `_config.yml`.
2. Replace the `Gemfile` with the one used by the remote-theme lessons (see
   `hsf-training-matplotlib`).
3. Remove the vendored theme files as above.
4. Build locally and compare **every** page type with the live site, because
   older Carpentries layouts differ from the theme.

Open the PR as a draft, with screenshots or a list of the pages checked.

## Carpentries Makefile (`carpentries-makefile`)

- Delete the `Makefile` if it's the upstream Carpentries one (it starts with
  `## Commands for both workshop and lesson websites`).
- Make sure the README documents local preview with `bundle exec jekyll serve`
  (see the Jekyll platform doc). Update `_config.yml` `exclude:` if it lists
  `Makefile`.
- This resolves old issue
  [hsf-training/maintenance#19](https://github.com/hsf-training/maintenance/issues/19).

## Small Jekyll fixes (`empty-episodes-rmd`, `config-placeholder`)

- Delete `_episodes_rmd/` if it only contains `.gitkeep`.
- Set `repository: hsf-training/<repo>` in `_config.yml`.

These two can go in one PR.

## Carpentries-derived license (`license-carpentries`)

Follow [`knowledge/standards.md`](../../knowledge/standards.md) section 1.

1. Create `LICENSE` from `templates/LICENSE` (CC BY 4.0, verbatim).
2. Create `LICENSE-CODE` from `templates/LICENSE-CODE-MIT`. **Keep MIT**,
   because the existing license already put code under MIT. Copyright line:
   the authors listed in the repo (AUTHORS, README, `.all-contributorsrc`) or
   "HSF Training contributors", with the year the lesson started (first
   commit).
3. `LICENSE.md`:
   - **Jekyll lessons:** keep it, because the theme navbar links to it, but
     turn it into a short page (keep the front matter) that says the material
     is CC BY 4.0 and code is MIT, linking both files.
   - **Other platforms:** delete it and update links to it.
4. Add the "License" section from `templates/README.md` to the README.
5. Keep the Carpentries attribution only if the lesson is actually derived
   from Carpentries material. If unsure, keep it and ask in the PR.
6. The PR body must ask the maintainers for sign-off, and must say that no
   license terms changed, only the files' wording and layout.

Repos with **no license** at all get an issue, not a PR (see standards).
