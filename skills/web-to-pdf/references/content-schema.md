# content.json 格式说明

`build_web_pdf.py` 的唯一内容输入。顶层字段 + 有序 `blocks` 数组，模型按网页内容
（可翻译、可摘要、可改写）把内容整理成 blocks，脚本负责全部排版。

## 顶层字段

```json
{
  "title": "构建智能体（Building Agents）· 简体中文翻译版",
  "subject": "PDF 元数据描述（一句话）",
  "author": "Z.ai",
  "language": "zh",                  // zh | en，影响目录标题默认值与缩进习惯
  "toc": true,                       // 是否生成目录页（≥3 页的文档建议 true）
  "toc_title": "目录",               // 可省略，默认按 language 取“目录/Contents”
  "header_text": "页眉左侧小字",      // 可省略，默认取 title
  "footer_text": "页脚左侧小字",      // 可省略，如 “简体中文翻译版 · 译自 example.com”
  "margin_cm": 2.0,                  // 可省略，默认 2.0cm 左右边距
  "palette": {                       // 可省略；省略时脚本自动调 palette.generate 生成
    "accent": "#b55333",             // 主题色：标题分隔线/表头/封面强调
    "text":   "#1c1e1f",             // 正文色
    "muted":  "#6f757a",             // 次要文字/图注/页眉页脚
    "mid":    "#e0e4e7",             // 表格斑马纹/提示框底色
    "bg":     "#ffffff"              // 页面底色（封面要求白或极浅）
  },
  "cover": {                         // 省略整个 cover = 无封面（≤2 页文档建议省略）
    "template": "01",                // 封面模板：01 HUD(科技) 02 Corporate(年报)
                                     // 03 Monolith(白皮书/提案) 04 Museum(简约画册)
                                     // 05 Sidebar(政府/投标) 09 Institutional(机构)
    "kicker":  "眉题小字 · 大写拉丁或中文",
    "hero":    "封面主标题（最显眼，建议不超过 5 个汉字，过长会折行产生孤字）",
    "summary": "2-4 行摘要",
    "meta":    "元信息行（如：中文翻译版 · 2026 年 · 译自 example.com）",
    "footer":  "页脚大写拉丁字串",
    "year":    "2026",
    "word":    "WATERMARK"           // 封面水印词
  },
  "blocks": [ ... ]                  // 正文内容，按序渲染
}
```

## blocks 块类型

| type | 字段 | 说明 |
|------|------|------|
| `h1` | `text`, `lead?` | 一级标题：带主题色下划线、防孤行、进目录 level0。`lead` 可选，为标题后第一段 |
| `h2` | `text`, `lead?` | 二级标题，进目录 level1 |
| `h3` | `text`, `lead?` | 三级标题，不进目录 |
| `para` | `text`, `indent?` | 正文段。`indent` 默认 true（中文首行缩进 2 字符；英文习惯传 false） |
| `bullets` | `items[]` | 无序列表 |
| `numbered` | `items[]` | 有序列表（自动编号 1. 2. 3.） |
| `callout` | `text` | 主题色左边框提示框（定义、经验法则、要点总结） |
| `note` | `text` | 灰色小字注释框（译注、免责声明、版权说明） |
| `table` | `headers[]?`, `rows[][]`, `widths[]?`, `width_ratio?`, `caption?` | 表格：斑马纹+主题色表头；`widths` 为各列比例(和为1)；`width_ratio` 默认 0.96 |
| `image` | `file`, `caption?`, `max_height?` | 插图：`file` 相对 assets-dir 或绝对路径；`max_height` 单位 pt，默认页高 1/3；caption 自动与图同页 |
| `hr` | `style?`, `thickness?` | 分隔线：`accent`（主题色）或默认灰色 |
| `spacer` | `height` | 垂直留白（pt） |
| `pagebreak` | — | 强制分页（慎用；正文默认自然流动） |

## 内联标记（所有 text 类字段支持）

直接写 ReportLab mini-HTML，脚本只对裸 `&` 做自动转义：

- `<b>粗体</b>`、`<i>斜体</i>`、`<u>下划线</u>`
- `<font face="Times New Roman">代码/模型名</font>` —— 西文等宽感名称用衬线体区分
- `<a href="https://..." color="#b55333">链接文字</a>`
- `<super>2</super>` / `<sub>2</sub>`、`<br/>` 换行

## 章节编号约定

`h1`/`h2` 的编号由内容自带（如 "1. 引言"、"2.1 选择模型"），脚本不做自动编号。
翻译类文档建议沿用原文编号；改编类文档按逻辑分节编号。

## 最小可用示例

```json
{
  "title": "示例文档",
  "subject": "演示 content.json 用法",
  "language": "zh",
  "cover": {
    "kicker": "DEMO · 演示文档",
    "hero": "示例标题",
    "summary": "这是一份演示文档，展示 content.json 的最小用法。",
    "meta": "2026 年 · 示例",
    "footer": "DEMO DOCUMENT",
    "year": "2026",
    "word": "DEMO"
  },
  "blocks": [
    {"type": "h1", "text": "1. 开始", "lead": "这是第一段正文，随标题保持在同一页。"},
    {"type": "callout", "text": "重要结论放在提示框里。"},
    {"type": "h2", "text": "1.1 列表与表格"},
    {"type": "bullets", "items": ["第一点", "第二点"]},
    {"type": "table",
     "headers": ["名称", "说明"],
     "rows": [["A", "说明文字"], ["B", "说明文字"]],
     "widths": [0.3, 0.7],
     "caption": "表 1：示例表格"},
    {"type": "image", "file": "demo.png", "caption": "图 1：示例插图", "max_height": 300},
    {"type": "note", "text": "译注：本文档由 Z.ai 协助生成，仅供学习交流。"}
  ]
}
```
