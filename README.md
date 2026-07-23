# Skills Collection

A collection of specialized skills for AI coding assistants (OpenCode, Claude Code, etc.). Each skill provides dedicated instructions, workflows, and scripts for specific tasks.

## Skills

| Skill | Description |
|-------|-------------|
| **playwright** | Web testing and browser automation using Playwright CLI with Docker. Session-based container architecture with multi-session support for parallel browser instances. Supports screenshots, page interaction, UI verification. Sessions timeout after 30 minutes of inactivity. |
| **jenkins** | Manage Jenkins jobs, builds, and nodes via REST API (HTTP Basic Auth). Trigger builds (with/without params), check status, view logs, manage build queue, monitor agent nodes. Includes auto crumb resolution and wait-for-build polling. |
| **douyin-video** | Download Douyin (TikTok) videos without watermark and extract speech-to-text captions via SiliconFlow SenseFlow API. Auto-saves each video's transcript to organized directories. No API key needed for downloads; API key required for transcription. |
| **springboot-migration** | Spring Boot 2.x to 3.x migration guide and automated scanner. Two modes: `migrate` guides a full migration (JDK 17, javax→jakarta, dependency upgrades, Security 6.0, config property changes); `check` scans a project to detect migration gaps (residual javax imports, deprecated APIs, outdated dependencies). |
| **bilibili-downloader** | Bilibili video/audio downloader. Separate video and audio streams; audio-only variant included. No login/cookie needed for public videos. |
| **writing-unit-tests** | Reference principles for writing clean, isolated unit tests. Headline rule: isolate anything the code under test mutates outside its own memory (HOME, env, cwd, clock, network) by redirecting it to a throwaway sandbox, so tests never clobber host/developer state. |
| **writing-event-report** | Generate structured Markdown reports for operational events: incidents, outages, deployments, configuration changes, maintenance, security events, postmortems, RCA requests, and event records. Includes report templates, examples, schemas, eval prompts, and a grading rubric. |

## Directory Structure

Each skill follows a standard layout:

```
skills/<skill-name>/
├── SKILL.md              # Skill definition and instructions
├── scripts/              # Executable scripts (optional)
├── references/           # Reference documentation (optional)
├── templates/            # Reusable output templates (optional)
├── examples/             # Completed examples (optional)
├── evals/                # Evaluation prompts or fixtures (optional)
└── agents/               # Supporting agent prompts or rubrics (optional)
```

## Usage

Clone this repository and configure your AI assistant to load skills from the `skills/` directory:

```bash
git clone https://github.com/niushuai1991/skills.git
```

Then point your assistant's skill directory to the cloned path. Each `SKILL.md` is self-contained — the assistant will load it when a matching task is detected.

## License

MIT
