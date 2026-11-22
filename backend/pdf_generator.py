"""
pdf_generator.py (v4)
─────────────────────
Generates Sankalpam PDF. Downloads NotoSans TTF if not cached
so Telugu/Sanskrit glyphs render correctly on Windows too.
"""
import os, logging, tempfile
from datetime import datetime
logger = logging.getLogger(__name__)

FONT_CACHE = os.path.join(tempfile.gettempdir(), "sankalpam_fonts")

# Noto fonts that cover Devanagari + Telugu + Tamil + Kannada
NOTO_FONTS = [
    ("NotoSans",   "https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"),
    ("NotoTelugu", "https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSansTelugu/NotoSansTelugu-Regular.ttf"),
]


class PDFGenerator:

    def __init__(self):
        self.output_dir = tempfile.gettempdir()
        os.makedirs(FONT_CACHE, exist_ok=True)

    def create_pdf(self, sankalpam_text, form_data, panchang, language="english"):
        # Preferred: WeasyPrint shapes Indic scripts correctly (ReportLab cannot)
        import pdf_html
        if pdf_html.available():
            return pdf_html.create_pdf(sankalpam_text, form_data, panchang, language)
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.platypus import (SimpleDocTemplate, Paragraph,
                                            Spacer, Table, TableStyle, HRFlowable)
            from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

            safe  = (form_data.get("name") or "user").replace(" ","_").replace("/","_")
            date  = form_data.get("date","today")
            path  = os.path.join(self.output_dir, f"sankalpam_{safe}_{date}.pdf")

            doc = SimpleDocTemplate(path, pagesize=A4,
                rightMargin=2*cm, leftMargin=2*cm,
                topMargin=2*cm, bottomMargin=2*cm)

            font = self._get_font(language)

            def mk(name, size, color="#1a1a1a", align=TA_JUSTIFY, after=6):
                return ParagraphStyle(name, fontName=font, fontSize=size,
                    textColor=colors.HexColor(color), alignment=align,
                    spaceAfter=after, leading=int(size*1.7))

            title_s  = mk("TT", 20, "#8B0000", TA_CENTER, 4)
            sub_s    = mk("SS", 10, "#5C3317", TA_CENTER, 3)
            sec_s    = mk("HH", 11, "#8B0000", TA_JUSTIFY, 4)
            body_s   = mk("BB", 11, "#1a1a1a", TA_JUSTIFY, 4)
            small_s  = mk("SM",  8, "#777777", TA_CENTER,  2)
            ctr_s    = mk("CC", 10, "#8B0000", TA_CENTER,  2)

            story = []
            HR = lambda thick=1, color="#DEB887", before=0, after=8: \
                HRFlowable(width="100%", thickness=thick,
                           color=colors.HexColor(color),
                           spaceBefore=before, spaceAfter=after)

            story.append(HR(3,"#8B0000",0,8))
            story.append(Paragraph("Om Shri Maha Vishnu Rajnaya", title_s))
            story.append(Paragraph("Sankalpam", title_s))
            story.append(Paragraph(
                f"{form_data.get('pooja_name','Pooja')} | "
                f"Language: {language.title()} | Date: {date}", sub_s))
            story.append(HR(1,"#DEB887",0,10))

            # Panchang table
            story.append(Paragraph("Panchang Details", sec_s))
            pan_rows = [
                ["Samvatsara", panchang.get("samvatsara","—")],
                ["Ayana",      panchang.get("ayana","—")],
                ["Ritu",       f"{panchang.get('ritu','')} ({panchang.get('ritu_english','')})"],
                ["Masa",       panchang.get("masa","—")],
                ["Paksha",     panchang.get("paksha","—")],
                ["Tithi",      panchang.get("tithi","—")],
                ["Vara",       f"{panchang.get('vara','')} / {panchang.get('vara_english','')}"],
                ["Nakshatra",  panchang.get("nakshatra","—")],
                ["Yoga",       panchang.get("yoga","—")],
                ["Karana",     panchang.get("karana","—")],
            ]
            # Convert table cell text to Paragraph so font is applied
            pan_data = [[Paragraph(str(r[0]), mk("pc",9,"#5C3317",after=0)),
                         Paragraph(str(r[1]), mk("pv",9,"#1a1a1a",after=0))]
                        for r in pan_rows]
            pt = Table(pan_data, colWidths=[4.5*cm, 11*cm])
            pt.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#FFF8DC")),
                ("BACKGROUND",(1,0),(1,-1),colors.HexColor("#FFFFF0")),
                ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#DEB887")),
                ("TOPPADDING",(0,0),(-1,-1),5),
                ("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("LEFTPADDING",(0,0),(-1,-1),8),
            ]))
            story.append(pt)
            story.append(Spacer(1,10))

            # Devotee table
            story.append(Paragraph("Devotee Details", sec_s))
            dev_rows = [
                ["Name",         form_data.get("name","—")],
                ["Gothram",      form_data.get("gothram","—")],
                ["Dharma Patni", form_data.get("dharma_patni_name") or "—"],
                ["Family Name",  form_data.get("family_name") or "—"],
                ["Location",     ", ".join(filter(None,[
                    form_data.get("city"), form_data.get("state"), form_data.get("country")]))],
            ]
            dev_data = [[Paragraph(r[0], mk("dc",9,"#5C3317",after=0)),
                         Paragraph(r[1], mk("dv",9,"#1a1a1a",after=0))]
                        for r in dev_rows]
            dt = Table(dev_data, colWidths=[4.5*cm, 11*cm])
            dt.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#E8F5E9")),
                ("BACKGROUND",(1,0),(1,-1),colors.HexColor("#F1F8E9")),
                ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#A5D6A7")),
                ("TOPPADDING",(0,0),(-1,-1),5),
                ("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("LEFTPADDING",(0,0),(-1,-1),8),
            ]))
            story.append(dt)
            story.append(Spacer(1,14))

            # Sankalpam text
            story.append(HR(2,"#8B0000",4,6))
            story.append(Paragraph(f"Sankalpam ({language.title()})", sec_s))

            SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            parts = sankalpam_text.split(SEP)

            for i, part in enumerate(parts):
                part = part.strip()
                if not part: continue
                if i == 1:
                    story.append(Spacer(1,8))
                    story.append(HR(1,"#DEB887",0,6))
                    story.append(Paragraph("Meaning / Translation", mk("MH",10,"#8B0000",after=4)))
                for para in part.split("\n\n"):
                    para = para.strip()
                    if para:
                        safe_p = para.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        story.append(Paragraph(safe_p, body_s))
                        story.append(Spacer(1,3))

            story.append(Spacer(1,16))
            story.append(HR(1,"#DEB887",0,5))
            story.append(Paragraph(
                f"Generated on {datetime.now().strftime('%d %B %Y at %I:%M %p')} | Sankalpam Generator",
                small_s))
            story.append(Paragraph("|| Shubham Bhavatu || May all be auspicious ||", ctr_s))

            doc.build(story)
            logger.info(f"PDF saved: {path}")
            return path

        except ImportError:
            raise RuntimeError("reportlab not installed. Run: pip install reportlab")
        except Exception as e:
            logger.error(f"PDF failed: {e}", exc_info=True)
            raise

    def _get_font(self, language="english"):
        """
        Register best available Unicode font.
        Priority: downloaded Noto > system fonts > Helvetica fallback.
        """
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # Already registered?
        try:
            pdfmetrics.getFont("NotoSans")
            return "NotoSans"
        except Exception:
            pass

        # System fonts (Windows / Mac / Linux)
        system_fonts = [
            # Windows — Arial supports Latin; for Indic we need Noto
            (r"C:\Windows\Fonts\arial.ttf",        "ArialW"),
            # macOS
            ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "ArialU"),
            # Linux Noto (apt install fonts-noto)
            ("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",        "NotoSans"),
            ("/usr/share/fonts/truetype/noto/NotoSansTelugu-Regular.ttf",  "NotoTelugu"),
            ("/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf",   "NotoTamil"),
            ("/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf", "NotoKannada"),
            ("/usr/share/fonts/truetype/freefont/FreeSans.ttf",            "FreeSans"),
            ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf","Liberation"),
        ]

        # Try cached downloaded Noto first
        cached = os.path.join(FONT_CACHE, "NotoSans-Regular.ttf")
        if os.path.exists(cached):
            try:
                pdfmetrics.registerFont(TTFont("NotoSans", cached))
                logger.info("Using cached NotoSans")
                return "NotoSans"
            except Exception:
                pass

        # Try system fonts
        for path, name in system_fonts:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont(name, path))
                    logger.info(f"Using system font: {path}")
                    return name
                except Exception:
                    pass

        # Try downloading Noto (requires internet)
        try:
            import urllib.request
            url = "https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
            logger.info("Downloading NotoSans font…")
            urllib.request.urlretrieve(url, cached)
            pdfmetrics.registerFont(TTFont("NotoSans", cached))
            logger.info("Downloaded and registered NotoSans")
            return "NotoSans"
        except Exception as e:
            logger.warning(f"Could not download font: {e}")

        logger.warning("Falling back to Helvetica — Indic glyphs may not render")
        return "Helvetica"
