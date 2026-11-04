---
name: write-repo-agents-md
description: Write or update an AGENTS.md file in an hsf-training repository that tells coding agents how that specific lesson is built, tested and structured, so future maintenance there is faster and safer. Use when asked to make a repo agent-friendly, or after working out a repo's build quirks that are worth recording.
---

# Write a per-repo AGENTS.md

A good `AGENTS.md` records what an agent would otherwise have to rediscover:
exact build commands, content conventions, CI behavior and pitfalls.
`hsf-training-llms-for-hep/AGENTS.md` is the reference example.

## Steps

1. Clone the repo (`workspace-setup`) and **actually build it**
   (`build-and-preview`). Every command you write down must have been run
   successfully, or be marked as not verified.

2. Start from the platform doc in `knowledge/platforms/` and keep only what
   applies to this repo, plus anything specific you discovered. Sections:
   - **What this is:** module name, platform, site URL, companion repos, and
     whether it's a translation of another lesson.
   - **Commands:** environment setup, build, preview and clean, exactly as
     CI runs them, with the required tool versions.
   - **Content structure and conventions:** where content lives, how pages
     are ordered or registered (TOC, file prefixes), episode format,
     exercise and solution markup, where figures and data go, citations.
   - **CI:** what each workflow does and which files are synced from
     `hsf-training-ai-maintenance` templates.
   - **Other notes:** pitfalls, plus the AI disclosure rules (`Assisted-by:`
     trailer, no `Co-authored-by` for agents) with a link to
     <https://github.com/hsf-training/hsf-training-ai-maintenance/blob/main/knowledge/contribution-policy.md>.

3. Keep it short and factual. Link to upstream docs instead of copying them.
   Don't include anything that changes often (e.g. open issues).

4. If the repo has a `CLAUDE.md`, make it contain only `@AGENTS.md`, or
   remove it. Don't keep two diverging instruction files.

5. Show the operator the file. After approval, open a PR ([Pushing and opening PRs](../../knowledge/contribution-policy.md#pushing-and-opening-prs)). Mention
   that the file is for coding agents, and that maintainers can edit it like
   any other doc.
