---
name: playwright
description: Web testing using Playwright CLI with Docker. Use when you need to test web pages, interact with websites, capture screenshots, verify UI behavior, or perform browser automation.
---

# Playwright Web Testing

Session-based temporary container mode. Browser state persists within a session.

## Quick Start

```bash
# Start a session
bash scripts/pw.sh session start
# → outputs session id (e.g., abc12345)

# Execute commands (uses current session)
bash scripts/pw.sh open https://example.com --browser chromium
bash scripts/pw.sh snapshot
bash scripts/pw.sh click e1
bash scripts/pw.sh screenshot --filename=result.png

# Stop session when done
bash scripts/pw.sh session stop
```

## Workflow

1. `bash scripts/pw.sh session start` → creates container, returns session id
2. Execute commands → same browser, state persists
3. `bash scripts/pw.sh session stop` → container deleted

## Session Management

```bash
bash scripts/pw.sh session start       # Start new session
bash scripts/pw.sh session list        # List active sessions
bash scripts/pw.sh session stop [id]   # Stop session (default: current)
bash scripts/pw.sh session clean       # Clean all sessions
```

## Multiple Sessions

```bash
bash scripts/pw.sh session start       # Session 1 (becomes current)
bash scripts/pw.sh session start       # Session 2 (becomes current)
bash scripts/pw.sh -s <id1> click e1   # Execute in specific session
```

## Notes

- Sessions timeout after 30 minutes of inactivity
- Container uses `--network host`, so `localhost` works directly

## Reference

See [references/commands.md](references/commands.md) for complete command list.
