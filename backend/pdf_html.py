"""
pdf_html.py
───────────
PDF via WeasyPrint (HTML → PDF with Pango/HarfBuzz shaping), so Telugu,
Tamil, Kannada and Devanagari conjuncts render correctly. Needs the Noto
fonts installed on the system (apt: fonts-noto-core).
"""
import html, os, re, tempfile
from datetime import datetime

FONTS = ("'Noto Sans', 'Noto Sans Telugu', 'Noto Sans Tamil', 'Noto Sans Kannada', "
         "'Noto Sans Devanagari', 'Noto Serif Devanagari', sans-serif")

CSS = f"""
@page {{ size: A4; margin: 18mm 18mm 16mm; }}
body {{ font-family: {FONTS}; color: #1a1a1a; font-size: 10.5pt; line-height: 1.75; }}
h1 {{ color: #8b0000; text-align: center; font-size: 20pt; margin: 6px 0 2px; font-weight: 600; }}
.brand {{ text-align: center; color: #8b0000; font-size: 9.5pt; font-style: italic; letter-spacing: 1px; margin-bottom: 4px; }}
.sub {{ text-align: center; color: #5c3317; font-size: 9.5pt; margin-bottom: 10px; }}
hr.top {{ border: 0; border-top: 3px solid #8b0000; margin: 0 0 8px; }}
hr {{ border: 0; border-top: 1px solid #deb887; margin: 12px 0; }}
h2 {{ color: #8b0000; font-size: 11.5pt; margin: 14px 0 6px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 9.5pt; }}
td {{ border: 0.5pt solid #deb887; padding: 4px 8px; line-height: 1.4; }}
td.k {{ width: 30%; background: #fff8dc; color: #5c3317; }}
td.v {{ background: #fffff0; }}
.dev td {{ border-color: #a5d6a7; }} .dev td.k {{ background: #e8f5e9; }} .dev td.v {{ background: #f1f8e9; }}
.text {{ text-align: justify; white-space: pre-wrap; font-size: 11pt; }}
.sankalpam {{ border: 1px solid #deb887; background: #fffdf6; padding: 10px 14px; border-radius: 6px; }}
.foot {{ text-align: center; color: #777; font-size: 8pt; margin-top: 14px; }}
.bless {{ text-align: center; color: #8b0000; font-size: 10pt; }}
"""


def available() -> bool:
    try:
        import weasyprint  # noqa: F401
        return True
    except Exception:
        return False


def create_pdf(sankalpam_text, form_data, panchang, language="english") -> str:
    from weasyprint import HTML

    e = lambda s: html.escape(str(s or "—"))
    parts = re.split(r"\s*━{5,}\s*", sankalpam_text, maxsplit=1)
    verses, meaning = parts[0], (parts[1] if len(parts) > 1 else "")
    rows = lambda pairs: "".join(f"<tr><td class='k'>{e(k)}</td><td class='v'>{e(v)}</td></tr>" for k, v in pairs)

    pan = rows([
        ("Samvatsara", panchang.get("samvatsara")), ("Ayana", panchang.get("ayana")),
        ("Ritu", f"{panchang.get('ritu', '')} ({panchang.get('ritu_english', '')})"),
        ("Masa", panchang.get("masa")), ("Paksha", panchang.get("paksha")),
        ("Tithi", panchang.get("tithi")), ("Vara", f"{panchang.get('vara', '')} / {panchang.get('vara_english', '')}"),
        ("Nakshatra", f"{panchang.get('nakshatra', '')} (pada {panchang.get('nakshatra_pada', '—')})"),
        ("Yoga", panchang.get("yoga")), ("Karana", panchang.get("karana")),
    ])
    dev = rows([
        ("Name", form_data.get("name")), ("Gothram", form_data.get("gothram")),
        ("Dharma Patni", form_data.get("dharma_patni_name")),
        ("Family members", form_data.get("other_members")),
        ("Location", ", ".join(filter(None, [form_data.get("city"), form_data.get("state"), form_data.get("country")]))),
    ])
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<hr class="top"><h1>ॐ Sankalpam</h1>
<div class="brand">by Velvue</div>
<div class="sub">{e(form_data.get('pooja_name'))} | {e(language.title())} | {e(form_data.get('date'))} {e(form_data.get('time'))}</div>
<hr>
<h2>Panchang Details</h2><table>{pan}</table>
<h2>Devotee Details</h2><table class="dev">{dev}</table>
<h2>Sankalpam ({e(language.title())})</h2>
<div class="sankalpam text">{html.escape(verses)}</div>
{f'<h2>Meaning</h2><div class="text">{html.escape(meaning)}</div>' if meaning else ''}
<hr><div class="foot">Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')} | Sankalpam Generator by Velvue · sankalpam-generator.velvue.in</div>
<div class="bless">॥ शुभं भवतु ॥ May all be auspicious</div>
</body></html>"""
    fd, path = tempfile.mkstemp(prefix="sankalpam_", suffix=".pdf")
    os.close(fd)
    HTML(string=doc).write_pdf(path)
    return path
