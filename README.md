# Agent-assisted maintenance of HSF Training modules

This repository helps maintainers of the [HSF Training](https://hepsoftwarefoundation.org/workinggroups/training.html)
modules in the [`hsf-training`](https://github.com/hsf-training) organization
use **their own coding agent** (Claude Code, Codex, Gemini CLI, Copilot,
Cursor, ...) for maintenance work. That includes keeping lessons building,
updating outdated software and links, cleaning up legacy files, and keeping
shared configuration consistent across repos.

There are no API keys to configure and nothing to install. The repo contains:

- **Knowledge** ([`knowledge/`](knowledge/)): how the organization is set up,
  how each kind of lesson is built and deployed, and the rules for
  agent-assisted contributions.
- **Skills** (`skills/`, coming soon): step-by-step procedures for
  recurring maintenance tasks, in the [Agent Skills](https://agentskills.io)
  format.

It replaces the archived [`maintenance`](https://github.com/hsf-training/maintenance)
scripts and an earlier Gemini-based tool that lived in this repo. See
[`PLAN.md`](PLAN.md) for the roadmap.

## Usage

1. Install and authenticate the [GitHub CLI](https://cli.github.com/)
   (`gh auth login`).
2. Clone this repo and start your agent in it:

   ```bash
   gh repo clone hsf-training/hsf-training-ai-maintenance
   cd hsf-training-ai-maintenance
   claude    # or codex, gemini, ...
   ```

   The agent picks up [`AGENTS.md`](AGENTS.md), which points it to everything
   else.

3. Ask for what you need, for example:
   - "Check whether `hsf-training-docker` still builds and fix what's broken."
   - "Which lessons still vendor the Carpentries theme files?"
   - "Look for outdated package versions in `hsf-training-scikit-hep-webpage`."

The agent works in local clones under `../hsf-workspace/` and asks before doing
anything visible to others, such as pushing, opening PRs or commenting. You are
responsible for reviewing what it proposes. See the
[contribution policy](knowledge/contribution-policy.md).

## Contributing

Improvements to the knowledge base and skills are very welcome. If an agent got
something wrong because a doc here was missing or inaccurate, fix the doc.
Install the [pre-commit](https://pre-commit.com/) hooks before committing:

```bash
pip install pre-commit   # or use prek
pre-commit install
```

## License

Documentation is licensed under [CC BY 4.0](LICENSE). Code is licensed under the
[BSD 3-Clause License](LICENSE-CODE).
