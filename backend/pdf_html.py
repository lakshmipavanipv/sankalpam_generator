"""
pdf_html.py
───────────
PDF via WeasyPrint (HTML → PDF with Pango/HarfBuzz shaping), so Telugu,
Tamil, Kannada and Devanagari conjuncts render correctly. Needs the Noto
fonts installed on the system (apt: fonts-noto-core).

Layout: page 1 holds the header, the panchang and devotee details side by
side, and the sankalpam itself (kept in one piece); the meaning follows.
"""
import html, os, re, tempfile
from datetime import datetime

FONTS = ("'Noto Sans', 'Noto Sans Telugu', 'Noto Sans Tamil', 'Noto Sans Kannada', "
         "'Noto Sans Devanagari', 'Noto Serif Devanagari', sans-serif")

CSS = f"""
@page {{
  size: A4; margin: 13mm 16mm 16mm;
  @bottom-left {{ content: "Sankalpam Generator by Velvue · sankalpam-generator.velvue.in";
                  font-family: {FONTS}; font-size: 7.5pt; color: #999; }}
  @bottom-right {{ content: "Page " counter(page) " of " counter(pages);
                   font-family: {FONTS}; font-size: 7.5pt; color: #999; }}
}}
body {{ font-family: {FONTS}; color: #1a1a1a; font-size: 10.5pt; line-height: 1.7; margin: 0; }}
.head {{ text-align: center; border-top: 3px solid #8b0000; border-bottom: 1px solid #deb887;
         padding: 4px 0 6px; margin-bottom: 10px; }}
h1 {{ color: #8b0000; font-size: 20pt; margin: 0; font-weight: 700; line-height: 1.3; }}
.brand {{ color: #8b0000; font-size: 9.5pt; font-style: italic; letter-spacing: 1px; }}
.brand b {{ font-style: normal; letter-spacing: 2px; }}
.brand .logo {{ height: 13pt; vertical-align: middle; margin: 0 4px 2px 5px; }}
.sub {{ color: #5c3317; font-size: 9.5pt; margin-top: 4px; }}
h2 {{ color: #8b0000; font-size: 11pt; margin: 0 0 5px; break-after: avoid; }}
.grid {{ display: flex; gap: 10px; margin-bottom: 14px; break-inside: avoid; }}
.grid > div {{ flex: 1; }}
table {{ width: 100%; border-collapse: collapse; font-size: 8.8pt; }}
td {{ border: 0.5pt solid #deb887; padding: 2px 7px; line-height: 1.3; vertical-align: top; }}
td.k {{ width: 34%; background: #fff8dc; color: #5c3317; }}
td.v {{ background: #fffff0; }}
.dev td {{ border-color: #a5d6a7; }} .dev td.k {{ background: #e8f5e9; }} .dev td.v {{ background: #f1f8e9; }}
.sankalpam {{ border: 1px solid #deb887; border-left: 4px solid #8b0000; background: #fffdf6;
              padding: 9px 14px; border-radius: 4px; text-align: left; font-size: 10.5pt;
              line-height: 1.7; break-inside: avoid; box-decoration-break: clone;
              -webkit-box-decoration-break: clone; margin-bottom: 14px; }}
.sankalpam p {{ margin: 0 0 6px; }} .sankalpam p:last-child {{ margin: 0; }}
.meaning p {{ margin: 0 0 7px; text-align: left; font-size: 10pt; line-height: 1.6;
              orphans: 3; widows: 3; }}
.meaning b {{ color: #8b0000; }}
.bless {{ text-align: center; color: #8b0000; font-size: 10pt; margin-top: 8px;
          border-top: 1px solid #deb887; padding-top: 5px; line-height: 1.4; break-inside: avoid; }}
.gen {{ text-align: center; color: #888; font-size: 7.5pt; }}
"""

_LABEL = re.compile(r"^\s*([^\s—][^—\n]{0,24}?)\s*—\s*")


LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "velvue-logo.png")


def _logo_tag() -> str:
    """Inline Velvue logo (data URI) or nothing if the file is missing."""
    try:
        import base64
        with open(LOGO, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode()
        return f'<img class="logo" src="data:image/png;base64,{b64}" alt="Velvue">'
    except OSError:
        return ""


def available() -> bool:
    try:
        import weasyprint  # noqa: F401
        return True
    except Exception:
        return False


def _paras(text: str) -> list[str]:
    """Split into paragraphs; single newlines inside a paragraph become spaces."""
    out = []
    for p in re.split(r"\n\s*\n", text.strip()):
        p = re.sub(r"[ \t]*\n[ \t]*", " ", p).strip()
        p = re.sub(r"[ \t]{2,}", " ", p)
        if p:
            out.append(p)
    return out


def create_pdf(sankalpam_text, form_data, panchang, language="english") -> str:
    from weasyprint import HTML

    e = lambda s: html.escape(str(s if s not in (None, "") else "—"))
    parts = re.split(r"\s*━{5,}\s*", sankalpam_text, maxsplit=1)
    verses, meaning = parts[0], (parts[1] if len(parts) > 1 else "")
    rows = lambda pairs: "".join(f"<tr><td class='k'>{e(k)}</td><td class='v'>{e(v)}</td></tr>" for k, v in pairs)

    pada = panchang.get("nakshatra_pada")
    pan = rows([
        ("Samvatsara", panchang.get("samvatsara")), ("Ayana", panchang.get("ayana")),
        ("Ritu", f"{panchang.get('ritu', '')} ({panchang.get('ritu_english', '')})"),
        ("Masa", panchang.get("masa")), ("Paksha", panchang.get("paksha")),
        ("Tithi", panchang.get("tithi")),
        ("Vara", f"{panchang.get('vara', '')} / {panchang.get('vara_english', '')}"),
        ("Nakshatra", f"{panchang.get('nakshatra', '')}" + (f" (pada {pada})" if pada else "")),
        ("Yoga", panchang.get("yoga")), ("Karana", panchang.get("karana")),
    ])
    dev = rows([
        ("Name", form_data.get("name")), ("Gothram", form_data.get("gothram")),
        ("Dharma Patni", form_data.get("dharma_patni_name")),
        ("Family members", form_data.get("other_members")),
        ("City", form_data.get("city")), ("State", form_data.get("state")),
        ("Country", form_data.get("country")),
        ("Date & time", f"{form_data.get('date', '')} {form_data.get('time', '')}".strip()),
    ])

    verse_html = "".join(f"<p>{html.escape(p)}</p>" for p in _paras(verses))
    meaning_html = ""
    for p in _paras(meaning):
        m = _LABEL.match(p)
        if m:
            p_html = f"<b>{html.escape(m.group(1))} —</b> {html.escape(p[m.end():])}"
        else:
            p_html = html.escape(p)
        meaning_html += f"<p>{p_html}</p>"

    lang = e(language.title())
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="head">
  <h1>ॐ Sankalpam</h1>
  <div class="brand">by {_logo_tag()}<b>VELVUE</b></div>
  <div class="sub">{e(form_data.get('pooja_name'))} · {lang} · {e(form_data.get('date'))}</div>
</div>
<div class="grid">
  <div><h2>Panchang</h2><table>{pan}</table></div>
  <div><h2>Devotee</h2><table class="dev">{dev}</table></div>
</div>
<h2>Sankalpam ({lang})</h2>
<div class="sankalpam">{verse_html}</div>
{f'<div class="meaning">{meaning_html}</div>' if meaning_html else ''}
<div class="bless">॥ शुभं भवतु ॥ May all be auspicious
  <div class="gen">Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}</div></div>
</body></html>"""
    fd, path = tempfile.mkstemp(prefix="sankalpam_", suffix=".pdf")
    os.close(fd)
    HTML(string=doc).write_pdf(path)
    return path
