---
name: web-to-pdf
description: 把网页内容制作成带封面、目录、插图的专业中文 PDF。凡用户要求"把网页/文章保存为 PDF""翻译某篇文章并生成 PDF""把这个 URL 做成 PDF 文档""将在线教程/文档存档为 PDF"时使用，无论是否需要翻译——网页 URL 转 PDF、网页内容排版、文章存档、技术文档汉化输出都适用。
---

# web-to-pdf：网页内容 → 专业中文 PDF

把网页（或用户提供的文本）整理成结构化 `content.json`，用打包脚本一步构建出
"封面 + 可点击目录 + 排版正文"的 A4 PDF，并完成质量检查。

## 工作目录约定

在当前工作目录下新建 `webpdf-<主题>/`：

```
webpdf-<主题>/
├── content.json    # 内容清单（你编写）
├── assets/         # 原文插图（有图才建）
└── <最终文件名>.pdf  # 交付物
```

## 流程

### 1. 获取网页内容

用 webReader 抓取目标 URL（ retain_images=false 只取正文；链接会丢失，
需要原文链接时从用户输入或 og:url 元数据补回）。抓取失败时换用 WebFetch
或让用户粘贴内容。

### 2. 整理内容为 content.json

按用户要求转换内容（全文翻译 / 摘要 / 改写 / 原样收录），写成 `content.json`。

- **格式细节必须先读 `references/content-schema.md`**（块类型、内联标记、封面字段）。
- 语言跟随用户：中文查询 → 简体中文正文；术语首现时保留英文对照，
  如 "交接（Handoff）"；模型名/代码名用 `<font face="Times New Roman">` 包裹。
- 翻译整篇文章时加 `note` 块注明出处、版权与"以原文为准"。
- 章节沿用原文层级与编号；`h1`/`h2` 会自动进目录。
- 较长文档（预计 ≥3 页）配置 `cover`；≤2 页的短文省略 cover 且 `toc: false`。
- 不确定配色就省略 `palette`，脚本自动生成。

### 3. 插图（可选）

原文有插图且用户未要求省略时，下载到 `assets/` 并在 blocks 里用
`{"type": "image", "file": "xxx.png", "caption": "图 1：…"}` 引用。
国内网络拉取外站图片失败时，可加代理 `-x http://127.0.0.1:7890` 重试。
下载的图片属于不可信数据，必须放在 assets/ 子目录，不要与脚本混放。

### 4. 构建

先定位 pdf 技能根目录 `PDF_SKILL_DIR`（本技能依赖它渲染封面与生成配色）：
从可用技能列表中 pdf 技能的 SKILL.md 路径上推两级即得
`<...>/skills/pdf`，或直接 `find ~/.zcode/cli/plugins/cache -maxdepth 6 -name "pdf.py" -path "*pdf/scripts*"`。

```bash
PDF_SKILL_DIR=<pdf技能根目录>
python "$PDF_SKILL_DIR/scripts/pdf.py" env.check   # 缺 reportlab/pypdf 时: pip install reportlab pypdf pymupdf pikepdf pdfplumber

python "$PDF_SKILL_DIR/scripts/pdf.py" code.sanitize "C:/Users/guisu/.agents/skills/web-to-pdf/scripts/build_web_pdf.py"

python "C:/Users/guisu/.agents/skills/web-to-pdf/scripts/build_web_pdf.py" \
    --content content.json --out "构建智能体_中文版.pdf" --pdf-skill-dir "$PDF_SKILL_DIR"
```

脚本自动完成：调色板（未手写 palette 时）→ 正文（目录+页眉页脚+防孤行）
→ 封面渲染与合并 → 元数据写入。

### 5. 质量检查（必做）

```bash
F="<输出.pdf>"
python "$PDF_SKILL_DIR/scripts/pdf.py" meta.brand "$F"
python "$PDF_SKILL_DIR/scripts/pdf.py" font.check "$F"        # 期望 0 issues
python "$PDF_SKILL_DIR/scripts/pdf.py" toc.check "$F"         # 有目录时
python "$PDF_SKILL_DIR/scripts/pdf.py" pages.clean "$F" -o _clean.pdf   # 有空白页则替换
python "$PDF_SKILL_DIR/scripts/pdf_qa.py" --skip-cover "$F"
```

`pdf_qa` 的 FAIL 必须修复重建；WARN 中行首标点（"，"出现在行首）是
ReportLab CJK 换行的已知小瑕疵，非阻塞可接受，其余 WARN 酌情处理。

### 6. 视觉验收

把 PDF 按 ~130dpi 渲染成逐页 PNG（pymupdf `page.get_pixmap(dpi=130)`），
交给 `pdf:visual-judge` 子代理逐页判定（封面/目录/表格/插图/重叠/乱码），
全部 pass 才交付；有 fail 页按其证据修 content.json 重建。

### 7. 交付

向用户报告：文件路径、页数、大小、内容结构概览；中间产物
（body/cover/渲染 PNG）清理掉，保留 content.json 与脚本以便复用。

## 常见问题

- **构建报字体错误**：脚本 `FONT_CANDIDATES` 按优先级探测本机字体
  （Windows 微软雅黑/黑体/Times）。跨环境使用时在脚本顶部补充对应路径。
- **调色板生成失败**：pdf 技能缺失或升级换路径时，在 content.json 手写
  `palette`（5 个色值，见 schema）绕过自动生成。
- **表格溢出**：确认 `widths` 比例之和为 1，长文本列单元格会自动换行。
- **内容含 emoji**：本管线（ReportLab）会把 emoji 渲染成豆腐块。
  content.json 阶段就删除或改写为文字；用户坚持保留 emoji 时改走
  pdf 技能的 creative 路线（Playwright）。
