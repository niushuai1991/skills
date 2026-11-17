---
name: spec-index
description: Create, refresh, and maintain repository spec-index.md files and related specification documents, including design specs, plans, implementation notes, statuses, links, replacement relationships, and deletion of old or superseded specs. Use when Codex is asked to create or update spec-index.md, maintain spec docs, prune outdated docs, catalog docs/specs/ files, summarize spec status, add new specs to an index, or build quick navigation for project specification documents.
---

# Spec Index

## Overview

Create and maintain concise `spec-index.md` files that help coding agents and maintainers find the right spec before editing code. Keep the index, spec metadata, links, and relationships aligned with repository evidence; delete old or superseded spec files instead of preserving stale copies. Do not invent architecture, status, dates, or relationships that are not supported by the files.

## Workflow

1. Locate the target index and source docs.
   - If the user gives a path, use it. Otherwise prefer `docs/spec-index.md` when the repo has a `docs/` directory.
   - Search for existing indexes and source docs with `rg --files -g 'spec-index.md' -g '*.md'`.
   - Treat `docs/specs/` as the default directory for created spec documents, creating it when it does not exist. Also check nearby `plans/`, `README.md`, deployment docs, templates, and implementation docs that the specs reference.

2. Inventory every spec.
   - Sort dated specs by date and then filename, and numbered specs by number.
   - Read enough of each spec to extract title, date, status, scope, related docs, replacement notes, and implementation references.
   - Use filename dates only when the document itself lacks an explicit date.

3. Choose the index shape from the evidence.
   - For a small design set, use sections like `Spec 文档`, `关联实现文档`, and `约定`.
   - For a larger project/domain spec set, use sections like `Spec 文档目录`, `快速导航`, `按修改场景`, `按组件查找`, `项目核心流程`, and `关键架构决策` only when the source docs clearly support them.
   - Keep the index compact. Prefer tables and short bullets over long summaries.

4. Write repository-relative links.
   - Links in `docs/spec-index.md` to files under `docs/specs/` should look like `specs/<file>.md`.
   - Links to files outside the index directory must use correct relative paths such as `../docker-images/...`.
   - Use code formatting for paths that do not have a useful Markdown target.

5. Keep the repository `AGENTS.md` linked to the index.
   - After creating or refreshing the index, add or update a link to `spec-index.md` in the repository root `AGENTS.md` (under a suitable existing section, or a new `## Spec 文档` section) so coding agents can discover the index.
   - Create a minimal `AGENTS.md` containing just the link when the repository has none.

6. Refresh content and prune old specs.
   - Keep custom sections that remain accurate.
   - Update stale summaries, statuses, ordering, and links.
   - Delete old, duplicate, or superseded spec files when replacement evidence is clear or the user asks for old specs to be removed.
   - Remove index entries and links for deleted specs; mention replacement notes in the surviving spec or index only when useful.

7. Maintain related spec docs when requested.
   - When adding a spec, register it in the index with a repository-relative link and a one-line goal.
   - When revising a spec, update the spec document itself (dates and revision notes belong in the spec's own header); do not touch the index unless the spec file is added, deleted, moved, or renamed.
   - When a spec supersedes another, keep the new spec and index current, then delete the superseded spec file unless the user explicitly asks to retain it.
   - When implementation docs move or are renamed, update spec cross-references and index links together.

## Content Rules

- Write all spec and index content in Chinese — headings, summaries, and body prose (e.g. `Spec 文档索引`); keep code, file paths, commands, and identifiers unchanged.
- Include one-line summaries grounded in the spec content.
- Keep each index entry minimal: a link and a one-line goal. Record dates, revision history, and design details inside the spec documents themselves; never append revision entries to the index when a spec is revised.
- Do not keep old specs merely for history; delete superseded files and keep only concise replacement notes where they help navigation.
- Include relationship diagrams only when they clarify replacement, dependency, or deployment relationships.
- Avoid adding speculative architecture, unverified component ownership, or generated line counts.
- If important metadata is missing, either omit that column or write a neutral value such as `未标注`; do not fabricate.

## Validation

Before finishing:
- Confirm every spec source file is represented or intentionally excluded.
- Confirm old, duplicate, or superseded spec files are deleted unless there is a clear reason to retain them.
- Check that all Markdown links are relative to the index file location.
- Confirm the repository `AGENTS.md` links to `spec-index.md`.
- Re-read the final index for stale copied text from another repository.
- When practical, run a link/path check with shell tests or `rg --files` against each linked local path.
