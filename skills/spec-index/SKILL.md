---
name: spec-index
description: Create, refresh, and maintain repository spec-index.md files and related specification documents, including design specs, plans, implementation notes, statuses, links, and replacement relationships. Use when Codex is asked to create or update spec-index.md, maintain spec docs, catalog docs/superpowers/specs/ files, summarize spec status, add new specs to an index, or build quick navigation for project specification documents.
---

# Spec Index

## Overview

Create and maintain concise `spec-index.md` files that help coding agents and maintainers find the right spec before editing code. Keep the index, spec metadata, links, and relationships aligned with repository evidence; do not invent architecture, status, dates, or relationships that are not supported by the files.

## Workflow

1. Locate the target index and source docs.
   - If the user gives a path, use it. Otherwise prefer `docs/spec-index.md` when the repo has a `docs/` directory.
   - Search for existing indexes and source docs with `rg --files -g 'spec-index.md' -g '*.md'`.
   - Treat `docs/superpowers/specs/` as the default spec directory when it exists. Also check nearby `plans/`, `README.md`, deployment docs, templates, and implementation docs that the specs reference.

2. Inventory every spec.
   - Sort dated specs by date and then filename, and numbered specs by number.
   - Read enough of each spec to extract title, date, status, scope, related docs, replacement history, and implementation references.
   - Use filename dates only when the document itself lacks an explicit date.

3. Choose the index shape from the evidence.
   - For a small historical design set, use sections like `Spec 文档`, `关系说明`, `关联实现文档`, and `约定`.
   - For a larger project/domain spec set, use sections like `Spec 文档目录`, `快速导航`, `按修改场景`, `按组件查找`, `项目核心流程`, and `关键架构决策` only when the source docs clearly support them.
   - Keep the index compact. Prefer tables and short bullets over long summaries.

4. Write repository-relative links.
   - Links in `docs/spec-index.md` to files under `docs/superpowers/specs/` should look like `superpowers/specs/<file>.md`.
   - Links to files outside the index directory must use correct relative paths such as `../docker-images/...`.
   - Use code formatting for paths that do not have a useful Markdown target.

5. Preserve useful existing content when refreshing.
   - Keep custom sections that remain accurate.
   - Update stale summaries, statuses, ordering, and links.
   - Add new specs without deleting historical specs unless the user explicitly asks.

6. Maintain related spec docs when requested.
   - When adding or revising a spec, keep its title, date, status, related docs, and replacement notes consistent with the index.
   - When a spec supersedes another, update both the new spec and the index so the historical relationship is explicit.
   - When implementation docs move or are renamed, update spec cross-references and index links together.

## Content Rules

- Use the language already dominant in the docs; for Chinese repos, use Chinese headings like `Spec 文档索引`.
- Include one-line summaries grounded in the spec content.
- Mark superseded specs as historical instead of removing them.
- Include relationship diagrams only when they clarify replacement, dependency, or deployment relationships.
- Avoid adding speculative architecture, unverified component ownership, or generated line counts.
- If important metadata is missing, either omit that column or write a neutral value such as `未标注`; do not fabricate.

## Validation

Before finishing:
- Confirm every spec source file is represented or intentionally excluded.
- Check that all Markdown links are relative to the index file location.
- Re-read the final index for stale copied text from another repository.
- When practical, run a link/path check with shell tests or `rg --files` against each linked local path.
