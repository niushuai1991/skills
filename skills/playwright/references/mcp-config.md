# Playwright MCP Configuration

## Agent Detection & Configuration

Detect the current agent and configure Playwright MCP:

| Agent | Detection | Configuration |
|-------|-----------|---------------|
| **opencode** | Check `~/.config/opencode/opencode.json` | Add to `mcp` section |
| **Claude Code** | Check `~/.claude/` | Run: `claude mcp add playwright npx @playwright/mcp@latest` |
| **Claude Desktop** | Check `~/Library/Application Support/Claude/` (macOS) or `%APPDATA%\Claude\` (Windows) | Edit `claude_desktop_config.json` |
| **Cursor** | Check `~/.cursor/` | Run: Cursor Settings → MCP → Add new MCP Server |
| **VS Code** | Check `.vscode/` or run `code --version` | Run: `code --add-mcp '{"name":"playwright","command":"npx","args":["@playwright/mcp@latest"]}'` |
| **Codex** | Check `~/.codex/` | Run: `codex mcp add playwright npx "@playwright/mcp@latest"` |
| **Windsurf** | Check `~/.windsurf/` | Edit MCP config with standard config |
| **Cline** | Check `cline_mcp_settings.json` | Add to `mcpServers` section |
| **Copilot** | Check `~/.copilot/` | Edit `mcp-config.json` |

## Standard MCP Config

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

## opencode Specific Config

For opencode, use this format in `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "playwright": {
      "type": "local",
      "command": ["npx", "@playwright/mcp@latest"],
      "enabled": true
    }
  }
}
```

## Docker-based MCP Config

If using Docker-based Playwright MCP:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--init", "--pull=always", "mcr.microsoft.com/playwright/mcp"]
    }
  }
}
```

## Official Documentation

https://github.com/microsoft/playwright-mcp
