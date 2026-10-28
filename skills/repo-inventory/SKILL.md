---
name: repo-inventory
description: Refresh knowledge/repos.toml, the inventory of hsf-training repositories (kind, platform, default branch, Pages setup, Training Center entries), and report repos that need curation or are out of sync with the Training Center. Use when the inventory may be stale, when repos were created, renamed or archived, or before an org-wide audit or campaign.
---

# Refresh the repository inventory

`knowledge/repos.toml` is the list of repos that other skills and scripts work
from. Some fields are **derived** from GitHub and some are **curated** by hand
(`kind`, `companion_of`, `notes`). The script keeps the curated fields.

## Steps

1. Run the script from the repo root (needs Python ≥ 3.11 and `gh` auth):

   ```bash
   python3 scripts/inventory.py --dry-run   # summary only
   python3 scripts/inventory.py             # rewrite knowledge/repos.toml
   ```

2. Review `git diff knowledge/repos.toml`. Expected changes are new or
   removed repos, archived flags, platforms, Pages settings and Training
   Center ids. Anything else (e.g. a lesson whose platform changed) is worth
   mentioning to the operator.

3. **Curate** every repo the summary lists under "Need a curated `kind`":
   - `kind`:
     - `lesson`: a training module with a rendered site or course material.
     - `companion`: code or notebooks used by a lesson. Also set
       `companion_of`.
     - `infra`: shared infrastructure (`.github`, theme, cookiecutter,
       training-center, this repo).
     - `fork`: set automatically for forks.
     - `other`: anything else.
   - `notes`: only durable facts an agent needs before touching the repo, such
     as "Spanish translation of X" or "workflows owned upstream". Don't put
     audit findings here.
   - `ignore_checks`: audit check ids that deliberately don't apply (e.g.
     `license-carpentries` for the theme, which really is Carpentries-derived).
     Explain why in `notes`.
   - **Renamed repos** show up as one entry "no longer in the org" (the script
     prints its curated fields) plus one new uncurated entry. Copy the curated
     fields over.
   - If `platform` is wrong, fix `detect_platform()` in `scripts/inventory.py`
     instead of editing the field, since derived fields get overwritten.

4. Report the Training Center mismatches from the summary to the operator:
   - archived repos still listed,
   - active lessons not listed,
   - catalog entries pointing to repos that don't exist.

   Don't edit `training-center` yourself as part of this skill. Fixing those is
   a separate change in that repo.

5. If the inventory changed, commit it on a branch of this repo. After the
   operator approves, push and open a PR ([Pushing and opening PRs](../../knowledge/contribution-policy.md#pushing-and-opening-prs)).
