# The `hsf-training` organization

The [HSF Training](https://hepsoftwarefoundation.org/activities/training.html)
group of the HEP Software Foundation trains researchers in High Energy Physics to
write high-quality, sustainable software. The
[`hsf-training`](https://github.com/hsf-training) GitHub organization hosts its
training modules ("lessons") and the infrastructure around them.

Facts marked *(as of YYYY-MM-DD)* are snapshots. Re-check them with `gh` before
relying on them.

## Useful links

- Training Center (catalog of all modules): <https://hsf-training.org/training-center/>
  (source: [`training-center`](https://github.com/hsf-training/training-center)).
  The old curriculum page on the HSF website redirects there.
- Upcoming events: <https://hepsoftwarefoundation.org/Schools/events.html>
- Past and upcoming training events: `_data/training-schools.yml` in
  [`HSF/hsf.github.io`](https://github.com/HSF/hsf.github.io) (title, dates,
  Indico link, `HSF` tag for events organized or supported by HSF). It doesn't
  record which modules were taught. For that, check the event's Indico
  timetable.
- Mailing list: `hsf-training-wg@googlegroups.com`
- Org profile shown on GitHub: [`.github/profile/README.md`](https://github.com/hsf-training/.github/blob/main/profile/README.md)

## People

The training conveners coordinate the group. In bot messages and agent-written
text, mention the team `@hsf-training/training-conveners` instead of
individual people.

Each lesson also has its own maintainers, usually its most recent active
contributors. Find them in the repo's README (all-contributors table, AUTHORS)
or from `git log`/`gh pr list --state merged` before asking for a review.

## Kinds of repositories

| Kind | Examples | Notes |
|---|---|---|
| Lesson webpage | `hsf-training-matplotlib`, `hsf-training-scikit-hep-webpage`, `array-oriented-programming` | The rendered site is the deliverable. See [`platforms/`](platforms/) for how each stack works. |
| Companion repo | `hsf-training-cms-analysis` (for `-cms-analysis-webpage`), `hsf_matplotlib_notebooks` (for `-matplotlib`) | Code or notebooks that learners clone during a lesson. Changes must stay in sync with the lesson text. |
| Infrastructure | `.github`, `hsf-training-theme`, `cookiecutter-jupyter-book`, `training-center`, this repo | Changes here affect many lessons at once. |
| Fork | `git-novice` (from `mambelli/git-novice`), `learner-certificates` (from `carpentries/learner-certificates`) | Maintained, but prefer syncing with upstream over diverging. Don't "standardize" files that upstream owns. |
| Other | `participation-analysis`, `PyHEP-resources`, `python-lesson`, `cpluspluscourse` | Check each repo's README. |
| Archived | `maintenance`, `carpentry-cookiecutter`, `hsf-training-uproot-webpage`, ... | Read-only. Don't open issues or PRs. They may still be useful as reference. |

The curated inventory is [`repos.toml`](repos.toml): kind, platform, default
branch, Pages setup and Training Center ids for every repo. Refresh it with the
`repo-inventory` skill.

External modules listed in the Training Center (e.g. the ROOT student course,
UnROOT) live in other organizations and are **out of scope**.

## Infrastructure repositories

- **[`.github`](https://github.com/hsf-training/.github)**: organization-wide
  [community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file):
  `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE.md`, and the
  org profile. GitHub uses these for any repo that doesn't have its own copy, so
  per-repo copies of these files are usually unwanted duplicates. Workflows and
  bot configs in `.github/.github/` are **not** inherited. They only apply to the
  `.github` repo itself.
- **[`hsf-training-theme`](https://github.com/hsf-training/hsf-training-theme)**:
  the remote Jekyll theme that Jekyll lessons load at build time (see
  [`platforms/jekyll-carpentries.md`](platforms/jekyll-carpentries.md)).
  Lessons only pick up theme changes when they are rebuilt.
- **[`cookiecutter-jupyter-book`](https://github.com/hsf-training/cookiecutter-jupyter-book)**:
  the template for new modules. *(as of 2026-10-28 it generates a Jupyter
  Book 1 project in `book/`)*. Its predecessor for Jekyll lessons,
  `carpentry-cookiecutter`, is archived.
- **[`training-center`](https://github.com/hsf-training/training-center)**:
  an Astro site deployed to <https://hsf-training.org/training-center/>.
  `data/data.yaml` lists every module (id, name, repository, webpage, status,
  level, language, videos). `data/curricula.yaml` defines the curated
  curriculum. When a lesson is created, renamed, moved or archived, this catalog
  needs updating too.

## Bots and services

- **GitHub Pages** serves every lesson at `https://hsf-training.github.io/<repo>/`.
  Some lessons deploy from a branch and some from a workflow. See the
  platform docs.
- **pre-commit.ci** runs each repo's `.pre-commit-config.yaml` on PRs and
  opens monthly autoupdate PRs. The configs usually include codespell, with
  repo-specific ignore words in `codespell.txt`.
- **Dependabot** (`.github/dependabot.yml`) keeps GitHub Actions versions up
  to date.
- **Stale and welcome bots** (`.github/stale.yml` for probot-stale,
  `.github/config.yml` for behaviorbot welcome) mark inactive issues and PRs and
  greet first-time contributors.
- **all-contributors** (`.all-contributorsrc`) maintains the contributor table
  in many READMEs.

## Things that commonly surprise agents

- **The default branch varies.** Many Jekyll lessons use `gh-pages` as the
  default branch, and some older repos use `master`. Always target the default
  branch reported by
  `gh repo view hsf-training/<repo> --json defaultBranchRef`, and never assume
  `main`.
- **Scheduled workflows can stop silently.** GitHub disables scheduled
  workflows in public repos after 60 days without repository activity. A
  lesson whose monthly build "always worked" may simply not have run for a
  long time. Check `gh run list` before trusting it.
- **Earlier bulk changes were only partly applied.** The archived `maintenance`
  scripts, such as move-to-theme and removing org-wide file copies, were not
  applied to every repo. Don't assume consistency, so check each repo.
- **Lessons are taught live.** Before merging content changes, check the
  Training Center and the events page for upcoming events using the module.
  Avoid restructuring a lesson shortly before it is taught.
