# Skills Collection

A collection of specialized skills for AI coding assistants (OpenCode, Claude Code, etc.). Each skill provides dedicated instructions, workflows, and scripts for specific tasks.

## Skills

| Skill | Description |
|-------|-------------|
| **playwright** | Web testing and browser automation using Playwright CLI with Docker. Capture screenshots, interact with pages, verify UI behavior. |
| **jenkins** | Manage Jenkins jobs, builds, and nodes via REST API. Trigger builds, check status, view logs, manage queue and nodes. |
| **douyin-video** | Download Douyin (TikTok) videos without watermark and extract speech-to-text captions automatically. |
| **springboot-migration** | Guide Spring Boot version migration with automated scanning, dependency updates, property changes, and verification checklists. |

## Directory Structure

Each skill follows a standard layout:

```
skills/<skill-name>/
├── SKILL.md              # Skill definition and instructions
├── scripts/              # Executable scripts
└── references/           # Reference documentation
```

## Usage

Clone this repository and configure your AI assistant to load skills from the `skills/` directory:

```bash
git clone https://github.com/niushuai1991/skills.git
```

Then point your assistant's skill directory to the cloned path. Each `SKILL.md` is self-contained — the assistant will load it when a matching task is detected.

## License

MIT
