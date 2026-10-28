# Plan: agent-driven maintenance for `hsf-training`

## Goal

Turn this repository from a standalone Python tool (Gemini API + GitHub token +
custom CLI) into a **knowledge base and skill library** that any maintainer can
point their own coding agent at (Claude Code, Codex, Gemini CLI, Copilot,
Cursor, ...) to maintain the repositories of the
[`hsf-training`](https://github.com/hsf-training) organization.

The repository will contain:

- **Knowledge**: what the org looks like, which repos exist, how each kind of
  lesson is built and deployed, and what a "healthy" repo looks like.
- **Skills**: step-by-step procedures for recurring maintenance tasks, written for
  agents but readable by humans.
- **Small helper scripts** (stdlib-only Python or `gh` one-liners) where gathering
  facts deterministically is cheaper and more reliable than letting the agent do
  it by hand.

There will be no API keys, LLM client code, or bespoke CLI. The operator brings
the agent and their own `gh` authentication. The agent does the fuzzy part
(judgment, merging, writing), and a human reviews every change before it
leaves their machine.

This replaces both the current Gemini-based agent in this repo and the archived
[`hsf-training/maintenance`](https://github.com/hsf-training/maintenance)
scripts.

## Current state of the org (survey, 2026-10-28)

This snapshot came from `gh` queries and motivates the work below. It goes stale
quickly. The `repo-inventory` and `repo-audit` skills (below) will regenerate it.

- **~35 active, ~23 archived repos.** The active ones are lesson webpages,
  companion code repos, infra (`.github`, `hsf-training-theme`,
  `cookiecutter-jupyter-book`, `training-center`) and a couple of forks
  (`git-novice`, `learner-certificates`).
- **Many build stacks in use:**
  - Jekyll + Carpentries + `remote_theme: hsf-training/hsf-training-theme`
    (matplotlib, cicd, cmake, docker, reana, singularity, generators, ml-gpu)
  - MyST / Jupyter Book 2 (`myst.yml`: scikit-hep, scikit-hep-es, databases-basics,
    llms-for-hep)
  - Jupyter Book 1 (array-oriented-programming, deep-learning-intro-for-hep,
    unix-shell, ssh-webpage, and the `cookiecutter-jupyter-book` template).
    Two of these don't pin `jupyter-book`, so they would now pull in JB2 and
    break.
  - Sphinx via LHCb starterkit-ci (analysis-essentials)
  - Hugo (cicd-github)
  - Carpentries sandpaper (git-novice fork)
  - JupyterLite (array-oriented-puzzles)
  - LaTeX/Beamer (cpluspluscourse)
- **Leftovers from earlier campaigns that were never finished:**
  - `move-to-theme` was not applied everywhere. advanced-cpp-bits, advanced-git,
    cms-analysis-webpage and ml-webpage have no `remote_theme` and still vendor
    the full Carpentries theme (`_layouts/`, `_includes/`, `assets/`, `bin/`).
  - `remove-organization-wide-files` was not applied everywhere. advanced-cpp-bits
    still has `.travis.yml`, `.github/FUNDING.yml`, `ISSUE_TEMPLATE.md`,
    `PULL_REQUEST_TEMPLATE.md`, and scikit-hep-webpage has its own issue/PR templates.
- **Bot configs that are probably dead.** Most repos carry `.github/stale.yml`
  (probot-stale, archived upstream) and `.github/config.yml` (behaviorbot
  welcome). Their "CENTRALLY MAINTAINED FILE" header points to the archived
  maintenance repo, and the stale message pings maintainers from 2022.
- **Licenses are inconsistent.** Most lessons ship a Carpentries-derived
  `LICENSE.md` (GitHub reports `NOASSERTION`, and it says "Copyright © Software
  Carpentry" even for original content). Others use BSD-3-Clause, CC-BY-4.0,
  Apache-2.0, MIT or GPL-3.0, and several have no license at all
  (hsf_matplotlib_notebooks, hsf-training-cms-analysis, this repo).
- **Branch protection varies.** About half the active repos protect the
  default branch. "Automatically delete head branches" is off on most.
- **Other drift:** duplicate `CONDUCT.md` + `CODE_OF_CONDUCT.md`, Jekyll configs
  with the `repository: <USERNAME>/<PROJECT>` placeholder, missing
  `dependabot.yml` in a few repos, and an org-level link checker that uses
  `actions/checkout@master` and the unmaintained `markdown-link-check` action.
- **Prior art:** `hsf-training-llms-for-hep` already has an `AGENTS.md`, which is
  a good model for per-repo agent docs.

## Design principles

1. **Harness-agnostic.** Plain Markdown. `AGENTS.md` is the entry point. Skills
   follow the open [Agent Skills](https://agentskills.io) format (`SKILL.md` with
   `name`/`description` frontmatter), which most harnesses can load. Agents
   without skill support can still read them as docs.
2. **Read-only by default.** Every skill first produces a report or a diff, and
   writing to GitHub (PRs, issues, settings) is a separate, explicitly confirmed
   step.
3. **Mechanical facts come from scripts, judgment comes from the agent.** For
   example, a script lists which repos have `stale.yml`, and the agent decides
   how to merge a customized `.pre-commit-config.yaml`.
4. **Humans own the result.** Agent-assisted commits carry an `Assisted-by:`
   trailer. PR descriptions disclose AI assistance. Nothing is pushed to a
   default branch directly. Bulk changes are verified locally (build + diff
   review) and piloted as a PR on one repo before going wide.
5. **Keep state in GitHub, not in the agent.** Campaigns are tracked as issues in
   this repo (a checklist of repos with PR links), so work can be picked up by a
   different person with a different agent.

## Proposed layout

```
.
├── AGENTS.md                 # entry point: purpose, rules of engagement, index of knowledge + skills
├── CLAUDE.md                 # one line: @AGENTS.md (Claude Code shim)
├── README.md                 # human-facing: what this is, how to use it with your agent
├── PLAN.md                   # this file (delete once implemented)
├── knowledge/
│   ├── org-overview.md       # org structure, infra repos, people/contacts, training-center, .github org files
│   ├── contribution-policy.md# AI-disclosure, review, branching, PR etiquette for agent-made changes
│   ├── standards.md          # the target state of a repo (files, CI, settings, README sections)
│   ├── repos.yaml            # inventory: repo → kind, platform, deploy, status, notes
│   └── platforms/
│       ├── README.md         # how to identify a repo's platform
│       ├── jekyll-carpentries.md
│       ├── jupyter-book-1.md
│       ├── myst-jupyter-book-2.md
│       ├── hugo.md
│       ├── jupyterlite.md
│       └── other.md          # starterkit-ci Sphinx, LaTeX, sandpaper, Astro, plain repos
├── templates/                # blueprints of shared files (successor of add-common-files/)
│   ├── .pre-commit-config.yaml
│   ├── .github/dependabot.yml
│   ├── .github/stale.yml     # probot-stale, pinging @hsf-training/training-conveners
│   ├── .github/config.yml    # welcome bot, pinging @hsf-training/training-conveners
│   ├── .github/workflows/... # e.g. link check
│   ├── codespell.txt
│   ├── LICENSE               # default for material: CC BY 4.0
│   ├── LICENSE-CODE          # default for code in new modules: BSD-3-Clause
│   ├── LICENSE-CODE-MIT      # for existing lessons that already use MIT (copied as LICENSE-CODE)
│   ├── CONTRIBUTING.md
│   └── README.md             # README skeleton with standard sections
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md
│       └── scripts/          # optional stdlib-only helpers
├── .claude/skills -> ../skills   # symlinks so harnesses auto-discover skills
└── .agents/skills -> ../skills
```

Each `platforms/*.md` explains how to recognize the stack, build and preview it
locally, how CI deploys it, which files are boilerplate and which are content,
and known pitfalls (e.g. the JB2 notes already in llms-for-hep's `AGENTS.md`).

Files in `templates/` are **starting points, not files to copy verbatim**. The
agent tailors each one to the target repo's platform and contents, for example:

- `.pre-commit-config.yaml`: drop hooks that have nothing to act on, such as
  notebook hooks in a repo without notebooks or `blacken-docs` in a repo
  without Python snippets. Point `files:` filters at the repo's real content
  directories (`_episodes/` for Jekyll, `book/` or `skhep-tutorial/` for
  MyST, ...), and add hooks the platform needs.
- `dependabot.yml`: add ecosystems the repo uses (`pip`, `bundler`, `docker`,
  `npm`) and not the ones it doesn't.
- `codespell.txt`: keep repo-specific words, such as physics jargon and
  package names.

Each template has a short comment block or companion note in
`knowledge/standards.md` that explains which parts are required, which are
optional, and when to drop or change them. Tailored differences from the
template are expected and aren't flagged as drift by `repo-audit`. The audit
only flags missing required parts and outdated versions.

`repos.yaml` mixes fields derived from `gh` (archived, default branch, pages URL)
with hand-curated ones (kind, platform, companion repo, notes). The
`repo-inventory` skill refreshes the derived fields and flags new repos, but
keeps the curated ones. This replaces `repository_list/repositories.csv`.

**Scope:** every non-archived repo in `hsf-training`, including forks
(`git-novice`, `learner-certificates`). For forks, skills must take upstream
into account: prefer syncing with upstream over diverging, and don't
"standardize" files that upstream owns (e.g. sandpaper workflows). External
modules listed in training-center (ROOT student course, UnROOT, ...) are out of
scope.

## Skills

Listed roughly in implementation order. For each skill, the line in italics notes
which old script or issue it replaces or resolves.

### Foundation

| Skill | What it does |
|---|---|
| `repo-inventory` | Lists org repos via `gh`, detects platform from marker files (`_config.yml`+`remote_theme`, `myst.yml`, `conf.py`, `hugo.toml`, ...), updates `knowledge/repos.yaml`, and cross-checks the `hsf-training` entries in `training-center/data/data.yaml` (modules listed there but archived, active lessons missing from it). *Replaces `repository_list/`.* |
| `workspace-setup` | Clones or updates a chosen set of repos into a local workspace (e.g. `../hsf-workspace/`), on fresh branches. *Replaces the `gh repo clone` loop + `gita` notes.* |
| `repo-audit` | Checks one or all repos against `standards.md`. A script gathers facts (files present, workflow list, protection, repo settings, stale branches, pre-commit revs, `~~~` fences, license detection), and the agent writes a prioritized report: a table per repo plus suggested campaigns. Read-only. |

### Changing many repos

| Skill | What it does |
|---|---|
| `bulk-change` | The campaign procedure that replaces `multi-gitter`. Steps: (1) define the change and target set from `repos.yaml`/audit, (2) open a tracking issue in this repo, (3) apply to one repo locally, build it, show the diff, and open a pilot PR, (4) once the pilot is approved, apply to the rest, building each locally, adapting per repo where it isn't mechanical, (5) open PRs with a consistent branch name/title/body, (6) update the tracking issue checklist with PR links. *Replaces the multi-gitter README, `helpers/open_prs_browser.py` (PR links live in the tracking issue) and `helpers/switch_out_gitconfig.py` (not needed with `gh`).* |
| `sync-shared-files` | Reconciles a repo's copies of shared files with `templates/`, tailoring each template to the repo (see above) rather than copying it. It drops parts that don't apply, keeps intentional local customizations (extra hooks, extra codespell words), and explains each difference from the template in the PR body. It also strips the old "CENTRALLY MAINTAINED FILE" headers, since synced files no longer carry headers. *Replaces `add-common-files/` and resolves the partial-sharing idea of old #14/#15 without marker gymnastics.* |
| `legacy-cleanup` | Removes known cruft: vendored Jekyll theme files when `remote_theme` is set, `.travis.yml`, per-repo copies of org-wide `.github` files, duplicate code-of-conduct files, `_config.yml` placeholders, and missing keys like `hsf_site`. Verifies the site still builds. *Replaces `move-to-theme/`, `remove-organization-wide-files/`, `add-missing-config-key/`, `fix-link-license/`.* |
| `repo-settings` | Reads and (with confirmation and admin rights) applies repo settings: delete-branch-on-merge, topics, description, homepage, and Pages source. It can also delete merged/stale branches after listing them. Branch protection is deliberately not managed (see #13 below). *Resolves old #11.* |

### Content

| Skill | What it does |
|---|---|
| `content-review` | Successor of the Gemini agent. It reviews a lesson (or one episode) for outdated software versions and APIs, deprecated practices, broken or moved links, technical inaccuracies, and examples that could be better. Unlike the old tool, it **verifies** findings: it runs the code, checks PyPI/conda-forge/release notes, and follows links. It keeps the old constraints (no restructuring, preserve difficulty and learning objectives). Output: clear-cut fixes become a PR, and judgment calls become one issue per repo with a grouped checklist. The six analysis categories and the difficulty check from `hsf_training_agent/src/ai/prompt_templates.py` (removed in phase 1, see `git show fab2f86:hsf_training_agent/src/ai/prompt_templates.py`) carry over into this skill. |
| `update-dependencies` | Bumps pinned versions (`environment.yml`, `requirements.txt`, Docker images, setup instructions, `Gemfile`), re-executes notebooks and code snippets, builds the site, and reports what broke and why. |
| `build-and-preview` | Builds any lesson locally per its platform doc so other skills (and humans) can check that a change renders. It also explains how to trigger a Pages rebuild (`gh api -X POST repos/hsf-training/<repo>/pages/builds`). *Replaces `trigger-jekyll-rebuilds/`.* |
| `org-triage` | Lists open issues and PRs across the org: unanswered first-time contributors, PRs waiting for review, stale issues, failing scheduled CI. It drafts responses but doesn't post them, and it reports CI breakage. Complements the stale and welcome bots, which only ping. |

### Later / optional

| Skill | What it does |
|---|---|
| `past-events` | Finds the workshops/events where a module was taught (Indico, HSF events pages, training-center) and adds or updates a "Past events" section in the README (and the site's landing page where the platform allows). *Resolves old #12.* |
| `write-repo-agents-md` | Generates an `AGENTS.md` for a lesson repo (build commands, content conventions, CI) modeled on llms-for-hep's, so future agents work faster in that repo. |
| `migrate-platform` | Guidance for moving a lesson between stacks (e.g. Jekyll/Carpentries → MyST/JB2, as scikit-hep and databases-basics did), building on `cookiecutter-jupyter-book`. Only a playbook, since every migration is a per-repo project. |

## Addressing the open issues of `hsf-training/maintenance`

These become decisions recorded in `knowledge/standards.md`, then campaigns run
with `bulk-change`.

### #21 Fix & standardize licenses

- **Decided:** the default is **CC BY 4.0 for instructional material and
  BSD-3-Clause for code in new modules**. Existing lessons that already
  license code under MIT (from the Carpentries text) keep MIT. The license is
  still the authors' choice. `standards.md` states the defaults and that
  deviations are fine when deliberate.
- **Decided:** use separate files. `LICENSE` holds the verbatim CC BY 4.0
  text, so GitHub detects the license of the material. `LICENSE-CODE` holds
  the code license. The README template gets a short "License" section that says
  which file covers what: code files, code snippets and notebook code cells
  are under `LICENSE-CODE`, and everything else is under `LICENSE`.
- Provide both files in `templates/`. Copyright lines name the module's
  authors or "HSF Training contributors". They drop the incorrect "Copyright ©
  Software Carpentry" attribution, except for lessons that are actually
  derived from Carpentries material, which keep an attribution note in the
  README.
- Campaign: the audit lists the current license per repo.
  - Repos with no license get an issue asking the authors to pick one, with
    the default suggested. They don't get a PR, because the authors choose.
  - Repos with the Carpentries-derived `LICENSE.md` get a PR that splits it
    into `LICENSE` (CC BY 4.0) + `LICENSE-CODE`. The code part stays **MIT**,
    as it was in the Carpentries text, so nothing is relicensed. The PR body
    still asks for maintainer sign-off because the wording and copyright lines
    change.
  - Repos with a deliberate different license (e.g. cpluspluscourse
    Apache-2.0, python-lesson GPL-3.0) are left alone, and the license is
    recorded in `repos.yaml`.

### #19 Remove/change Carpentry Makefiles

- The Jekyll lessons carry the upstream Carpentries `Makefile`, which references
  `bin/` scripts that `move-to-theme` deleted. The first step is to confirm which
  targets still work.
- Recommended: replace it with a minimal `Makefile` (`serve`, `build`, `clean`)
  wrapping the Jekyll commands, or drop it and document the commands in the
  README. Either way, `platforms/jekyll-carpentries.md` documents the outcome and
  `legacy-cleanup` applies it.

### #13 Standardize branch protection rules

- **Decided: not now.** There are too few maintainers for required reviews or
  PR-only merging to be workable. `standards.md` records this decision and its
  reason, and the issue can be closed with a link to it. Existing protections
  are left as they are, and the audit doesn't flag unprotected repos.
- Still standardize delete-branch-on-merge (on) and clean up stale branches
  (old #11) via `repo-settings`.

### #12 Add list of past workshops to README

- Add an optional "Past events" section to the README template in `templates/`
  and `standards.md`.
- Implement the `past-events` skill. The data source needs to be identified
  first (Indico categories, HSF website event pages, training-center), so it
  is in the later phase.

## Other carry-overs from the old repo

- **Centrally maintained file headers.** These are dropped. Templates live
  here, and the agent reconciles them with each repo's copy. `sync-shared-files`
  removes the existing headers, which name the archived repo and `@klieret`.
- **Stale and welcome bots** (`.github/stale.yml`, `.github/config.yml`) stay
  for now. Their messages mention a team instead of individuals, so the list
  of people can change without touching every repo. No org-wide team exists
  before phase 1 (only `analysis-essentials-admins`, `cpluscplusadmin`,
  `cplusplusteam`), so phase 1 created `training-conveners`, mentioned as
  `@hsf-training/training-conveners`. It must be a visible (closed) team so
  that it can be mentioned. Update the org `.github`
  repo's copy too. The audit should also confirm the bots still act on
  repos; if they've stopped, revisit with `actions/stale` and
  `actions/first-interaction`.
- **Dependabot for GitHub Actions** (old #22) becomes part of `standards.md`.
  The audit flags repos without it.
- **`~~~` → ```` ``` ```` fences** (old #16/#20, needed for blacken-docs) becomes
  an audit check, and `legacy-cleanup` fixes what's left.
- **"Test on the sandbox repo first, always dry-run first"** becomes "verify
  locally first, pilot on one repo" in `bulk-change`. There's no sandbox repo:
  agents apply changes in a local clone, build the site, and show the diff
  before anything is pushed. `repository-maintenance-test` stays archived.

## Implementation phases

### Phase 0: decisions (done)

See [Decisions](#decisions). They get written into `standards.md` and
`contribution-policy.md` in phases 1–2.

### Phase 1: scaffold and knowledge (done)

- Remove the old tool: `hsf_training_agent/`, `examples/`, `requirements.txt`,
  `setup.py`, `.env.example`.
- Write `AGENTS.md`, the `CLAUDE.md` shim, a new `README.md`, and
  `knowledge/org-overview.md`, `contribution-policy.md` and `platforms/*`.
- Add `LICENSE` (CC BY 4.0, for the docs) and `LICENSE-CODE` (BSD-3-Clause,
  for the scripts) to this repo.
- Create the `training-conveners` team for bot mentions and add the current
  conveners.
- Fix `.pre-commit-config.yaml`. It was copied from a lesson, so
  `end-of-file-fixer` and `trailing-whitespace` are limited to `_episodes/`
  paths that don't exist here.

### Phase 2: inventory and audit

- Implement `repo-inventory`, generate `repos.yaml`, and curate it by hand once.
- Write `standards.md` and `templates/`.
- Implement `workspace-setup` and `repo-audit`, run the first org-wide audit,
  and post it as a tracking issue. That issue becomes the backlog for phase 3.

### Phase 3: campaigns

- Implement `bulk-change`, `sync-shared-files`, `legacy-cleanup`, `repo-settings`
  and `build-and-preview`.
- Run campaigns in roughly this order (lowest risk first): org-wide duplicates
  → shared-file sync (bot configs with the team mention, headers dropped,
  dependabot, pre-commit) → vendored theme files and Makefiles (#19) → licenses
  (#21) → repo settings and stale branches (#11).
- Close the old #13 by linking to the decision recorded in `standards.md`.

### Phase 4: content

- Implement `content-review` and `update-dependencies`. Pilot them on one
  actively taught lesson, then turn what we learn into the skills before
  running them more widely.
- Implement `org-triage`.

### Phase 5: later

- `past-events` (#12), `write-repo-agents-md`, `migrate-platform`.
- Optional: package the skills as a Claude Code plugin / marketplace entry, or
  similar for other harnesses. Scheduled unattended runs are out of scope
  because they bring back API keys and remove the human reviewer.

## Decisions

Made on 2026-10-28.

1. **License:** CC BY 4.0 for material and a separate code license, in
   separate files: `LICENSE` and `LICENSE-CODE`. Code is BSD-3-Clause for new
   modules and stays MIT for existing lessons that already use it, from the
   Carpentries text. The final choice is left to each module's authors.
2. **Branch protection:** not implemented for now, because there are too few
   maintainers.
3. **Shared-file headers:** dropped.
4. **Stale/welcome bots:** kept for now. They mention
   `@hsf-training/training-conveners` instead of individual people.
5. **Sandbox repo:** none. Agents test changes locally, then pilot on one repo.
6. **Scope:** forks in the org are maintained, with care for upstream. External
   modules get nothing.
7. **Repo name:** keep `hsf-training-ai-maintenance` for now.
