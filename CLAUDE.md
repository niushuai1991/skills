# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **catalog of skills** for AI coding assistants (Claude Code, OpenCode). It is not an application: there is **no build system, package manager, test suite, or linter**. Each skill is a self-contained folder of instructions plus standalone scripts — the assistant loads a skill's `SKILL.md` when a matching task is detected. Do not look for or add a build/test pipeline.

Scripts here are invoked individually by the assistant (or user) at runtime, each from within its own skill directory. There are no shared libraries between skills.

## Skill anatomy (the pattern across all skills)

```
skills/<skill-name>/
├── SKILL.md          # Entry point + routing trigger
├── scripts/          # Standalone executables, optional
├── references/       # Deep-detail docs, optional
├── templates/        # Reusable output templates, optional
├── examples/         # Completed examples, optional
├── evals/            # Evaluation prompts or fixtures, optional
└── agents/           # Supporting agent prompts or rubrics, optional
```

Three conventions that only become visible by reading multiple `SKILL.md` files:

1. **Frontmatter drives routing.** `SKILL.md` starts with YAML frontmatter: `name` (skill id) and `description` (when to use). The `description` is the assistant's matching signal — phrase it as a trigger ("Use when…"). Bilingual skills write the description in Chinese (e.g. `douyin-video`); keep the existing language of the skill you're editing.

2. **Progressive disclosure.** `SKILL.md` holds quick-start + workflow only. Detailed references (command lists, API endpoints, migration checklists) live in `references/` and are linked from `SKILL.md` with explicit "load this when…" guidance. Don't inline exhaustive detail into `SKILL.md`; don't make the assistant read references it doesn't need for the task.

3. **Scripts are self-contained and env-var configured.** Each script reads its config from environment variables (e.g. `JENKINS_URL`/`JENKINS_USER`/`JENKINS_TOKEN`, `API_KEY`), not from config files or arguments-with-secrets. Match this when extending one.

## Working in this repo

**Adding a skill:** create `skills/<name>/SKILL.md` (frontmatter + instructions) plus `scripts/` and `references/` as needed. Then **update both `README.md` and `README.CN.md`** — the English and Chinese READMEs are kept in sync as a single table of skills; forgetting one leaves them divergent.

**Editing an existing skill:** match the language already used in that skill's `SKILL.md` (English or Chinese). `springboot-migration` uses a two-mode design (`migrate` vs `check`) gated off the user's wording — preserve that dispatch if you touch it.

**Commit style:** Conventional Commits — `feat:`, `docs:`, `fix(scope):`. Recent history shows one commit per skill addition and paired README updates.

## Notes on specific skills

- **`bilibili-downloader/`** is currently untracked and is **third-party code**, not original. Its `README.md` records provenance (source repo, anonymous numeric-username author) and a line-by-line security audit with sha256 hashes. If you touch those files, preserve the provenance/audit framing — do not strip it as "ordinary docs."

- **`playwright`** (`scripts/pw.sh`) wraps the Playwright CLI inside a Docker container and manages multiple sessions via a JSON state file (`/tmp/playwright-sessions-<uid>.json`, manipulated with `jq`). Sessions auto-expire after 30 min of inactivity. The container runs with `--network host`, so `localhost` reaches the host directly.
