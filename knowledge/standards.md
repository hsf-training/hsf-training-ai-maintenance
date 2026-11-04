# Repository standards

What a healthy `hsf-training` repository looks like. `scripts/audit.py` checks
the mechanical parts. Each rule below lists the audit check ids (in
backticks) that detect a violation.

Levels:

- **Required**: fix when found.
- **Recommended**: fix when touching the repo anyway, or in a campaign.
- **Optional**: depends on the repo, so don't push it.

Scope depends on the repo's `kind` in [`repos.toml`](repos.toml):

- **Lessons** get everything.
- **Companion, infra and other** repos get everything except the
  lesson-specific rules.
- **Forks** only get the CI and hygiene rules (sections 5 and 6). Anything
  else should be changed upstream first.
- **Archived** repos are never changed.

Deliberate deviations are fine. Record them in `repos.toml` so audits and
agents don't keep "fixing" them: add the check id to the repo's
`ignore_checks` (the audit then skips it) and explain why in `notes`.

## 1. Licensing

- **Required: a license.** `license-missing`
  - Default for **new** modules: `LICENSE` with CC BY 4.0 for the material, and
    `LICENSE-CODE` with BSD-3-Clause for code. Templates are in
    [`templates/`](../templates/).
  - The authors choose. A repo without a license gets an **issue** suggesting
    the default, not a PR.
- **Recommended: no Carpentries-derived license text.** `license-carpentries`
  - Many lessons have a `LICENSE.md` copied from the Carpentries template. It
    attributes the material to Software Carpentry and puts code under MIT.
  - Split it into `LICENSE` (CC BY 4.0) and `LICENSE-CODE`, **keeping MIT** for
    code (`templates/LICENSE-CODE-MIT`). Don't relicense existing lessons.
  - Keep an attribution note in the README only for lessons that really are
    derived from Carpentries material.
  - **Jekyll lessons must keep `LICENSE.md`.** The theme's navbar uses
    `{% link LICENSE.md %}`, which fails the build if the file is missing.
    Turn it into a short site page (keep the front matter) that summarizes
    both licenses and links to `LICENSE` and `LICENSE-CODE`. On the pilot PR,
    check which license GitHub detects with several license files present.
  - The PR asks the maintainers for sign-off.
- **Required, with two license files: a README "License" section** saying
  which file covers what. Code files, code snippets and notebook code cells are
  covered by `LICENSE-CODE`, and everything else by `LICENSE`.

## 2. Community files

- **Required: `README.md`.** `readme-missing` Lessons follow
  [`templates/README.md`](../templates/README.md): link to the rendered site,
  short description, how to contribute and preview locally, contributors, and
  license. A "Past events" section is optional.
- **Recommended: `CONTRIBUTING.md`** for lessons, based on
  [`templates/CONTRIBUTING.md`](../templates/CONTRIBUTING.md) and tailored to
  the repo (default branch, how to preview).
- **Recommended: no per-repo copies of org-wide files.** `org-file-duplicate`
  - `.github/ISSUE_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE.md` and
    `.github/FUNDING.yml` come from the org's `.github` repo. Delete per-repo
    copies unless they're deliberately different.
  - Code of conduct: don't have both `CONDUCT.md` and `CODE_OF_CONDUCT.md`.
    `conduct-duplicate` Jekyll lessons **must** keep `CODE_OF_CONDUCT.md`,
    because the theme's navbar uses `{% link CODE_OF_CONDUCT.md %}` and the
    build fails without it. Elsewhere the org default is enough.
- **Recommended: no legacy CI.** `travis` (`.travis.yml`).

## 3. Shared tooling

The shared files in [`templates/`](../templates/) are **starting points, not
files to copy verbatim**. Tailor each one to the repo (see
[Tailoring templates](#tailoring-templates)). Differences from the template are
expected, and the audit only flags missing or outdated parts.

- **Required: `.pre-commit-config.yaml`**, run by pre-commit.ci.
  `precommit-missing`
  - Must include the `pre-commit-hooks` basics and `codespell` with
    repo-specific words in `codespell.txt`.
  - Has a `ci:` block with the pre-commit.ci commit messages
    (`chore(deps): update pre-commit hooks`, `style: pre-commit fixes`) and
    `autoupdate_schedule: "monthly"`, as in the
    [Scientific Python style guide](https://learn.scientific-python.org/development/guides/style/).
  - Hook versions are kept current by pre-commit.ci's monthly autoupdate.
    Outdated revs usually mean pre-commit.ci isn't enabled for the repo.
    `precommit-outdated`
- **Required for repos with workflows: `.github/dependabot.yml` with the
  `github-actions` ecosystem.** `dependabot-missing`, `dependabot-no-actions`
  - Add other ecosystems the repo actually uses (`pip`, `bundler`, `npm`,
    `docker`, ...).
  - A failing Dependabot job (`dependabot-failing`) usually means the config
    names an ecosystem or directory with nothing in it.
- **Recommended: stale and welcome bots** (`.github/stale.yml`,
  `.github/config.yml`). `bots-missing`
  - They must mention `@hsf-training/training-conveners`, never individual
    people. `bots-individual-mentions`
- **Required: no "CENTRALLY MAINTAINED FILE" headers.** `legacy-header` These
  point to the archived maintenance repo. Remove them when syncing. The audit
  also checks copies at any depth, e.g. the shared files inside
  `cookiecutter-jupyter-book`'s template directory, which every new module
  inherits.

## 4. Platform-specific (lessons)

See [`platforms/`](platforms/README.md) for details.

**Jekyll + Carpentries**

- **Recommended: use `remote_theme: hsf-training/hsf-training-theme`.**
  - `jekyll-vendored-theme`: the full theme is vendored. Migrating is
    per-repo work.
  - `jekyll-theme-leftovers`: the repo uses the remote theme but still has
    `_layouts/`, `assets/` or `bin/`.
- **Recommended: no Carpentries Makefile.** `carpentries-makefile` Its
  targets depend on `bin/` scripts that were removed. Delete it and document
  the `bundle exec jekyll serve` commands in the README.
- **Recommended: no empty `_episodes_rmd/`.** `empty-episodes-rmd`
- **Recommended: no `repository: <USERNAME>/<PROJECT>` placeholder in
  `_config.yml`.** `config-placeholder` Set it to `hsf-training/<repo>`.

**Jupyter Book 1**

- **Required: pin `jupyter-book<2`** (or migrate to JB2). An unpinned
  install gets JB2, which can't build a JB1 book. `build-tool-unpinned`
  The pin belongs in the environment files (`environment.yml`,
  `requirements.txt`), not only in CI. Otherwise local builds that follow the
  README get JB2.

**All lessons**

- **Recommended: the site builds on PRs**, not only on deploy, so breakage is
  caught before merging.
- **Recommended: automated link checking with
  [lychee](https://github.com/lycheeverse/lychee-action)**
  (see [`templates/.github/workflows/check-links.yml`](../templates/.github/workflows/check-links.yml)).
  `no-link-check`, `link-check-deprecated` (the old gaurav-nelson action is
  unmaintained).

## 5. CI health

- **Required: the latest run of each workflow on the default branch
  succeeds.** `ci-failing`
- **Required: the Pages site builds.** `pages-errored`
- **Required: one way of deploying.** `pages-source-mismatch` If a workflow
  deploys with `actions/deploy-pages`, the Pages source must be "GitHub
  Actions". Otherwise a branch build runs as well, and the two deploys race.
  Switching the source is an admin action.
- **Required: Actions runs where there are workflows.** `actions-not-running`
  Workflow files that GitHub never registered usually mean Actions is
  disabled for the repo, which is common for forks. Enabling it is an admin
  decision.
- **Recommended: no workflows disabled for inactivity.** `workflow-disabled`
  - GitHub disables scheduled workflows after 60 days without activity in
    the repo.
  - Re-enable a workflow (`gh workflow enable`, after the operator approves)
    only if its builds still pass. Otherwise fix the build first.

## 6. Settings and hygiene

- **Recommended: "Automatically delete head branches" on.**
  `delete-branch-on-merge-off`
- **Recommended: a repository description**, and the **homepage set to the
  Pages site** for repos that have one. `description-missing`,
  `homepage-missing`
- **Recommended: no stale branches.** `stale-branches` These are branches
  that are merged, or that have no commits in over a year.
  - Delete them only after listing them for the operator. Some are kept on
    purpose, e.g. old workshop snapshots.
  - Never delete the default branch or the Pages source branch.
- **Recommended: bot PRs don't pile up.** `bot-prs-pending` Dependabot and
  pre-commit.ci PRs open for more than 30 days mean nobody is merging updates.
- **Not required: branch protection.** Decided 2026-10-28: there are too few
  maintainers for required reviews or PR-only merging to work. Existing
  protections are left as they are.

## 7. Training Center

- **Recommended: every active lesson is listed** in
  `training-center/data/data.yaml`. `training-center-missing`
- **Recommended: archived lessons are removed** from the catalog, or marked
  accordingly. `training-center-archived`

## 8. Content (not checked by the audit)

These need judgment and are handled by the `content-review` and
`update-dependencies` skills.

- Code in lessons runs with current versions of its dependencies, and
  versions in setup instructions are pinned or current.
- Links work and point to current documentation.
- Code fences use ```` ``` ```` rather than `~~~` where tools such as
  blacken-docs need it, but follow the lesson's existing style.

## Tailoring templates

| Template | Tailor by |
|---|---|
| `.pre-commit-config.yaml` | Point `files:`/`exclude:` at the repo's real content (`_episodes/`, `book/`, `content/`, ...). Add `blacken-docs` only if the lesson has Python snippets in Markdown. Add `nbstripout` only if notebook outputs shouldn't be committed (not for books that render stored outputs). Keep hooks the repo already relies on (e.g. linters for companion code). |
| `codespell.txt` | Keep repo-specific words (physics jargon, package names, non-English text). Don't remove words without checking that codespell still passes. |
| `.github/dependabot.yml` | Keep `github-actions`. Add `pip`, `bundler`, `npm`, `docker`, ... only for manifests that exist, with the right `directory`. |
| `.github/stale.yml` | Usually unchanged. Exempt labels can be added per repo. |
| `.github/config.yml` | Usually unchanged. |
| `.github/workflows/check-links.yml` | Adjust paths, and exclude known-flaky or rate-limited hosts in `lychee.toml`/`.lycheeignore`. For built sites, checking the built HTML catches more than checking the Markdown. |
| `LICENSE` / `LICENSE-CODE` | Choose the code license (BSD-3-Clause for new modules, MIT for existing Carpentries-based lessons). Fill in the copyright line: the module's authors or "HSF Training contributors", and the year the module started. |
| `CONTRIBUTING.md` | Default branch name, how to preview locally, where to ask questions. |
| `README.md` | Everything in angle brackets. Drop sections that don't apply. |
