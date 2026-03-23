"""
sankalpam_generator.py (v5 – exact format, single flowing sentence)
"""
import math, logging
from transliteration import name_to_deva, deva_to_script, to_script
logger = logging.getLogger(__name__)

SEP = "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

# ── Dvipa info: country → (dvipa_deva, varsha_deva, khanda_deva, meru_dir_deva)
DVIPA = {
    "india":               ("जम्बुद्वीपे","भारतवर्षे","भारतखण्डे","मेरोः दक्षिणदिग्भागे"),
    "nepal":               ("जम्बुद्वीपे","भारतवर्षे","भारतखण्डे","मेरोः दक्षिणदिग्भागे"),
    "sri lanka":           ("जम्बुद्वीपे","भारतवर्षे","भारतखण्डे","मेरोः दक्षिणदिग्भागे"),
    "bangladesh":          ("जम्बुद्वीपे","भारतवर्षे","भारतखण्डे","मेरोः दक्षिणदिग्भागे"),
    "pakistan":            ("जम्बुद्वीपे","भारतवर्षे","भारतखण्डे","मेरोः पश्चिमदिग्भागे"),
    "usa":                 ("क्रौञ्चद्वीपे","रमणकवर्षे","इन्द्रखण्डे","मेरोः पश्चिमदिग्भागे"),
    "united states":       ("क्रौञ्चद्वीपे","रमणकवर्षे","इन्द्रखण्डे","मेरोः पश्चिमदिग्भागे"),
    "canada":              ("क्रौञ्चद्वीपे","रमणकवर्षे","इन्द्रखण्डे","मेरोः पश्चिमदिग्भागे"),
    "mexico":              ("क्रौञ्चद्वीपे","रमणकवर्षे","इन्द्रखण्डे","मेरोः पश्चिमदिग्भागे"),
    "uk":                  ("प्लक्षद्वीपे","शिशिरवर्षे","प्लक्षखण्डे","मेरोः पश्चिमोत्तरदिग्भागे"),
    "united kingdom":      ("प्लक्षद्वीपे","शिशिरवर्षे","प्लक्षखण्डे","मेरोः पश्चिमोत्तरदिग्भागे"),
    "germany":             ("प्लक्षद्वीपे","शिशिरवर्षे","प्लक्षखण्डे","मेरोः पश्चिमोत्तरदिग्भागे"),
    "france":              ("प्लक्षद्वीपे","शिशिरवर्षे","प्लक्षखण्डे","मेरोः पश्चिमोत्तरदिग्भागे"),
    "netherlands":         ("प्लक्षद्वीपे","शिशिरवर्षे","प्लक्षखण्डे","मेरोः पश्चिमोत्तरदिग्भागे"),
    "sweden":              ("प्लक्षद्वीपे","शिशिरवर्षे","प्लक्षखण्डे","मेरोः पश्चिमोत्तरदिग्भागे"),
    "italy":               ("प्लक्षद्वीपे","शिशिरवर्षे","प्लक्षखण्डे","मेरोः पश्चिमोत्तरदिग्भागे"),
    "spain":               ("प्लक्षद्वीपे","शिशिरवर्षे","प्लक्षखण्डे","मेरोः पश्चिमोत्तरदिग्भागे"),
    "australia":           ("पुष्करद्वीपे","उत्तरवर्षे","पुष्करखण्डे","मेरोः आग्नेयदिग्भागे"),
    "new zealand":         ("पुष्करद्वीपे","उत्तरवर्षे","पुष्करखण्डे","मेरोः आग्नेयदिग्भागे"),
    "south africa":        ("शाल्मलद्वीपे","शाल्मलिवर्षे","शाल्मलिखण्डे","मेरोः दक्षिणपश्चिमदिग्भागे"),
    "nigeria":             ("शाल्मलद्वीपे","शाल्मलिवर्षे","शाल्मलिखण्डे","मेरोः दक्षिणपश्चिमदिग्भागे"),
    "kenya":               ("शाल्मलद्वीपे","शाल्मलिवर्षे","शाल्मलिखण्डे","मेरोः दक्षिणपश्चिमदिग्भागे"),
    "brazil":              ("शाकद्वीपे","शाकवर्षे","शाकखण्डे","मेरोः पश्चिमदक्षिणदिग्भागे"),
    "argentina":           ("शाकद्वीपे","शाकवर्षे","शाकखण्डे","मेरोः पश्चिमदक्षिणदिग्भागे"),
    "uae":                 ("जम्बुद्वीपे","भारतवर्षे","पश्चिमखण्डे","मेरोः पश्चिमदिग्भागे"),
    "united arab emirates":("जम्बुद्वीपे","भारतवर्षे","पश्चिमखण्डे","मेरोः पश्चिमदिग्भागे"),
    "singapore":           ("जम्बुद्वीपे","भारतवर्षे","पूर्वखण्डे","मेरोः पूर्वदिग्भागे"),
    "malaysia":            ("जम्बुद्वीपे","भारतवर्षे","पूर्वखण्डे","मेरोः पूर्वदिग्भागे"),
}
DEFAULT_DVIPA = ("जम्बुद्वीपे","भारतवर्षे","भारतखण्डे","मेरोः दक्षिणदिग्भागे")

def get_dvipa(country): return DVIPA.get(country.lower().strip(), DEFAULT_DVIPA)

# ── Panchang terms in Devanagari ──────────────────────────────────────────────
AYANA_DEVA   = {"Uttarayana":"उत्तरायणे",   "Dakshinayana":"दक्षिणायने"}
PAKSHA_DEVA  = {"Shukla Paksha":"शुक्लपक्षे","Krishna Paksha":"कृष्णपक्षे"}
RITU_DEVA    = {"Vasanta":"वसन्तऋतौ","Grishma":"ग्रीष्मऋतौ","Varsha":"वर्षऋतौ",
                "Sharada":"शरदृतौ","Hemanta":"हेमन्तऋतौ","Shishira":"शिशिरऋतौ"}
VARA_ORDER   = ["Ravivara","Somavara","Mangalavara","Budhavara","Guruvara","Shukravara","Shanivara"]
VARA_DEVA    = ["रविवासरे","सोमवासरे","भौमवासरे","सौम्यवासरे","गुरुवासरे","शुक्रवासरे","शनिवासरे"]
VARA_EN      = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

MASA_DEVA = {
    "Chaitra":"चैत्रमासे","Vaishakha":"वैशाखमासे","Jyeshtha":"ज्येष्ठमासे",
    "Ashadha":"आषाढमासे","Shravana":"श्रावणमासे","Bhadrapada":"भाद्रपदमासे",
    "Ashwayuja":"आश्वयुजमासे","Kartika":"कार्तिकमासे","Margashira":"मार्गशीर्षमासे",
    "Pushya":"पुष्यमासे","Magha":"माघमासे","Phalguna":"फाल्गुनमासे",
    # Tamil calendar months
    "Chithirai":"चैत्रमासे","Vaikasi":"वैशाखमासे","Aani":"ज्येष्ठमासे",
    "Aadi":"आषाढमासे","Aavani":"श्रावणमासे","Purattasi":"भाद्रपदमासे",
    "Aippasi":"आश्वयुजमासे","Karthigai":"कार्तिकमासे","Margazhi":"मार्गशीर्षमासे",
    "Thai":"पुष्यमासे","Maasi":"माघमासे","Panguni":"फाल्गुनमासे",
}

TITHI_DEVA = {
    "Pratipada":"प्रतिपदायाम्","Dwitiya":"द्वितीयायाम्","Tritiya":"तृतीयायाम्",
    "Chaturthi":"चतुर्थ्याम्","Panchami":"पञ्चम्याम्","Shashti":"षष्ठ्याम्",
    "Saptami":"सप्तम्याम्","Ashtami":"अष्टम्याम्","Navami":"नवम्याम्","Dashami":"दशम्याम्",
    "Ekadashi":"एकादश्याम्","Dwadashi":"द्वादश्याम्","Trayodashi":"त्रयोदश्याम्",
    "Chaturdashi":"चतुर्दश्याम्","Purnima":"पौर्णमास्याम्","Amavasya":"अमावास्यायाम्",
}

NAKSHATRA_DEVA = {
    "Ashwini":"अश्विनीनक्षत्रे","Bharani":"भरणीनक्षत्रे","Krittika":"कृत्तिकानक्षत्रे",
    "Rohini":"रोहिणीनक्षत्रे","Mrigashira":"मृगशिरानक्षत्रे","Ardra":"आर्द्रानक्षत्रे",
    "Punarvasu":"पुनर्वसुनक्षत्रे","Pushya":"पुष्यनक्षत्रे","Ashlesha":"आश्लेषानक्षत्रे",
    "Magha":"मघानक्षत्रे","Purva Phalguni":"पूर्वफाल्गुनीनक्षत्रे",
    "Uttara Phalguni":"उत्तरफाल्गुनीनक्षत्रे","Hasta":"हस्तनक्षत्रे",
    "Chitra":"चित्रानक्षत्रे","Swati":"स्वातीनक्षत्रे","Vishakha":"विशाखानक्षत्रे",
    "Anuradha":"अनुराधानक्षत्रे","Jyeshtha":"ज्येष्ठानक्षत्रे","Mula":"मूलनक्षत्रे",
    "Purva Ashadha":"पूर्वाषाढानक्षत्रे","Uttara Ashadha":"उत्तराषाढानक्षत्रे",
    "Shravana":"श्रवणनक्षत्रे","Dhanishtha":"धनिष्ठानक्षत्रे",
    "Shatabhisha":"शतभिषानक्षत्रे","Purva Bhadrapada":"पूर्वभाद्रपदानक्षत्रे",
    "Uttara Bhadrapada":"उत्तरभाद्रपदानक्षत्रे","Revati":"रेवतीनक्षत्रे",
}

YOGA_DEVA = {
    "Vishkambha":"विष्कम्भयोगे","Priti":"प्रीतियोगे","Ayushman":"आयुष्मान्योगे",
    "Saubhagya":"सौभाग्ययोगे","Shobhana":"शोभनयोगे","Atiganda":"अतिगण्डयोगे",
    "Sukarma":"सुकर्मयोगे","Dhriti":"धृतियोगे","Shula":"शूलयोगे","Ganda":"गण्डयोगे",
    "Vriddhi":"वृद्धियोगे","Dhruva":"ध्रुवयोगे","Vyaghata":"व्याघातयोगे",
    "Harshana":"हर्षणयोगे","Vajra":"वज्रयोगे","Siddhi":"सिद्धियोगे",
    "Vyatipata":"व्यतीपातयोगे","Variyana":"वरीयान्योगे","Parigha":"परिघयोगे",
    "Shiva":"शिवयोगे","Siddha":"सिद्धयोगे","Sadhya":"साध्ययोगे","Shubha":"शुभयोगे",
    "Shukla":"शुक्लयोगे","Brahma":"ब्रह्मयोगे","Indra":"इन्द्रयोगे","Vaidhriti":"वैधृतियोगे",
}

KARANA_DEVA = {
    "Bava":"बवकरणे","Balava":"बालवकरणे","Kaulava":"कौलवकरणे","Taitila":"तैतिलकरणे",
    "Garaja":"गरजकरणे","Vanija":"वणिजकरणे","Vishti":"विष्टिकरणे","Shakuni":"शकुनिकरणे",
    "Chatushpada":"चतुष्पादकरणे","Nagava":"नागवकरणे","Kimstughna":"किंस्तुघ्नकरणे",
}

# ── Rivers ────────────────────────────────────────────────────────────────────
RIVERS = [
    (27.90,78.10,"Ganga"),(25.32,82.97,"Ganga"),(22.57,88.36,"Hooghly"),
    (16.50,80.62,"Krishna"),(17.38,78.48,"Musi"),(13.08,80.27,"Cooum"),
    (12.97,77.59,"Arkavathi"),(18.52,73.85,"Mula-Mutha"),(19.07,72.87,"Ulhas"),
    (26.84,80.94,"Gomti"),(14.40,75.73,"Tungabhadra"),(8.50,76.95,"Pamba"),
    (49.19,-122.84,"Fraser"),(43.70,-79.42,"Humber"),(45.50,-73.56,"St. Lawrence"),
    (40.71,-74.00,"Hudson"),(47.60,-122.33,"Duwamish"),(37.77,-122.41,"Sacramento"),
    (29.76,-95.36,"Buffalo Bayou"),(41.88,-87.62,"Chicago"),(38.89,-77.03,"Potomac"),
    (44.97,-93.27,"Mississippi"),(51.50,-0.12,"Thames"),(48.85,2.35,"Seine"),
    (52.52,13.40,"Spree"),(-33.86,151.20,"Parramatta"),(-37.81,144.96,"Yarra"),
    (-27.46,153.02,"Brisbane"),(-31.95,115.86,"Swan"),(-33.92,18.42,"Liesbeek"),
    (-23.55,-46.63,"Tiete"),(1.35,103.82,"Kallang"),(25.20,55.27,"Dubai Creek"),
]

def get_nearest_river(lat, lon):
    best, blat, blon = "Ganga", 27.90, 78.10
    md = float("inf")
    for rlat,rlon,rname in RIVERS:
        d = math.sqrt((lat-rlat)**2+(lon-rlon)**2)
        if d < md: md,best,blat,blon = d,rname,rlat,rlon
    dlat,dlon = blat-lat, blon-lon
    # no direction needed — just "sameepe" (nearby)
    return best


class SankalpamGenerator:

    def generate_all_languages(self, panchang, form_data, location):
        ctx = self._ctx(panchang, form_data, location)
        # Build the master Sanskrit Devanagari sentence once
        deva_sentence = self._build_deva(ctx)
        return {
            "sanskrit": deva_sentence + SEP + self._meaning_en(ctx, "sanskrit"),
            "english":  self._build_english(ctx) + SEP + self._meaning_en(ctx, "english"),
            "telugu":   deva_to_script(deva_sentence,"telugu")  + SEP + self._meaning_native(ctx,"telugu"),
            "tamil":    deva_to_script(deva_sentence,"tamil")   + SEP + self._meaning_native(ctx,"tamil"),
            "kannada":  deva_to_script(deva_sentence,"kannada") + SEP + self._meaning_native(ctx,"kannada"),
            "marathi":  deva_sentence + SEP + self._meaning_native(ctx,"marathi"),
            "hindi":    deva_sentence + SEP + self._meaning_native(ctx,"hindi"),
        }

    def _ctx(self, panchang, form_data, location):
        country = form_data.get("country","India").strip()
        state   = form_data.get("state","").strip()
        city    = form_data.get("city","").strip()
        lat     = location.get("latitude", 17.38)
        lon     = location.get("longitude",78.48)
        vara_idx = VARA_ORDER.index(panchang["vara"]) if panchang["vara"] in VARA_ORDER else 0
        river   = get_nearest_river(lat, lon)
        dvipa   = get_dvipa(country)

        # Build compound location in Devanagari (no spaces in compounds)
        country_deva = name_to_deva(country)
        state_deva   = name_to_deva(state) if state else ""
        city_deva    = name_to_deva(city)  if city  else ""
        river_deva   = name_to_deva(river)

        # Panchang in Devanagari
        samvat_deva   = name_to_deva(panchang["samvatsara"])
        ayana_deva    = AYANA_DEVA.get(panchang["ayana"], panchang["ayana"])
        ritu_deva     = RITU_DEVA.get(panchang["ritu"], panchang["ritu"]+"ऋतौ")
        masa_deva     = MASA_DEVA.get(panchang["masa"], name_to_deva(panchang["masa"])+"मासे")
        paksha_deva   = PAKSHA_DEVA.get(panchang["paksha"], panchang["paksha"])
        tithi_deva    = TITHI_DEVA.get(panchang["tithi"], name_to_deva(panchang["tithi"])+"तिथौ")
        vara_deva     = VARA_DEVA[vara_idx]
        naksh_deva    = NAKSHATRA_DEVA.get(panchang["nakshatra"], name_to_deva(panchang["nakshatra"])+"नक्षत्रे")
        yoga_deva     = YOGA_DEVA.get(panchang["yoga"], name_to_deva(panchang["yoga"])+"योगे")
        karana_deva   = KARANA_DEVA.get(panchang["karana"], name_to_deva(panchang["karana"])+"करणे")

        # Personal names in Devanagari
        name_deva    = name_to_deva(form_data.get("name",""))
        gothram_deva = name_to_deva(form_data.get("gothram",""))
        patni_raw    = form_data.get("dharma_patni_name","").strip()
        patni_deva   = name_to_deva(patni_raw) if patni_raw else ""
        pooja_raw    = form_data.get("pooja_name","Pooja").strip()
        # Remove common suffixes for compound form
        pooja_base   = pooja_raw.replace(" Puja","").replace(" Homa","").replace(" Puja","")
        pooja_deva   = name_to_deva(pooja_base) + "पूजां"

        s_type       = form_data.get("sankalpam_type","").strip()
        desires      = form_data.get("desires","").strip()
        other_members= form_data.get("other_members","").strip()

        return dict(
            # raw
            name_raw=form_data.get("name",""), gothram_raw=form_data.get("gothram",""),
            patni_raw=patni_raw, pooja_raw=pooja_raw, s_type=s_type, desires=desires,
            other_members=other_members,
            city=city, state=state, country=country,
            river=river,
            # panchang raw
            samvatsara=panchang["samvatsara"], ayana=panchang["ayana"],
            ritu=panchang["ritu"], ritu_en=panchang.get("ritu_english",""),
            masa=panchang["masa"], paksha=panchang["paksha"], tithi=panchang["tithi"],
            vara_idx=vara_idx, vara_en=VARA_EN[vara_idx],
            nakshatra=panchang["nakshatra"], yoga=panchang["yoga"], karana=panchang["karana"],
            # Devanagari
            dvipa=dvipa,
            country_deva=country_deva, state_deva=state_deva, city_deva=city_deva,
            river_deva=river_deva,
            samvat_deva=samvat_deva, ayana_deva=ayana_deva, ritu_deva=ritu_deva,
            masa_deva=masa_deva, paksha_deva=paksha_deva, tithi_deva=tithi_deva,
            vara_deva=vara_deva, naksh_deva=naksh_deva, yoga_deva=yoga_deva,
            karana_deva=karana_deva,
            name_deva=name_deva, gothram_deva=gothram_deva,
            patni_deva=patni_deva, pooja_deva=pooja_deva,
        )

    def _build_deva(self, c):
        """Build the canonical Sanskrit Devanagari sentence."""
        d = c["dvipa"]
        loc = c["country_deva"] + "देशे"
        if c["state"]:  loc = c["state_deva"]  + "प्रदेशे, " + loc
        if c["city"]:   loc = c["city_deva"]   + "नगरे, " + loc

        # Build family part: patni + other members
        family_parts = []
        if c["patni_raw"]:
            family_parts.append(f"सधर्मिणी {c['patni_deva']} सहितस्य")
        if c.get("other_members",""):
            other_deva = ", ".join(name_to_deva(m.strip()) for m in c["other_members"].split(",") if m.strip())
            family_parts.append(other_deva + " सहितस्य")
        family_parts.append("मम सहकुटुम्बस्य")
        patni_part = ", " + ", ".join(family_parts)
        desires_part = f", (स्वकीयाः कामनाः: {c['desires']})" if c["desires"] else ""
        s_type_part = f" ({c['s_type']})" if c["s_type"] else ""

        return (
            f"ॐ श्री महाविष्णोराज्ञया प्रवर्तमानस्य, "
            f"अद्य ब्रह्मणः द्वितीयपरार्धे, "
            f"श्वेतवराहकल्पे, वैवस्वतमन्वन्तरे, कलियुगे, प्रथमपादे, "
            f"{d[0]}, {d[1]}, {d[2]}, {d[3]}, "
            f"{loc}, "
            f"{c['river_deva']} नदी समीपे, "
            f"अस्मिन् वर्तमाने, व्यावहारिकचान्द्रमानेन, "
            f"{c['samvat_deva']} नाम संवत्सरे, "
            f"{c['ayana_deva']}, {c['ritu_deva']}, {c['masa_deva']}, "
            f"{c['paksha_deva']}, {c['tithi_deva']}, {c['vara_deva']}, "
            f"{c['naksh_deva']}, {c['yoga_deva']}, {c['karana_deva']}, "
            f"एवं गुणविशेषणविशिष्टायां शुभतिथौ, "
            f"{c['gothram_deva']}गोत्रभवस्य, {c['name_deva']}नामधेयस्य"
            f"{patni_part}, "
            f"क्षेमस्थैर्यायुरारोग्यऐश्वर्याभिवृद्ध्यर्थम्, "
            f"धर्मार्थकाममोक्षचतुर्विधफलपुरुषार्थसिद्ध्यर्थम्, "
            f"इष्टकाम्यर्थसिद्ध्यर्थम्, "
            f"श्रीपरमेश्वरप्रीत्यर्थं, "
            f"{c['pooja_deva']} करिष्ये"
            f"{desires_part} ॥"
        )

    def _build_english(self, c):
        """Romanised English transliteration of the Sankalpam."""
        d = c["dvipa"]
        # Convert Devanagari dvipa to roman via script labels
        dvipa_en = _deva_tuple_to_en(d, c["country"])
        loc_parts = []
        if c["city"]:  loc_parts.append(c["city"] + "nagare")
        if c["state"]: loc_parts.append(c["state"].replace(" ","") + "pradeshe")
        loc_parts.append(c["country"].replace(" ","") + "deshe")
        loc_en = ", ".join(loc_parts)

        ayana_en  = "Uttarayane" if c["ayana"]=="Uttarayana" else "Dakshinayane"
        paksha_en = "ShuklaPakshe" if "Shukla" in c["paksha"] else "KrishnaPakshe"
        tithi_en  = c["tithi"].replace(" ","") + "tithau"
        vara_en   = ["Ravi","Soma","Bhouma","Sowmya","Guru","Shukra","Sthira"][c["vara_idx"]] + "vasare"
        naksh_en  = c["nakshatra"].replace(" ","") + "nakshatre"
        yoga_en   = c["yoga"].replace(" ","") + "yoge"
        karana_en = c["karana"].replace(" ","") + "karane"
        ritu_en   = c["ritu"] + "rutau"
        masa_en   = c["masa"] + "mase"
        patni_part = f", sadharmiNi {c['patni_raw']} sahitasya, mama sahakuTumbasya" if c["patni_raw"] \
                     else ", mama sahakuTumbasya"
        desires_part = f", (svakeeya kaamanah: {c['desires']})" if c["desires"] else ""
        pooja_base = c["pooja_raw"].replace(" Puja","").replace(" Homa","")
        s_type_part = f" ({c['s_type']})" if c["s_type"] else ""

        return (
            f"Om Sri Maha Vishnu Rajnaya pravartamanasya, "
            f"adya Brahmanah dviteeya paradhe, "
            f"Shvetavaraha kalpe, Vaivasvata manvantare, Kaliyuge, Prathama pade, "
            f"{dvipa_en}, "
            f"{loc_en}, "
            f"{c['river'].replace(' ','')} nadi sameepe, "
            f"asmin vartamane, vyavaharika chandra manena, "
            f"{c['samvatsara']} nama samvatsare, "
            f"{ayana_en}, {ritu_en}, {masa_en}, "
            f"{paksha_en}, {tithi_en}, {vara_en}, "
            f"{naksh_en}, {yoga_en}, {karana_en}, "
            f"evam guna visheshana vishishtayam shubha tithau, "
            f"{c['gothram_raw'].replace(' ','')}gothrabhavasyа, {c['name_raw'].replace(' ','')}namadheyasya"
            f"{patni_part}, "
            f"kshema sthairya ayurarogya aishvarya abhivruddhyartham, "
            f"dharmarthha kamamoksha chaturvidha phala purushardha siddhyartham, "
            f"ishta kamyartha siddhyartham, "
            f"Sri Parameshwara preetyartham, "
            f"{pooja_base.replace(' ','')}pujam{s_type_part} karishye"
            f"{desires_part} ||"
        )

    def _meaning_en(self, c, tab):
        """English meaning paragraph."""
        ayana_date = "(Jan 14–Jul 13)" if c["ayana"]=="Uttarayana" else "(Jul 14–Jan 13)"
        paksha_m = "Shukla Paksha (Bright Fortnight)" if "Shukla" in c["paksha"] else "Krishna Paksha (Dark Fortnight)"
        loc_full = ", ".join(filter(None,[c["city"], c["state"], c["country"]]))
        patni_m = f", along with wife {c['patni_raw']}," if c["patni_raw"] else ","
        other_m = ""
        if c.get("other_members",""):
            other_m = ", " + c["other_members"]
        pooja_m = c["pooja_raw"]
        desires_m = f"\n\n(Personal desires: {c['desires']})" if c["desires"] else ""
        prefix = "\nMeaning — " if tab == "english" else "\nMeaning of the above Sankalpam — "
        return (
            f"{prefix}By the command of Sri Maha Vishnu, "
            f"in the {c['samvatsara']} Samvatsara, during {c['ayana']} {ayana_date}, "
            f"in the {c['ritu']} ({c['ritu_en']}) season, in the month of {c['masa']}, "
            f"in {paksha_m}, on the {c['tithi']} Tithi, on {c['vara_en']}, "
            f"under {c['nakshatra']} Nakshatra, in {c['yoga']} Yoga, in {c['karana']} Karana — "
            f"near {c['river']} river, in {loc_full} — "
            f"I, {c['name_raw']} of {c['gothram_raw']} Gotra{patni_m}{other_m} "
            f"for the welfare, stability, long life, health and prosperity of our family, "
            f"for the attainment of Dharma, Artha, Kama and Moksha (the four goals of life), "
            f"for the fulfilment of cherished desires, "
            f"for the grace of Sri Parameshwara — "
            f"am performing the {pooja_m}."
            f"{desires_m}"
        )

    def _meaning_native(self, c, script):
        """Meaning paragraph in native language (Telugu/Tamil/Kannada/Marathi/Hindi)."""
        def s(deva): return deva_to_script(deva, script)
        ayana_date = "(Jan 14–Jul 13)" if c["ayana"]=="Uttarayana" else "(Jul 14–Jan 13)"
        ayana_s    = s(AYANA_DEVA.get(c["ayana"], c["ayana"]))
        ritu_s     = s(RITU_DEVA.get(c["ritu"], c["ritu"]))
        masa_s     = s(MASA_DEVA.get(c["masa"], c["masa"]))
        paksha_s   = s(PAKSHA_DEVA.get(c["paksha"], c["paksha"]))
        tithi_s    = s(TITHI_DEVA.get(c["tithi"], c["tithi"]))
        vara_s     = s(VARA_DEVA[c["vara_idx"]])
        naksh_s    = s(NAKSHATRA_DEVA.get(c["nakshatra"], c["nakshatra"]))
        yoga_s     = s(YOGA_DEVA.get(c["yoga"], c["yoga"]))
        karana_s   = s(KARANA_DEVA.get(c["karana"], c["karana"]))
        name_s     = s(c["name_deva"])
        gothram_s  = s(c["gothram_deva"])
        patni_s    = s(c["patni_deva"]) if c["patni_raw"] else ""
        pooja_s    = s(c["pooja_deva"])
        city_s     = s(c["city_deva"]) if c.get("city_deva") else s(name_to_deva(c["city"]))
        state_s    = s(c["state_deva"]) if c.get("state_deva") else (s(name_to_deva(c["state"])) if c["state"] else "")
        country_s  = s(c["country_deva"]) if c.get("country_deva") else s(name_to_deva(c["country"]))
        river_s    = s(c["river_deva"])
        dvipa_s    = ", ".join(s(p) for p in c["dvipa"])
        samvat_s   = s(c["samvat_deva"])

        loc_full = ", ".join(filter(None,[c["city"], c["state"], c["country"]]))
        desires_deva = f"\n\n(व्यक्तिगत कामनाः: {c['desires']})" if c["desires"] else ""
        desires_s = s(desires_deva) if c["desires"] else ""

        # Language-specific meaning templates
        other_m_s = ""
        if c.get("other_members",""):
            members = [name_to_deva(m.strip()) for m in c["other_members"].split(",") if m.strip()]
            other_m_s = ", " + ", ".join(s(m) for m in members)

        loc_tel = ", ".join(filter(None,[
            city_s  + "నగరే" if city_s  else "",
            state_s + "ప్రదేశే" if state_s else "",
            country_s + "దేశే"
        ]))

        if script == "telugu":
            patni_m = f", సధర్మిణి {patni_s}తో" if c["patni_raw"] else ""
            return (
                f"\nఅర్థం — శ్రీమహావిష్ణువు ఆజ్ఞచే, {samvat_s} సంవత్సరమున, "
                f"{ayana_s} {ayana_date}, {ritu_s}, {masa_s}, {paksha_s}, "
                f"{tithi_s}, {vara_s} ({c['vara_en']}), {naksh_s}, "
                f"{yoga_s}, {karana_s} — {dvipa_s}; {river_s} నది సమీపే; "
                f"{loc_tel} — {gothram_s} గోత్రభవస్య, {name_s} నామధేయస్య{patni_m}{other_m_s}, "
                f"కుటుంబ క్షేమ స్థైర్య ఆయురారోగ్య ఐశ్వర్యాభివృద్ధికై, "
                f"ధర్మార్థ కామమోక్ష చతుర్విధ పురుషార్థ సిద్ధికై, "
                f"ఇష్ట కామ్యార్థ సిద్ధికై, శ్రీ పరమేశ్వర ప్రీత్యర్థం — "
                f"{pooja_s} కరిష్యే ।{desires_s}"
            )
        elif script == "tamil":
            patni_m = f", சஹதர்மிணி {patni_s}வுடன்" if c["patni_raw"] else ""
            loc_tam = ", ".join(filter(None,[
                city_s  + "நகரே" if city_s  else "",
                state_s + "பிரதேசே" if state_s else "",
                country_s + "தேசே"
            ]))
            return (
                f"\nபொருள் — ஸ்ரீமகாவிஷ்ணுவின் ஆணையால், {samvat_s} ஸம்வத்ஸரத்தில், "
                f"{ayana_s} {ayana_date}, {ritu_s}, {masa_s}, {paksha_s}, "
                f"{tithi_s}, {vara_s} ({c['vara_en']}), {naksh_s}, "
                f"{yoga_s}, {karana_s} — {dvipa_s}; {river_s} நதி சமீபே; "
                f"{loc_tam} — {gothram_s} கோத்ரபவஸ்ய, {name_s} நாமதேயஸ்ய{patni_m}{other_m_s}, "
                f"குடும்ப க்ஷேம ஸ்தைர்ய ஆயுராரோக்ய ஐஸ்வர்யாபிவ்ருத்திக்காக, "
                f"தர்மார்த காம மோக்ஷ சதுர்வித புருஷார்த சித்திக்காக, "
                f"இஷ்ட காம்யார்த சித்திக்காக, ஸ்ரீ பரமேஸ்வர ப்ரீத்யர்தம் — "
                f"{pooja_s} கரிஷ்யே ।{desires_s}"
            )
        elif script == "kannada":
            patni_m = f", ಸಹಧರ್ಮಿಣಿ {patni_s}ರೊಂದಿಗೆ" if c["patni_raw"] else ""
            loc_kan = ", ".join(filter(None,[
                city_s  + "ನಗರೇ" if city_s  else "",
                state_s + "ಪ್ರದೇಶೇ" if state_s else "",
                country_s + "ದೇಶೇ"
            ]))
            return (
                f"\nಅರ್ಥ — ಶ್ರೀಮಹಾವಿಷ್ಣುವಿನ ಆಜ್ಞೆಯಿಂದ, {samvat_s} ಸಂವತ್ಸರದಲ್ಲಿ, "
                f"{ayana_s} {ayana_date}, {ritu_s}, {masa_s}, {paksha_s}, "
                f"{tithi_s}, {vara_s} ({c['vara_en']}), {naksh_s}, "
                f"{yoga_s}, {karana_s} — {dvipa_s}; {river_s} ನದಿ ಸಮೀಪ; "
                f"{loc_kan} — {gothram_s} ಗೋತ್ರಭವಸ್ಯ, {name_s} ನಾಮಧೇಯಸ್ಯ{patni_m}{other_m_s}, "
                f"ಕುಟುಂಬ ಕ್ಷೇಮ ಸ್ಥೈರ್ಯ ಆಯುರಾರೋಗ್ಯ ಐಶ್ವರ್ಯಾಭಿವೃದ್ಧಿಗಾಗಿ, "
                f"ಧರ್ಮಾರ್ಥ ಕಾಮಮೋಕ್ಷ ಚತುರ್ವಿಧ ಪುರುಷಾರ್ಥ ಸಿದ್ಧಿಗಾಗಿ, "
                f"ಇಷ್ಟಕಾಮ್ಯಾರ್ಥ ಸಿದ್ಧಿಗಾಗಿ, ಶ್ರೀ ಪರಮೇಶ್ವರ ಪ್ರೀತ್ಯರ್ಥಂ — "
                f"{pooja_s} ಕರಿಷ್ಯೇ ।{desires_s}"
            )
        elif script == "marathi":
            patni_m = f", सहधर्मिणी {patni_s} यांच्यासह" if c["patni_raw"] else ""
            loc_mar = ", ".join(filter(None,[
                city_s  + "नगरे" if city_s  else "",
                state_s + "प्रदेशे" if state_s else "",
                country_s + "देशे"
            ]))
            return (
                f"\nअर्थ — श्रीमहाविष्णूच्या आज्ञेने, {samvat_s} संवत्सरात, "
                f"{ayana_s} {ayana_date}, {ritu_s}, {masa_s}, {paksha_s}, "
                f"{tithi_s}, {vara_s} ({c['vara_en']}), {naksh_s}, "
                f"{yoga_s}, {karana_s} — {dvipa_s}; {river_s} नदी समीप; "
                f"{loc_mar} — {gothram_s} गोत्रभवस्य, {name_s} नामधेयस्य{patni_m}{other_m_s}, "
                f"कुटुंबाच्या क्षेम, स्थैर्य, आयुरारोग्य, ऐश्वर्याभिवृद्धीसाठी, "
                f"धर्मार्थ काम मोक्ष चतुर्विध पुरुषार्थ सिद्धीसाठी, "
                f"इष्ट कामार्थ सिद्धीसाठी, श्री परमेश्वर प्रीत्यर्थ — "
                f"{pooja_s} करिष्ये ।{desires_s}"
            )
        else:  # hindi
            patni_m = f", सहधर्मिणी {patni_s} के साथ" if c["patni_raw"] else ""
            loc_hin = ", ".join(filter(None,[
                city_s  + "नगरे" if city_s  else "",
                state_s + "प्रदेशे" if state_s else "",
                country_s + "देशे"
            ]))
            return (
                f"\nअर्थ — श्रीमहाविष्णु की आज्ञा से, {samvat_s} संवत्सर में, "
                f"{ayana_s} {ayana_date}, {ritu_s}, {masa_s}, {paksha_s}, "
                f"{tithi_s}, {vara_s} ({c['vara_en']}), {naksh_s}, "
                f"{yoga_s}, {karana_s} — {dvipa_s}; {river_s} नदी समीप; "
                f"{loc_hin} — {gothram_s} गोत्रभवस्य, {name_s} नामधेयस्य{patni_m}{other_m_s}, "
                f"परिवार के क्षेम, स्थैर्य, आयु, आरोग्य और ऐश्वर्य वृद्धि के लिए, "
                f"धर्म, अर्थ, काम, मोक्ष चतुर्विध पुरुषार्थ सिद्धि के लिए, "
                f"इष्ट कामार्थ सिद्धि के लिए, श्री परमेश्वर की प्रसन्नता के लिए — "
                f"{pooja_s} करिष्ये ।{desires_s}"
            )

def _deva_tuple_to_en(dvipa_tuple, country):
    """Return English labels for dvipa info."""
    EN = {
        "india":        "Jambudweepe, BharataVarshe, BharataKhande, Meroh DakshinaDigbhaage",
        "canada":       "KrounChadweepe, RamanakVarshe, IndraKhande, Meroh PashchimaDigbhaage",
        "usa":          "KrounChadweepe, RamanakVarshe, IndraKhande, Meroh PashchimaDigbhaage",
        "united states":"KrounChadweepe, RamanakVarshe, IndraKhande, Meroh PashchimaDigbhaage",
        "australia":    "PushkaraDweepe, UttaraVarshe, PushkaraKhande, Meroh AgneyaDigbhaage",
        "uk":           "PlakshaDweepe, ShishiraVarshe, PlakshaKhande, Meroh PashchimottaraDigbhaage",
        "united kingdom":"PlakshaDweepe, ShishiraVarshe, PlakshaKhande, Meroh PashchimottaraDigbhaage",
        "south africa": "ShaalmalaDweepe, ShaalamaliVarshe, ShaalamaliKhande, Meroh DakshinaPashchimaDigbhaage",
        "brazil":       "ShaakaDweepe, ShaakaVarshe, ShaakaKhande, Meroh PashchimaDakshinaDigbhaage",
        "singapore":    "Jambudweepe, BharataVarshe, PurvaKhande, Meroh PurvaDigbhaage",
        "uae":          "Jambudweepe, BharataVarshe, PashchimaKhande, Meroh PashchimaDigbhaage",
    }
    return EN.get(country.lower().strip(),
        "Jambudweepe, BharataVarshe, BharataKhande, Meroh DakshinaDigbhaage")
