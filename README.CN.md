# 技能集合

面向 AI 编程助手（OpenCode、Claude Code 等）的专用技能仓库。每个技能为特定任务提供专门的指令、工作流和脚本。

## 已有技能

| 技能 | 描述 |
|------|------|
| **playwright** | 基于 Playwright CLI + Docker 的 Web 测试和浏览器自动化。采用会话式容器架构，支持多会话并行（独立浏览器实例），可同时登录多个账户。支持截图、页面交互、UI 验证。会话 30 分钟无操作自动超时。 |
| **jenkins** | 通过 REST API（HTTP Basic Auth）管理 Jenkins 任务、构建和节点。支持触发构建（带/不带参数）、查看状态与日志、管理构建队列、监控 Agent 节点。内置 CSRF crumb 自动获取和构建轮询等待。 |
| **douyin-video** | 抖音无水印视频下载与硅基流动 SenseVoice API 语音转文字。自动将每个视频的文案保存到以视频 ID 命名的独立目录。下载无需 API 密钥，语音转文字需要配置 API_KEY 环境变量。 |
| **springboot-migration** | Spring Boot 2.x → 3.x 迁移指南与自动化扫描工具。两种模式：`migrate` 引导完整迁移流程（JDK 17、javax→jakarta、依赖升级、Security 6.0、配置属性变更）；`check` 自动扫描项目检测迁移遗漏项（残留 javax import、废弃 API、过时依赖坐标）。 |
| **bilibili-downloader** | Bilibili 视频下载。分别下载视频流和音频流，含纯音频变体。公开视频无需登录/cookie。 |
| **writing-unit-tests** | 编写干净、隔离的单元测试的参考原则。核心规则：把被测代码在自身内存之外修改的东西（HOME、环境变量、cwd、时钟、网络）重定向到一次性沙盒，确保测试不会污染宿主/开发者的真实环境。 |

## 目录结构

每个技能遵循统一布局：

```
skills/<skill-name>/
├── SKILL.md              # 技能定义和指令
├── scripts/              # 可执行脚本
└── references/           # 参考文档
```

## 使用方式

克隆仓库并配置你的 AI 助手从 `skills/` 目录加载技能：

```bash
git clone https://github.com/niushuai1991/skills.git
```

将助手的技能目录指向克隆路径即可。每个 `SKILL.md` 是自包含的，当检测到匹配任务时助手会自动加载对应技能。

## 许可证

MIT
