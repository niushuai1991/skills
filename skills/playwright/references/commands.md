# Playwright CLI Commands Reference

## Session Management

```bash
bash scripts/pw.sh session start       # Start new session, returns session id
bash scripts/pw.sh session list        # List all active sessions
bash scripts/pw.sh session stop [id]   # Stop session (default: current)
bash scripts/pw.sh session clean       # Stop all sessions and clean up
```

Sessions timeout after 10 minutes of inactivity.

## Browser Control

```bash
bash scripts/pw.sh open [url]                 # Open browser (headless by default)
bash scripts/pw.sh open [url] --browser chromium  # Use chromium
bash scripts/pw.sh open [url] --headed        # Open with UI (requires display)
bash scripts/pw.sh close                      # Close browser
bash scripts/pw.sh goto <url>                 # Navigate to URL
```

## Page Actions

```bash
bash scripts/pw.sh snapshot              # Capture snapshot (get element refs)
bash scripts/pw.sh click <ref>           # Click element
bash scripts/pw.sh dblclick <ref>        # Double click
bash scripts/pw.sh fill <ref> <text>     # Fill text
bash scripts/pw.sh type <text>           # Type text
bash scripts/pw.sh hover <ref>           # Hover
bash scripts/pw.sh select <ref> <value>  # Select dropdown option
bash scripts/pw.sh check <ref>           # Check checkbox/radio
bash scripts/pw.sh uncheck <ref>         # Uncheck
bash scripts/pw.sh drag <startRef> <endRef>  # Drag and drop
```

## Keyboard & Mouse

```bash
bash scripts/pw.sh press <key>           # Press key (Enter, Tab, ArrowLeft)
bash scripts/pw.sh mousemove <x> <y>     # Move mouse
```

## Screenshots & PDF

```bash
bash scripts/pw.sh screenshot --filename=output.png  # Take screenshot
bash scripts/pw.sh pdf --filename=output.pdf         # Save as PDF
```

## Debug

```bash
bash scripts/pw.sh console [level]       # View console messages
bash scripts/pw.sh network               # View network requests
bash scripts/pw.sh eval <func>           # Execute JavaScript
```

## Multiple Sessions

```bash
bash scripts/pw.sh session start         # Start session 1
bash scripts/pw.sh session start         # Start session 2 (becomes current)
bash scripts/pw.sh -s <id> <command>     # Execute in specific session
```

## Output Format

After each command, playwright-cli returns:
- Page URL and Title
- Console message counts
- Snapshot file path

Elements have refs like `e1`, `e2`. Use these for interactions.
