# 技能集合

面向 AI 编程助手（OpenCode、Claude Code 等）的专用技能仓库。每个技能为特定任务提供专门的指令、工作流和脚本。

## 已有技能

| 技能 | 描述 |
|------|------|
| **playwright** | 基于 Playwright CLI + Docker 的 Web 测试和浏览器自动化。支持截图、页面交互、UI 验证。 |
| **jenkins** | 通过 REST API 管理 Jenkins 任务、构建和节点。支持触发构建、查看状态/日志、管理队列和节点。 |
| **douyin-video** | 抖音无水印视频下载与语音转文字文案提取，自动保存到本地文件。 |

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
