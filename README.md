# Agent-assisted maintenance of HSF Training modules

This repository helps maintainers of the [HSF Training](https://hepsoftwarefoundation.org/activities/training.html)
modules in the [`hsf-training`](https://github.com/hsf-training) organization
use **their own coding agent** (Claude Code, Codex, Gemini CLI, Copilot,
Cursor, ...) for maintenance work. That includes keeping lessons building,
updating outdated software and links, cleaning up legacy files, and keeping
shared configuration consistent across repos.

There are no API keys to configure and nothing to install. The repo contains:

- **Knowledge** ([`knowledge/`](knowledge/)): how the organization is set up,
  how each kind of lesson is built and deployed, and the rules for
  agent-assisted contributions.
- **Skills** ([`skills/`](skills/)): step-by-step procedures for recurring
  maintenance tasks, in the [Agent Skills](https://agentskills.io) format.
  See the list in [`AGENTS.md`](AGENTS.md#skills).
- **Templates** ([`templates/`](templates/TEMPLATES.md)): shared files such as
  the pre-commit config, bot configs and licenses.
- **Scripts** ([`scripts/`](scripts/)): small standard-library Python helpers
  for the inventory, audits and the local workspace.

It replaces the archived [`maintenance`](https://github.com/hsf-training/maintenance)
scripts. See [`PLAN.md`](PLAN.md) for the roadmap.

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
   - "Audit the org and tell me what's broken."
   - "Look for outdated package versions in `hsf-training-scikit-hep-webpage`."

The agent works in local clones under `../hsf-workspace/` and asks before doing
anything visible to others, such as pushing, opening PRs or commenting. You are
responsible for reviewing what it proposes. See the
[contribution policy](knowledge/contribution-policy.md).

> [!WARNING]
> The agent can do anything your GitHub credentials allow. If you are an org
> admin, that includes archiving, renaming and transferring repos. With the
> `delete_repo` scope, it also includes deleting them. The agent is told never
> to delete, transfer or rename a repo, and to archive one only with your
> explicit approval, but instructions are not a guarantee. To limit what it can
> do:
>
> - Check that `gh auth status` doesn't list `delete_repo`. If it does, remove
>   it with `gh auth refresh --remove-scopes delete_repo`.
> - Better, give the agent a fine-grained token without the "Administration"
>   permission, set only in its environment (`GH_TOKEN=... claude`). See
>   [Limiting what the agent's credentials can do](knowledge/contribution-policy.md#limiting-what-the-agents-credentials-can-do).

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
