---
name: writing-event-report
description: Use when documenting operational events as structured Markdown reports, including incidents, faults, outages, deployments, configuration changes, routine maintenance, security events, postmortems, RCA requests, event records, or analysis reports.
---

# Writing Event Report

Create factual, source-backed operational event reports in Markdown. Do not invent evidence; if a field is unknown, mark it as `待确认` or `未提供` and list what is needed to verify it.

## Event Types

Choose the closest event type from the user's context:

| Type | Use for | Template |
|------|---------|----------|
| Fault event | Outages, crashes, performance degradation, OOM, database failures, network incidents | `templates/fault-event-template.md` |
| Change event | Deployments, configuration changes, upgrades, migrations, infrastructure changes | `templates/change-event-template.md` |
| Operation event | Maintenance, backups, inspections, capacity planning, routine operational work | `templates/operation-event-template.md` |
| Security event | Unauthorized access, suspicious processes, malware, breaches, policy violations, audit findings | `templates/security-event-template.md` |

If the event spans multiple types, use the dominant type and add cross-impact notes in the report.

## Workflow

1. Identify the event type, time range, affected systems, severity, and intended audience.
2. Read exactly one matching template from `templates/`.
3. Collect available evidence from the conversation, files, logs, commands, tickets, monitoring links, or user-provided notes.
4. Draft the report using the template structure. Keep conclusions tied to explicit data sources.
5. Save the report as Markdown when the user asks for a file, a report record, or does not specify inline-only output.

Default filename:

```text
YYYY-MM-DD-event-type-brief-description.md
```

Example: `2026-07-21-fault-metabase-oom-crash.md`

Use the user-specified directory when provided; otherwise save in the current working directory.

## Evidence Collection

Only run local diagnostic commands when they are relevant and safe for the environment. Prefer read-only commands and explain unavailable sources in the report.

Common fault or performance sources:

```bash
uptime
free -h
top -bn1 | head -20
ps aux --sort=-%cpu | head -20
ps aux --sort=-%mem | head -20
journalctl --since "YYYY-MM-DD HH:MM" --until "YYYY-MM-DD HH:MM" --no-pager
dmesg | tail -50
```

Common network sources:

```bash
ss -tlnp
netstat -tlnp
```

Common security sources:

```bash
last -a
who
ps aux
ss -tunap
```

Application evidence usually comes from `/var/log/`, application log directories, deployment logs, monitoring dashboards, database logs, change tickets, and incident chat transcripts.

## Report Requirements

Every report should include:

- Header metadata: date, time range, event type, severity, affected systems, owner or handler when known.
- Executive summary: one short paragraph describing what happened and current status.
- Timeline: chronological sequence with source-backed timestamps.
- Analysis: direct cause, root cause or current hypothesis, trigger conditions, and uncertainty.
- Impact: service, user, data, business, security, or operational impact as applicable.
- Data sources: commands, files, dashboards, tickets, logs, or user-provided statements used.
- Recommendations: specific short-term and long-term actions with measurable outcomes where possible.
- Lessons learned or follow-up items for team reuse.

## Supporting Files

- `templates/fault-event-template.md`: fault report template.
- `templates/change-event-template.md`: change report template.
- `templates/operation-event-template.md`: operation report template.
- `templates/security-event-template.md`: security report template.
- `examples/server-crash-example.md`: completed OOM crash report example.
- `references/schemas.md`: metadata, eval, and grading schemas.
- `evals/evals.json`: representative evaluation prompts.
- `agents/grader.md`: grading rubric for generated reports.

## Quality Bar

- Separate facts from assumptions.
- Cite every important conclusion to a data source.
- Keep recommendations actionable and scoped.
- Use tables for timelines, evidence, and impact summaries.
- Avoid blaming individuals; describe system conditions and process gaps.
