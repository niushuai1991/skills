# -*- coding: utf-8 -*-
"""build_web_pdf.py — 把结构化内容(content.json)构建成带封面/目录的专业中文 PDF。

用法:
  python build_web_pdf.py --content content.json --out 最终.pdf --pdf-skill-dir <pdf技能根目录>
                          [--assets-dir assets] [--cover-template 01] [--no-cover] [--no-toc]

content.json 的格式见技能包 references/content-schema.md。
依赖: reportlab pypdf pymupdf(可选) + pdf 技能(用于封面渲染与字体回退)。
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, KeepTogether, CondPageBreak, HRFlowable,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from PIL import Image as PILImage

# --------------------------------------------------------------------------
# 字体候选（按优先级尝试，全部失败则报错）。跨环境使用时在此补充路径。
# 注册名保持与 pdf 技能 install_font_fallback 的 FONT_FALLBACK_CHAIN 一致。
# --------------------------------------------------------------------------
FONT_CANDIDATES = {
    "Microsoft YaHei": [("C:/Windows/Fonts/msyh.ttc", 0),
                        ("C:/Windows/Fonts/msyh.ttf", None),
                        ("/usr/share/fonts/truetype/chinese/msyh.ttf", None)],
    "Microsoft YaHei Bold": [("C:/Windows/Fonts/msyhbd.ttc", 0),
                             ("/usr/share/fonts/truetype/chinese/msyhbd.ttf", None)],
    "SimHei": [("C:/Windows/Fonts/simhei.ttf", None),
               ("/usr/share/fonts/truetype/chinese/SimHei.ttf", None)],
    "Times New Roman": [("C:/Windows/Fonts/times.ttf", None),
                        ("/usr/share/fonts/truetype/english/Times-New-Roman.ttf", None)],
    "Times New Roman Bold": [("C:/Windows/Fonts/timesbd.ttf", None),
                             ("/usr/share/fonts/truetype/english/Times-New-Roman-Bold.ttf", None)],
}
REQUIRED_FONTS = ["Microsoft YaHei", "Microsoft YaHei Bold", "SimHei",
                  "Times New Roman", "Times New Roman Bold"]

CN = "Microsoft YaHei"
EN = "Times New Roman"

# 裸 & 转义（保留已有实体与用户写的标记）
_AMP_RE = re.compile(r"&(?!(amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)")


def esc(text):
    return _AMP_RE.sub("&amp;", text)


def register_fonts():
    missing = []
    for name in REQUIRED_FONTS:
        for path, idx in FONT_CANDIDATES[name]:
            if not os.path.exists(path):
                continue
            try:
                if idx is None:
                    pdfmetrics.registerFont(TTFont(name, path))
                else:
                    pdfmetrics.registerFont(TTFont(name, path, subfontIndex=idx))
                break
            except Exception:
                continue
        else:
            missing.append(name)
    if "Microsoft YaHei" in missing and "SimHei" not in missing:
        # 用 SimHei 顶替雅黑（覆盖候选名），保持回退链可用
        pass
    if missing:
        raise RuntimeError(
            "以下字体注册失败: %s\n请在 build_web_pdf.py 的 FONT_CANDIDATES 中"
            "补充本机可用的中/英文字体路径。" % ", ".join(missing))
    registerFontFamily("Microsoft YaHei", normal="Microsoft YaHei",
                       bold="Microsoft YaHei Bold",
                       italic="Microsoft YaHei", boldItalic="Microsoft YaHei Bold")
    registerFontFamily("SimHei", normal="SimHei", bold="SimHei")
    registerFontFamily("Times New Roman", normal="Times New Roman",
                       bold="Times New Roman Bold",
                       italic="Times New Roman", boldItalic="Times New Roman Bold")


def resolve_palette(spec, title, skill_dir):
    """palette 优先用 content.json 里给的，否则调 pdf 技能的 palette.generate。"""
    if spec:
        return {
            "ACCENT": colors.HexColor(spec.get("accent", "#b55333")),
            "TEXT_PRIMARY": colors.HexColor(spec.get("text", "#1c1e1f")),
            "TEXT_MUTED": colors.HexColor(spec.get("muted", "#6f757a")),
            "BG_SURFACE": colors.HexColor(spec.get("mid", "#e0e4e7")),
            "BG_PAGE": colors.HexColor(spec.get("bg", "#ffffff")),
        }
    script = os.path.join(skill_dir, "scripts", "pdf.py")
    try:
        out = subprocess.run(
            [sys.executable, script, "palette.generate",
             "--title", title, "--mode", "minimal", "--format", "json"],
            capture_output=True, text=True, timeout=60, check=True).stdout
        p = json.loads(out)
        return {
            "ACCENT": colors.HexColor(p["accent"]),
            "TEXT_PRIMARY": colors.HexColor(p["text"]),
            "TEXT_MUTED": colors.HexColor(p["muted"]),
            "BG_SURFACE": colors.HexColor(p.get("mid", "#e0e4e7")),
            "BG_PAGE": colors.HexColor(p.get("bg", "#ffffff")),
        }
    except Exception as e:
        raise RuntimeError("自动生成调色板失败(可在 content.json 手写 palette): %s" % e)


class Builder:
    def __init__(self, content, assets_dir, skill_dir, cover_template, use_cover, use_toc):
        self.content = content
        self.assets_dir = os.path.abspath(assets_dir)
        self.skill_dir = skill_dir
        self.cover_template = cover_template
        self.use_cover = use_cover
        self.use_toc = use_toc
        self.lang = content.get("language", "zh")

        self.pal = resolve_palette(content.get("palette"), content.get("title", "文档"),
                                   skill_dir)
        self._make_styles()

        self.page_w, self.page_h = A4
        self.margin_lr = content.get("margin_cm", 2.0) * cm
        self.margin_top = self.margin_lr + 0.3 * cm
        self.margin_bottom = self.margin_lr + 0.1 * cm
        self.avail_w = self.page_w - 2 * self.margin_lr
        self.h1_orphan = (self.page_h - self.margin_top - self.margin_bottom) * 0.15
        self.max_keep = self.page_h * 0.4

    # ------------------------------------------------------------- styles
    def _make_styles(self):
        p = self.pal
        self.s_h1 = ParagraphStyle("H1", fontName=CN, fontSize=18, leading=26,
                                   textColor=p["TEXT_PRIMARY"], spaceBefore=18,
                                   spaceAfter=6, wordWrap="CJK")
        self.s_h2 = ParagraphStyle("H2", fontName=CN, fontSize=14, leading=21,
                                   textColor=p["TEXT_PRIMARY"], spaceBefore=16,
                                   spaceAfter=8, wordWrap="CJK")
        self.s_h3 = ParagraphStyle("H3", fontName=CN, fontSize=11.5, leading=17,
                                   textColor=p["TEXT_PRIMARY"], spaceBefore=12,
                                   spaceAfter=6, wordWrap="CJK")
        body_kw = dict(fontName=CN, fontSize=10.5, leading=18,
                       textColor=p["TEXT_PRIMARY"], alignment=TA_LEFT,
                       wordWrap="CJK", spaceBefore=0, spaceAfter=8)
        self.s_body = ParagraphStyle("Body", firstLineIndent=21, **body_kw)
        self.s_body_ni = ParagraphStyle("BodyNI", firstLineIndent=0, **body_kw)
        self.s_bullet = ParagraphStyle("Bullet", parent=self.s_body_ni,
                                       leftIndent=16, spaceBefore=1, spaceAfter=3,
                                       leading=17)
        self.s_number = ParagraphStyle("Numbered", parent=self.s_body_ni,
                                       leftIndent=18, spaceBefore=1, spaceAfter=3,
                                       leading=17)
        self.s_quote = ParagraphStyle("Quote", parent=self.s_body_ni)
        self.s_note = ParagraphStyle("Note", fontName=CN, fontSize=9, leading=15,
                                     textColor=p["TEXT_MUTED"], alignment=TA_LEFT,
                                     wordWrap="CJK")
        self.s_caption = ParagraphStyle("Caption", fontName=CN, fontSize=8.5,
                                        leading=13, textColor=p["TEXT_MUTED"],
                                        alignment=TA_CENTER, wordWrap="CJK",
                                        spaceBefore=6, spaceAfter=6)
        self.s_toc_title = ParagraphStyle("TocTitle", fontName=CN, fontSize=20,
                                          leading=28, textColor=p["TEXT_PRIMARY"],
                                          spaceAfter=14, wordWrap="CJK")
        self.s_th = ParagraphStyle("TblHeader", fontName=CN, fontSize=10.5, leading=15,
                                   textColor=colors.white, alignment=TA_LEFT,
                                   wordWrap="CJK")
        self.s_td = ParagraphStyle("TblCell", fontName=CN, fontSize=10, leading=15,
                                   textColor=p["TEXT_PRIMARY"], alignment=TA_LEFT,
                                   wordWrap="CJK")

    # ------------------------------------------------------------ helpers
    def _keep(self, elements):
        total = 0
        for el in elements:
            _, h = el.wrap(self.avail_w, self.page_h)
            total += h
        if total <= self.max_keep:
            return [KeepTogether(elements)]
        if len(elements) >= 2:
            return [KeepTogether(elements[:2])] + list(elements[2:])
        return list(elements)

    def _heading(self, text, style, level):
        key = "h_" + hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
        p = Paragraph('<a name="%s"/><b>%s</b>' % (key, esc(text)), style)
        p.bookmark_name = text
        p.bookmark_level = level
        p.bookmark_text = text
        p.bookmark_key = key
        return p

    def _callout(self, text, border, bg, style):
        t = Table([[Paragraph(esc(text), style)]],
                  colWidths=[self.avail_w * 0.96], hAlign="CENTER")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("LINEBEFORE", (0, 0), (0, -1), 3, border),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        return t

    def _image(self, path, max_h, max_w=None):
        if not os.path.isabs(path):
            path = os.path.join(self.assets_dir, path)
        if not os.path.exists(path):
            raise FileNotFoundError("图片不存在: %s" % path)
        max_w = max_w or self.avail_w
        max_h = max_h or self.page_h * 0.33
        ow, oh = PILImage.open(path).size
        ratio = min(max_w / ow if ow > max_w else 1.0,
                    max_h / oh if oh > max_h else 1.0)
        img = Image(path, width=ow * ratio, height=oh * ratio)
        img.hAlign = "CENTER"
        return img

    # ------------------------------------------------------------- blocks
    def block(self, b):
        t = b.get("type")
        if t == "h1":
            rule = HRFlowable(width="100%", thickness=1.2, color=self.pal["ACCENT"],
                              spaceBefore=0, spaceAfter=10)
            items = [self._heading(b["text"], self.s_h1, 0), rule]
            if b.get("lead"):
                items.append(Paragraph(esc(b["lead"]), self.s_body))
            return [CondPageBreak(self.h1_orphan)] + self._keep(items)
        if t == "h2":
            items = [self._heading(b["text"], self.s_h2, 1)]
            if b.get("lead"):
                items.append(Paragraph(esc(b["lead"]), self.s_body))
            return self._keep(items)
        if t == "h3":
            items = [Paragraph("<b>%s</b>" % esc(b["text"]), self.s_h3)]
            if b.get("lead"):
                items.append(Paragraph(esc(b["lead"]), self.s_body))
            return self._keep(items)
        if t == "para":
            style = self.s_body if b.get("indent", True) else self.s_body_ni
            return [Paragraph(esc(b["text"]), style)]
        if t == "bullets":
            return [Paragraph("• " + esc(i), self.s_bullet) for i in b["items"]]
        if t == "numbered":
            return [Paragraph("%d. %s" % (n + 1, esc(i)), self.s_number)
                    for n, i in enumerate(b["items"])]
        if t == "callout":
            return [Spacer(1, 4),
                    self._callout(b["text"], self.pal["ACCENT"], self.pal["BG_SURFACE"],
                                  self.s_quote),
                    Spacer(1, 8)]
        if t == "note":
            return [Spacer(1, 4),
                    self._callout(b["text"], self.pal["TEXT_MUTED"],
                                  colors.Color(0.96, 0.96, 0.97), self.s_note),
                    Spacer(1, 8)]
        if t == "table":
            return self._table(b)
        if t == "image":
            img = self._image(b["file"], b.get("max_height"))
            out = [Spacer(1, 10)]
            if b.get("caption"):
                out += self._keep([img, Paragraph(esc(b["caption"]), self.s_caption),
                                   Spacer(1, 8)])
            else:
                out += [img, Spacer(1, 8)]
            return out
        if t == "hr":
            color = (self.pal["ACCENT"] if b.get("style") == "accent"
                     else self.pal["TEXT_MUTED"])
            alpha = 1.0 if b.get("style") == "accent" else 0.4
            c = colors.Color(color.red, color.green, color.blue, alpha=alpha)
            return [HRFlowable(width="100%", thickness=b.get("thickness", 0.5),
                               color=c, spaceBefore=6, spaceAfter=8)]
        if t == "spacer":
            return [Spacer(1, b.get("height", 12))]
        if t == "pagebreak":
            return [PageBreak()]
        raise ValueError("未知块类型: %s" % t)

    def _table(self, b):
        headers = b.get("headers")
        rows = b["rows"]
        ncol = len(rows[0])
        widths = b.get("widths") or [1.0 / ncol] * ncol
        total = self.avail_w * b.get("width_ratio", 0.96)
        col_w = [w * total for w in widths]
        data = []
        if headers:
            data.append([Paragraph("<b>%s</b>" % esc(h), self.s_th) for h in headers])
        for r in rows:
            data.append([Paragraph(esc(c), self.s_td) for c in r])
        tbl = Table(data, colWidths=col_w, hAlign="CENTER", repeatRows=1 if headers else 0)
        style = [
            ("GRID", (0, 0), (-1, -1), 0.5, self.pal["TEXT_MUTED"]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
        if headers:
            style.append(("BACKGROUND", (0, 0), (-1, 0), self.pal["ACCENT"]))
            start = 1
        else:
            start = 0
        for i in range(start, len(data)):
            bg = colors.white if (i - start) % 2 == 0 else self.pal["BG_SURFACE"]
            style.append(("BACKGROUND", (0, i), (-1, i), bg))
        tbl.setStyle(TableStyle(style))
        out = [Spacer(1, 10), tbl]
        if b.get("caption"):
            out += [Spacer(1, 4), Paragraph(esc(b["caption"]), self.s_caption)]
        out.append(Spacer(1, 12))
        return out

    # ------------------------------------------------------- page furniture
    def _before_page(self, c):
        p = self.pal
        c.saveState()
        header = self.content.get("header_text", self.content.get("title", ""))
        if header:
            c.setFont(CN, 7.5)
            c.setFillColor(p["TEXT_MUTED"])
            c.drawString(self.margin_lr, self.page_h - 1.35 * cm, header)
            c.setStrokeColor(p["ACCENT"])
            c.setStrokeAlpha(0.35)
            c.setLineWidth(1.2)
            c.line(self.margin_lr, self.page_h - 1.55 * cm,
                   self.page_w - self.margin_lr, self.page_h - 1.55 * cm)
        c.setStrokeColor(p["TEXT_MUTED"])
        c.setStrokeAlpha(0.35)
        c.setLineWidth(0.5)
        c.line(self.margin_lr, 1.45 * cm, self.page_w - self.margin_lr, 1.45 * cm)
        c.setFont(CN, 7.5)
        c.setFillColor(p["TEXT_MUTED"])
        footer = self.content.get("footer_text", "")
        if footer:
            c.drawString(self.margin_lr, 1.05 * cm, footer)
        c.drawRightString(self.page_w - self.margin_lr, 1.05 * cm,
                          "第 %d 页" % c.getPageNumber())
        c.restoreState()

    # ---------------------------------------------------------------- build
    def build_body(self, out_path):
        class Doc(SimpleDocTemplate):
            builder = self

            def afterFlowable(self, flowable):
                if hasattr(flowable, "bookmark_name"):
                    level = getattr(flowable, "bookmark_level", 0)
                    text = getattr(flowable, "bookmark_text", "")
                    key = getattr(flowable, "bookmark_key", "")
                    self.notify("TOCEntry", (level, text, self.page, key))
                    try:
                        self.canv.addOutlineEntry(text, key, level=level, closed=False)
                    except Exception:
                        pass

            def beforePage(self):
                self.builder._before_page(self.canv)

        story = []
        if self.use_toc:
            toc = TableOfContents()
            toc.dotsMinLevel = 0
            toc.levelStyles = [
                ParagraphStyle("TOC1", fontName=CN, fontSize=11.5, leading=20,
                               leftIndent=6, textColor=self.pal["TEXT_PRIMARY"],
                               wordWrap="CJK"),
                ParagraphStyle("TOC2", fontName=CN, fontSize=10, leading=17,
                               leftIndent=26, textColor=self.pal["TEXT_MUTED"],
                               wordWrap="CJK"),
            ]
            toc_title = self.content.get("toc_title",
                                         "目录" if self.lang == "zh" else "Contents")
            story.append(Paragraph("<b>%s</b>" % esc(toc_title), self.s_toc_title))
            story.append(HRFlowable(width="100%", thickness=1.2,
                                    color=self.pal["ACCENT"],
                                    spaceBefore=0, spaceAfter=12))
            story.append(toc)
            story.append(PageBreak())

        for b in self.content.get("blocks", []):
            story.extend(self.block(b))

        doc = Doc(out_path, pagesize=A4,
                  leftMargin=self.margin_lr, rightMargin=self.margin_lr,
                  topMargin=self.margin_top, bottomMargin=self.margin_bottom,
                  title=self.content.get("title", "文档"),
                  author=self.content.get("author", "Z.ai"),
                  creator=self.content.get("author", "Z.ai"),
                  subject=self.content.get("subject", ""))
        doc.multiBuild(story)


def make_cover_and_merge(content, body_pdf, final_pdf, skill_dir, template):
    sys.path.insert(0, os.path.join(skill_dir, "scripts"))
    from pypdf import PdfReader, PdfWriter, Transformation
    from cover_render import render_cover, detect_fonts

    cover_spec = content.get("cover")
    final_dir = os.path.dirname(os.path.abspath(final_pdf))
    cover_pdf = os.path.join(final_dir, "_cover_tmp.pdf")
    pal = content.get("palette") or {}
    cover_palette = {
        "primary": pal.get("accent", "#b55333"),
        "text": pal.get("text", "#1c1e1f"),
        "muted": pal.get("muted", "#6f757a"),
        "bg": pal.get("bg", "#ffffff"),
    }
    fonts = detect_fonts()
    render_cover(template, cover_spec, cover_pdf, palette=cover_palette, fonts=fonts)

    a4_w, a4_h = 595.28, 841.89

    def norm(page):
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        if abs(w - a4_w) > 2 or abs(h - a4_h) > 2:
            page.add_transformation(
                Transformation().scale(sx=a4_w / w, sy=a4_h / h))
            page.mediabox.lower_left = (0, 0)
            page.mediabox.upper_right = (a4_w, a4_h)
        return page

    writer = PdfWriter()
    writer.add_page(norm(PdfReader(cover_pdf).pages[0]))
    for page in PdfReader(body_pdf).pages:
        writer.add_page(norm(page))
    writer.add_metadata({
        "/Title": content.get("title", "文档"),
        "/Author": content.get("author", "Z.ai"),
        "/Creator": content.get("author", "Z.ai"),
        "/Subject": content.get("subject", ""),
    })
    with open(final_pdf, "wb") as f:
        writer.write(f)
    os.remove(cover_pdf)


def main():
    ap = argparse.ArgumentParser(description="content.json -> 专业中文 PDF")
    ap.add_argument("--content", required=True, help="内容 JSON 文件路径")
    ap.add_argument("--out", required=True, help="输出 PDF 路径")
    ap.add_argument("--pdf-skill-dir", required=True,
                    help="pdf 技能根目录(含 scripts/pdf.py、scripts/cover_render.py)")
    ap.add_argument("--assets-dir", default=None,
                    help="图片资产目录(默认: content.json 同级的 assets/)")
    ap.add_argument("--cover-template", default=None,
                    help="封面模板编号 01-09(默认取 content.cover.template 或 01)")
    ap.add_argument("--no-cover", action="store_true", help="不生成封面")
    ap.add_argument("--no-toc", action="store_true", help="不生成目录")
    args = ap.parse_args()

    register_fonts()
    sys.path.insert(0, os.path.join(args.pdf_skill_dir, "scripts"))
    from pdf import install_font_fallback  # noqa: E402  (pdf 技能辅助函数)
    install_font_fallback()

    with open(args.content, encoding="utf-8") as f:
        content = json.load(f)

    content_dir = os.path.dirname(os.path.abspath(args.content))
    assets_dir = args.assets_dir or os.path.join(content_dir, "assets")
    use_cover = (not args.no_cover) and bool(content.get("cover"))
    template = (args.cover_template or (content.get("cover") or {}).get("template", "01"))
    use_toc = (not args.no_toc) and content.get("toc", True)

    builder = Builder(content, assets_dir, args.pdf_skill_dir,
                      template, use_cover, use_toc)

    with tempfile.TemporaryDirectory(prefix="webpdf_") as td:
        body_pdf = os.path.join(td, "body.pdf")
        builder.build_body(body_pdf)
        if use_cover:
            make_cover_and_merge(content, body_pdf, args.out,
                                 args.pdf_skill_dir, template)
        else:
            import shutil
            shutil.copyfile(body_pdf, args.out)

    size_kb = os.path.getsize(args.out) / 1024
    print("OK: %s (%.0f KB)" % (os.path.abspath(args.out), size_kb))


if __name__ == "__main__":
    main()
