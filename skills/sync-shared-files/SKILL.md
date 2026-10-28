---
name: sync-shared-files
description: Bring a repo's shared configuration files (.pre-commit-config.yaml, .github/dependabot.yml, stale and welcome bot configs, link-check workflow, CONTRIBUTING.md) in line with templates/, tailored to the repo, and remove the old "CENTRALLY MAINTAINED FILE" headers. Use for findings like precommit-missing, dependabot-missing, bots-individual-mentions, legacy-header, link-check-deprecated, or when asked to standardize config across repos.
---

# Sync shared files from `templates/`

Templates are **starting points, not files to copy verbatim**. The goal is
that each repo has the *required* parts of each template, adapted to the repo,
and keeps intentional local customizations. Read
[`knowledge/standards.md`](../../knowledge/standards.md), sections 3 and
"Tailoring templates", first.

For more than one or two repos, run this inside the `bulk-change` procedure.

## Steps (per repo)

1. Prepare a clone on a work branch (`workspace-setup`). Read the repo's
   platform doc and look at its existing files before changing anything.

2. For each shared file, compare the repo's copy with `templates/` and decide
   what to do:

   | File | Do |
   |---|---|
   | `.pre-commit-config.yaml` | Make sure the baseline hooks and codespell are present. Keep extra hooks the repo uses. Point `files:`/`exclude:` filters at the repo's real content directories. Add `blacken-docs`/`nbstripout` only when they apply (see standards). Don't downgrade revs. |
   | `codespell.txt` | Keep it. Add words only if codespell flags correct jargon. |
   | `.github/dependabot.yml` | Keep `github-actions` if the repo has workflows. Remove ecosystems with nothing to update (they make the Dependabot job fail). Add ones whose manifests exist. |
   | `.github/stale.yml`, `.github/config.yml` | Replace individual mentions with `@hsf-training/training-conveners`, update dead links (e.g. `workinggroups/training.html` → `activities/training.html`), and keep repo-specific settings such as extra exempt labels. |
   | `.github/workflows/*link*` | Replace the unmaintained `gaurav-nelson/github-action-markdown-link-check` with the lychee template, and carry over its exclusions (`mlc_config.json` → `.lycheeignore` or `lychee.toml`). Then delete `mlc_config.json` if nothing else uses it. |
   | `CONTRIBUTING.md` | Only for lessons, and only if missing or clearly outdated (e.g. dead links, wrong default branch). Fill in the default branch and repo name. |

3. Remove the old header block that starts with
   `# === IMPORTANT: CENTRALLY MAINTAINED FILE ===` and ends with `# ======`.
   It points to the archived maintenance repo and to individual people.

4. Verify:
   - `pre-commit run -a`. New hooks may fix whitespace or spelling across the
     repo. That's fine, but say so in the PR, and if the diff gets large, put
     those fixes in a separate commit.
   - For workflow changes, check the YAML (`check-yaml` hook). If possible,
     check that the action versions exist
     (`gh api repos/<owner>/<action>/releases/latest`).

5. In the PR body, list every place the result **differs from the template**
   and why, e.g. "kept `black` hook for the companion code" or "no
   `debug-statements`: no Python files".

## Changing the templates themselves

If many repos need the same deviation, the template is probably wrong.
Propose a change to `templates/` and `knowledge/standards.md` in this repo
first.
