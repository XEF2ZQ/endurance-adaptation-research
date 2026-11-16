"""Build a typeset research PDF; render PNGs for visual quality assurance."""
import html
import re
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "pdf"
TMP = ROOT / "tmp" / "pdfs"


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"(https://[^\s<]+)", r'<a href="\1">\1</a>', text)
    return text


def markdown_to_html(markdown):
    lines = markdown.splitlines()
    result, i = [], 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("!["):
            result.append('<div class="figure"><img src="protocol_timing.png" width="480"/></div>')
            i += 1
        elif line.startswith("|"):
            table = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [x.strip() for x in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", x) for x in cells):
                    table.append(cells)
                i += 1
            result.append('<table>')
            for row_num, cells in enumerate(table):
                tag = "th" if row_num == 0 else "td"
                result.append('<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells) + '</tr>')
            result.append('</table>')
        elif line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            value = line[level:].strip()
            if value == "References":
                result.append('<div style="page-break-before:always"></div>')
            result.append(f'<h{level}>{inline(value)}</h{level}>')
            i += 1
        else:
            paragraph = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(("#", "|", "![")):
                paragraph.append(lines[i].strip())
                i += 1
            text = ' '.join(paragraph)
            css = ' class="reference"' if re.match(r"^\[\d+\]", text) else ''
            result.append(f'<p{css}>{inline(text)}</p>')
    return result


CSS = """
body {font-family: sans-serif; font-size:10pt; line-height:1.3; color:#203043; margin:0;}
h1 {font-size:27pt; line-height:1.1; color:#123a54; margin-top:0; margin-bottom:16pt;}
h2 {font-size:15pt; line-height:1.2; color:#123a54; margin-top:16pt; margin-bottom:8pt; page-break-after:avoid;}
h3 {font-size:11.5pt; color:#176b87; margin-top:11pt; margin-bottom:6pt; page-break-after:avoid;}
p {margin-top:0; margin-bottom:7pt; orphans:3; widows:3;}
table {border-collapse:collapse; width:100%; margin-top:10pt; margin-bottom:12pt; font-size:8.4pt;}
th {background-color:#e4eef3; color:#123a54; text-align:left; font-weight:bold;}
td, th {border-bottom:0.6pt solid #ccd7df; padding:6pt; vertical-align:top;}
tr {page-break-inside:avoid;}
a {color:#176b87; text-decoration:none;}
.reference {font-size:8.5pt; line-height:1.28; margin-bottom:10pt;}
.figure {margin-top:12pt; margin-bottom:12pt; page-break-inside:avoid;}
.keep {page-break-inside:avoid;}
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    svg = fitz.open(ROOT / "results" / "protocol_timing.svg")
    svg[0].get_pixmap(matrix=fitz.Matrix(1.7, 1.7)).save(TMP / "protocol_timing.png")
    raw_blocks = markdown_to_html((ROOT / "manuscript.md").read_text(encoding="utf-8"))
    # Tables are emitted as adjacent fragments by the small Markdown parser.
    blocks = []
    buffer = []
    for block in raw_blocks:
        if block == '<table>' or buffer:
            buffer.append(block)
            if block == '</table>':
                blocks.append(''.join(buffer))
                buffer = []
        else:
            blocks.append(block)
    assert not buffer
    (TMP / "article.html").write_text('\n'.join(blocks), encoding="utf-8")
    archive = fitz.Archive(str(TMP))
    page_rect = fitz.Rect(0, 0, 595.276, 841.89)
    content_rect = fitz.Rect(51, 57, 544.276, 785)
    def height(block):
        story = fitz.Story(html=block, user_css=CSS, archive=archive)
        more, filled = story.place(fitz.Rect(0, 0, content_rect.width, 4000))
        if more:
            raise ValueError('A block exceeds the measurement area')
        return fitz.Rect(filled).y1 + 1
    heights = [height(block) for block in blocks]
    doc = fitz.open()
    page = doc.new_page(width=page_rect.width, height=page_rect.height)
    y = content_rect.y0
    for i, (block, required) in enumerate(zip(blocks, heights)):
        if 'page-break-before:always' in block:
            if y > content_rect.y0:
                page = doc.new_page(width=page_rect.width, height=page_rect.height)
                y = content_rect.y0
            continue
        # Reserve the first paragraph with any immediately preceding headings.
        reserve = required
        if re.match(r'<h[123]>', block):
            j = i + 1
            while j < len(blocks) and re.match(r'<h[123]>', blocks[j]):
                reserve += heights[j]
                j += 1
            if j < len(blocks):
                reserve += heights[j]
        if y + reserve > content_rect.y1:
            page = doc.new_page(width=page_rect.width, height=page_rect.height)
            y = content_rect.y0
        if required > content_rect.height:
            raise ValueError('An indivisible block exceeds one page')
        rect = fitz.Rect(content_rect.x0, y, content_rect.x1, y + required)
        spare, scale = page.insert_htmlbox(rect, block, css=CSS, archive=archive, scale_low=1)
        if spare < 0 or scale != 1:
            raise ValueError(f'Block did not fit at original font size: {i}')
        y += required
    # Reopen the assembled pages before adding consistent page furniture.
    doc.save(TMP / 'layout.pdf', garbage=4, deflate=True)
    doc.close()
    doc = fitz.open(TMP / 'layout.pdf')
    for index, page in enumerate(doc):
        page.wrap_contents()
        page.draw_line((51, 39), (544, 39), color=(.65, .74, .79), width=.5)
        page.insert_text((51, 31), "ENDURANCE ADAPTATION | EVIDENCE AUDIT", fontsize=7, color=(.22, .35, .43))
        page.draw_line((51, 803), (544, 803), color=(.65, .74, .79), width=.5)
        page.insert_text((51, 818), "Version 1.0 | 16 November 2026 | Narrative review and computational methods", fontsize=7, color=(.32, .4, .46))
        page.insert_text((510, 818), str(index+1), fontsize=8, color=(.22, .35, .43))
    doc.set_metadata({"title":"Androgens, Estradiol and Subthreshold Endurance Adaptation",
                      "author":"Prepared for Peter Kosanyi; assisted by OpenAI Codex",
                      "subject":"Evidence audit and reproducible methods; no original human experiment",
                      "keywords":"testosterone, estradiol, subthreshold, endurance, critical power"})
    destination = OUT / "endurance_adaptation_review.pdf"
    doc.save(destination, garbage=4, deflate=True)
    for index, page in enumerate(doc):
        page.get_pixmap(matrix=fitz.Matrix(1.25, 1.25)).save(TMP / f"page-{index+1:02d}.png")
    print(f"Created {destination}; {len(doc)} pages; PyMuPDF {fitz.VersionBind}")


if __name__ == "__main__":
    main()
