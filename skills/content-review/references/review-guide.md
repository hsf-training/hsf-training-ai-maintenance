# Content review guide

What to look for, what counts as evidence, and what to leave alone. Read the
section for a category before recording a finding in it.

## Categories

### `broken`: code or instructions that fail

The highest-value findings, because learners hit them during a workshop.

- **Look for:** cells or code blocks that error, setup commands that fail
  (`pip install` of a removed package, a conda environment that doesn't
  solve), datasets and files that no longer download, outputs that no longer
  match what the text says.
- **Evidence:** the failing command and its error output, from your own run
  in the lesson's environment. "This will probably fail" is not evidence.
- **Fix:** the smallest change that makes it work again, plus the text and
  stored outputs that refer to it.

### `outdated`: software, APIs and versions

- **Look for:** deprecated or removed APIs (deprecation warnings in the build
  log are a good lead), versions in text and setup instructions that are no
  longer supported, tools that have been superseded, screenshots of UIs that
  changed a lot.
- **Evidence:** the package's changelog, release notes or deprecation notice
  (link it), and the updated code run with the new version.
- **Leave alone:** versions that are old but still work and are still
  supported. A version bump on its own is the job of `update-dependencies`.
- HEP examples: uproot 3 → 4+ (`uproot.open(...)["tree"].arrays()` API),
  awkward 0/1 → 2, coffea 0.7 → 2024+, ROOT 5 → 6 idioms, `python2` / `print`
  statements, `setup.py`-only packaging, CentOS 7 / SL7 images,
  `actions/checkout@v2`.

### `practice`: practices the community moved away from

- **Look for:** advice that is now discouraged, e.g. `pip install` outside an
  environment, `sudo pip`, `conda` from `defaults` where `conda-forge` is
  needed, `import *`, committing notebooks with huge outputs, `latest` Docker
  tags in instructions meant to be reproducible.
- **Evidence:** the current official docs or a widely accepted guide (e.g.
  the [Scientific Python development guide](https://learn.scientific-python.org/development/),
  the Python Packaging User Guide).
- **Leave alone:** style preferences. Two valid ways to do something are not
  a finding.

### `links`: broken or moved resources

- **Look for:** the output of `scripts/check_links.py`. Also check references
  without URLs ("see the ROOT User's Guide, chapter 7") if they're central to
  an exercise.
- **Evidence:** the checker's status plus your own look at the page. For a
  moved page, confirm the new URL has the same content. For a dead one, find
  the replacement (the project's current docs, the Wayback Machine for
  context, a DOI instead of a PDF link).
- **Leave alone:** "check" results you couldn't confirm either way. Mention
  them in the report as unverified, not as findings.

### `accuracy`: statements that are wrong

- **Look for:** factual claims about software behavior, performance, defaults
  or physics conventions that are wrong or no longer true.
- **Evidence:** a source (official docs, release notes, a paper, the PDG) or
  a minimal run that shows the actual behavior.
- **Leave alone:** simplifications made on purpose for teaching. Physics
  content is the maintainers' call. Raise it as a question, not a correction.

### `example`: examples and exercises that could be better

- **Look for:** exercises whose solution doesn't match the question,
  examples that rely on data or services that are gone, examples that could
  use a more current, equally simple approach.
- **Evidence:** the alternative written out and run.
- These are almost always **judgment calls** (issue, not PR).

### `new`: recent developments worth a mention

- **Look for:** a widely adopted tool or approach that the lesson's topic
  would naturally mention today (e.g. `uv` for environment setup, Pixi, the
  Scikit-HEP tools that replaced older ones).
- **Evidence:** adoption signals (official recommendation, docs, usage in
  the experiments), not novelty.
- Always an issue, low priority, and at most a few per lesson. A lesson isn't
  outdated because it doesn't mention every new tool.

## Priority

| Priority | Meaning |
|---|---|
| high | Broken or wrong: learners will hit an error or learn something false. |
| medium | Outdated: works today, but teaches a deprecated way or will break soon (deprecation warning, end-of-life version). |
| low | Nice to have: clearer examples, new tools, polish. |

## PR or issue

Make it a **PR** only if all of these hold:

- the fix is mechanical and has one obviously right answer,
- you verified it (ran the code, rebuilt the site, opened the new link),
- it doesn't change what the lesson teaches, its difficulty, or its
  prerequisites.

Everything else goes into the **issue**: pedagogy, rewrites, new topics,
changes to prerequisites, dropping material, physics content.

## Difficulty check

For each proposed change, ask:

- Does it introduce a concept the lesson hasn't explained by that point?
- Does it change the prerequisites listed on the setup page or landing page?
- Does it make an exercise noticeably harder or easier?
- Does it lengthen an episode beyond its stated teaching time?

A "yes" turns the change into a judgment call for the maintainers.

## Not findings

Don't report these, they waste the maintainers' time:

- formatting or style preferences, unless they break rendering,
- the lesson's choice of tools when the choice is still reasonable,
- old but working and supported versions,
- typos in code comments that don't confuse,
- things already reported in an open issue or fixed in an open PR (check
  with `gh issue list` / `gh pr list` first, and link them instead),
- anything you couldn't verify. Mention it under "not verified" in your
  report, and leave it out of the issue.
