"""
sankalpam_generator.py (v6)

Builds one grammatically correct Sanskrit sankalpam (Devanagari) and renders it
in Telugu / Kannada / Tamil scripts, plus a romanised English version.
Each language also gets a real translation of the meaning in that language.
"""
import re, logging
from transliteration import name_to_deva, deva_to_script
logger = logging.getLogger(__name__)

SEP = "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"


def tidy(s: str) -> str:
    """Single spaces, no space before punctuation, one space after commas."""
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" +([,;.:)])", r"\1", s)
    s = re.sub(r"(?<=\S)॥", " ॥", s)
    s = re.sub(r"\( +", "(", s)
    s = re.sub(r",(?=\S)", ", ", s)
    s = re.sub(r"\n +", "\n", s)
    s = re.sub(r" +\n", "\n", s)
    return s.strip()


# ── Puranic geography: country → (dvipa, varsha, khanda, direction from Meru) ──
_JAMBU    = ("जम्बूद्वीपे", "भरतवर्षे", "भरतखण्डे", "मेरोः दक्षिणदिग्भागे")
_KRAUNCHA = ("क्रौञ्चद्वीपे", "रमणकवर्षे", "इन्द्रखण्डे", "मेरोः पश्चिमदिग्भागे")
_PLAKSHA  = ("प्लक्षद्वीपे", "शिशिरवर्षे", "प्लक्षखण्डे", "मेरोः पश्चिमोत्तरदिग्भागे")
_PUSHKARA = ("पुष्करद्वीपे", "उत्तरवर्षे", "पुष्करखण्डे", "मेरोः आग्नेयदिग्भागे")
_SHALMALI = ("शाल्मलिद्वीपे", "शाल्मलिवर्षे", "शाल्मलिखण्डे", "मेरोः नैर्ऋत्यदिग्भागे")
_SHAKA    = ("शाकद्वीपे", "शाकवर्षे", "शाकखण्डे", "मेरोः पश्चिमदक्षिणदिग्भागे")
_GULF     = ("जम्बूद्वीपे", "भरतवर्षे", "पश्चिमखण्डे", "मेरोः पश्चिमदिग्भागे")
_EAST     = ("जम्बूद्वीपे", "भरतवर्षे", "पूर्वखण्डे", "मेरोः पूर्वदिग्भागे")
_PAK      = ("जम्बूद्वीपे", "भरतवर्षे", "भरतखण्डे", "मेरोः पश्चिमदिग्भागे")

DVIPA = {
    "india": _JAMBU, "nepal": _JAMBU, "sri lanka": _JAMBU, "bangladesh": _JAMBU, "pakistan": _PAK,
    "usa": _KRAUNCHA, "united states": _KRAUNCHA, "united states of america": _KRAUNCHA,
    "canada": _KRAUNCHA, "mexico": _KRAUNCHA,
    "uk": _PLAKSHA, "united kingdom": _PLAKSHA, "germany": _PLAKSHA, "france": _PLAKSHA,
    "netherlands": _PLAKSHA, "sweden": _PLAKSHA, "italy": _PLAKSHA, "spain": _PLAKSHA, "ireland": _PLAKSHA,
    "australia": _PUSHKARA, "new zealand": _PUSHKARA,
    "south africa": _SHALMALI, "nigeria": _SHALMALI, "kenya": _SHALMALI,
    "brazil": _SHAKA, "argentina": _SHAKA,
    "uae": _GULF, "united arab emirates": _GULF, "qatar": _GULF, "oman": _GULF,
    "kuwait": _GULF, "saudi arabia": _GULF, "bahrain": _GULF,
    "singapore": _EAST, "malaysia": _EAST,
}

GEO_ROMAN = {
    "जम्बूद्वीपे": "Jambudvipe", "भरतवर्षे": "Bharatavarshe", "भरतखण्डे": "Bharatakhande",
    "क्रौञ्चद्वीपे": "Kraunchadvipe", "रमणकवर्षे": "Ramanakavarshe", "इन्द्रखण्डे": "Indrakhande",
    "प्लक्षद्वीपे": "Plakshadvipe", "शिशिरवर्षे": "Shishiravarshe", "प्लक्षखण्डे": "Plakshakhande",
    "पुष्करद्वीपे": "Pushkaradvipe", "उत्तरवर्षे": "Uttaravarshe", "पुष्करखण्डे": "Pushkarakhande",
    "शाल्मलिद्वीपे": "Shalmalidvipe", "शाल्मलिवर्षे": "Shalmalivarshe", "शाल्मलिखण्डे": "Shalmalikhande",
    "शाकद्वीपे": "Shakadvipe", "शाकवर्षे": "Shakavarshe", "शाकखण्डे": "Shakakhande",
    "पश्चिमखण्डे": "Pashchimakhande", "पूर्वखण्डे": "Purvakhande",
    "मेरोः दक्षिणदिग्भागे": "Meroh dakshina digbhage", "मेरोः पश्चिमदिग्भागे": "Meroh pashchima digbhage",
    "मेरोः पश्चिमोत्तरदिग्भागे": "Meroh pashchimottara digbhage", "मेरोः आग्नेयदिग्भागे": "Meroh agneya digbhage",
    "मेरोः नैर्ऋत्यदिग्भागे": "Meroh nairritya digbhage",
    "मेरोः पश्चिमदक्षिणदिग्भागे": "Meroh pashchima-dakshina digbhage",
    "मेरोः पूर्वदिग्भागे": "Meroh purva digbhage",
}

def get_dvipa(country): return DVIPA.get(country.lower().strip(), _JAMBU)


# ── Panchang tables (index-aligned with panchang_service) ────────────────────
TITHI_KEYS = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami",
              "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi",
              "Purnima", "Amavasya"]
TITHI_SA = ["प्रतिपदि", "द्वितीयायां", "तृतीयायां", "चतुर्थ्यां", "पञ्चम्यां", "षष्ठ्यां", "सप्तम्यां",
            "अष्टम्यां", "नवम्यां", "दशम्यां", "एकादश्यां", "द्वादश्यां", "त्रयोदश्यां", "चतुर्दश्यां",
            "पौर्णमास्यां", "अमावास्यायां"]
TITHI_RO = ["Pratipadi", "Dvitiyayam", "Tritiyayam", "Chaturthyam", "Panchamyam", "Shashthyam",
            "Saptamyam", "Ashtamyam", "Navamyam", "Dashamyam", "Ekadashyam", "Dvadashyam",
            "Trayodashyam", "Chaturdashyam", "Paurnamasyam", "Amavasyayam"]
TITHI_N = {
    "te": ["పాడ్యమి", "విదియ", "తదియ", "చవితి", "పంచమి", "షష్ఠి", "సప్తమి", "అష్టమి", "నవమి", "దశమి",
           "ఏకాదశి", "ద్వాదశి", "త్రయోదశి", "చతుర్దశి", "పౌర్ణమి", "అమావాస్య"],
    "kn": ["ಪಾಡ್ಯ", "ಬಿದಿಗೆ", "ತದಿಗೆ", "ಚೌತಿ", "ಪಂಚಮಿ", "ಷಷ್ಠಿ", "ಸಪ್ತಮಿ", "ಅಷ್ಟಮಿ", "ನವಮಿ", "ದಶಮಿ",
           "ಏಕಾದಶಿ", "ದ್ವಾದಶಿ", "ತ್ರಯೋದಶಿ", "ಚತುರ್ದಶಿ", "ಹುಣ್ಣಿಮೆ", "ಅಮಾವಾಸ್ಯೆ"],
    "ta": ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி",
           "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "அமாவாசை"],
    "hi": ["प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी",
           "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "पूर्णिमा", "अमावस्या"],
    "mr": ["प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी",
           "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "पौर्णिमा", "अमावास्या"],
}

VARA_KEYS = ["Ravivara", "Somavara", "Mangalavara", "Budhavara", "Guruvara", "Shukravara", "Shanivara"]
VARA_SA = ["भानुवासरे", "इन्दुवासरे", "भौमवासरे", "सौम्यवासरे", "गुरुवासरे", "भृगुवासरे", "स्थिरवासरे"]
VARA_RO = ["Bhanu vasare", "Indu vasare", "Bhauma vasare", "Saumya vasare", "Guru vasare",
           "Bhrigu vasare", "Sthira vasare"]
VARA_EN = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
VARA_N = {
    "te": ["ఆదివారం", "సోమవారం", "మంగళవారం", "బుధవారం", "గురువారం", "శుక్రవారం", "శనివారం"],
    "kn": ["ಭಾನುವಾರ", "ಸೋಮವಾರ", "ಮಂಗಳವಾರ", "ಬುಧವಾರ", "ಗುರುವಾರ", "ಶುಕ್ರವಾರ", "ಶನಿವಾರ"],
    "ta": ["ஞாயிற்றுக்கிழமை", "திங்கட்கிழமை", "செவ்வாய்க்கிழமை", "புதன்கிழமை", "வியாழக்கிழமை",
           "வெள்ளிக்கிழமை", "சனிக்கிழமை"],
    "hi": ["रविवार", "सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"],
    "mr": ["रविवार", "सोमवार", "मंगळवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"],
}

NAK_KEYS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya",
            "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
            "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
            "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
NAK_SA = ["अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशीर्ष", "आर्द्रा", "पुनर्वसु", "पुष्य", "आश्लेषा",
          "मघा", "पूर्वफल्गुनी", "उत्तरफल्गुनी", "हस्त", "चित्रा", "स्वाती", "विशाखा", "अनूराधा",
          "ज्येष्ठा", "मूला", "पूर्वाषाढा", "उत्तराषाढा", "श्रवण", "धनिष्ठा", "शतभिषक्", "पूर्वाभाद्रपदा",
          "उत्तराभाद्रपदा", "रेवती"]
NAK_RO = ["Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu", "Pushya",
          "Ashlesha", "Magha", "Purvaphalguni", "Uttaraphalguni", "Hasta", "Chitra", "Svati", "Vishakha",
          "Anuradha", "Jyeshtha", "Mula", "Purvashadha", "Uttarashadha", "Shravana", "Dhanishtha",
          "Shatabhishak", "Purvabhadrapada", "Uttarabhadrapada", "Revati"]
NAK_N = {
    "te": ["అశ్విని", "భరణి", "కృత్తిక", "రోహిణి", "మృగశిర", "ఆర్ద్ర", "పునర్వసు", "పుష్యమి", "ఆశ్లేష",
           "మఖ", "పుబ్బ", "ఉత్తర", "హస్త", "చిత్త", "స్వాతి", "విశాఖ", "అనూరాధ", "జ్యేష్ఠ", "మూల",
           "పూర్వాషాఢ", "ఉత్తరాషాఢ", "శ్రవణ", "ధనిష్ఠ", "శతభిష", "పూర్వాభాద్ర", "ఉత్తరాభాద్ర", "రేవతి"],
    "kn": ["ಅಶ್ವಿನಿ", "ಭರಣಿ", "ಕೃತ್ತಿಕಾ", "ರೋಹಿಣಿ", "ಮೃಗಶಿರ", "ಆರ್ದ್ರಾ", "ಪುನರ್ವಸು", "ಪುಷ್ಯ", "ಆಶ್ಲೇಷಾ",
           "ಮಘಾ", "ಪೂರ್ವಾಫಲ್ಗುಣಿ", "ಉತ್ತರಾಫಲ್ಗುಣಿ", "ಹಸ್ತ", "ಚಿತ್ರಾ", "ಸ್ವಾತಿ", "ವಿಶಾಖಾ", "ಅನೂರಾಧಾ",
           "ಜ್ಯೇಷ್ಠಾ", "ಮೂಲಾ", "ಪೂರ್ವಾಷಾಢಾ", "ಉತ್ತರಾಷಾಢಾ", "ಶ್ರವಣ", "ಧನಿಷ್ಠಾ", "ಶತಭಿಷಾ",
           "ಪೂರ್ವಾಭಾದ್ರಾ", "ಉತ್ತರಾಭಾದ್ರಾ", "ರೇವತಿ"],
    "ta": ["அசுவினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்",
           "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்",
           "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி",
           "உத்திரட்டாதி", "ரேவதி"],
    "hi": ["अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा", "पुनर्वसु", "पुष्य", "आश्लेषा",
           "मघा", "पूर्वाफाल्गुनी", "उत्तराफाल्गुनी", "हस्त", "चित्रा", "स्वाती", "विशाखा", "अनुराधा",
           "ज्येष्ठा", "मूल", "पूर्वाषाढ़ा", "उत्तराषाढ़ा", "श्रवण", "धनिष्ठा", "शतभिषा", "पूर्वाभाद्रपद",
           "उत्तराभाद्रपद", "रेवती"],
    "mr": ["अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृग", "आर्द्रा", "पुनर्वसू", "पुष्य", "आश्लेषा",
           "मघा", "पूर्वा", "उत्तरा", "हस्त", "चित्रा", "स्वाती", "विशाखा", "अनुराधा", "ज्येष्ठा", "मूळ",
           "पूर्वाषाढा", "उत्तराषाढा", "श्रवण", "धनिष्ठा", "शततारका", "पूर्वाभाद्रपदा", "उत्तराभाद्रपदा",
           "रेवती"],
}

YOGA_KEYS = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti",
             "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata",
             "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra",
             "Vaidhriti"]
YOGA_SA = ["विष्कम्भ", "प्रीति", "आयुष्मान्", "सौभाग्य", "शोभन", "अतिगण्ड", "सुकर्म", "धृति", "शूल", "गण्ड",
           "वृद्धि", "ध्रुव", "व्याघात", "हर्षण", "वज्र", "सिद्धि", "व्यतीपात", "वरीयान्", "परिघ", "शिव",
           "सिद्ध", "साध्य", "शुभ", "शुक्ल", "ब्रह्म", "ऐन्द्र", "वैधृति"]
YOGA_RO = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti",
           "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata",
           "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Aindra",
           "Vaidhriti"]

KARANA_KEYS = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti", "Shakuni",
               "Chatushpada", "Nagava", "Kimstughna"]
KARANA_SA = ["बव", "बालव", "कौलव", "तैतिल", "गरज", "वणिज", "विष्टि", "शकुनि", "चतुष्पात्", "नाग", "किंस्तुघ्न"]
KARANA_RO = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti", "Shakuni",
             "Chatushpat", "Naga", "Kimstughna"]

MASA_KEYS = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashwayuja", "Kartika",
             "Margashira", "Pushya", "Magha", "Phalguna"]
MASA_SA = ["चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ", "श्रावण", "भाद्रपद", "आश्वयुज", "कार्तिक", "मार्गशीर्ष",
           "पुष्य", "माघ", "फाल्गुन"]
MASA_RO = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvayuja", "Kartika",
           "Margashirsha", "Pushya", "Magha", "Phalguna"]
MASA_N = {
    "te": ["చైత్ర", "వైశాఖ", "జ్యేష్ఠ", "ఆషాఢ", "శ్రావణ", "భాద్రపద", "ఆశ్వయుజ", "కార్తీక", "మార్గశిర",
           "పుష్య", "మాఘ", "ఫాల్గుణ"],
    "kn": ["ಚೈತ್ರ", "ವೈಶಾಖ", "ಜ್ಯೇಷ್ಠ", "ಆಷಾಢ", "ಶ್ರಾವಣ", "ಭಾದ್ರಪದ", "ಆಶ್ವಯುಜ", "ಕಾರ್ತಿಕ", "ಮಾರ್ಗಶಿರ",
           "ಪುಷ್ಯ", "ಮಾಘ", "ಫಾಲ್ಗುಣ"],
    "ta": ["சைத்ர", "வைசாக", "ஜ்யேஷ்ட", "ஆஷாட", "சிராவண", "பாத்ரபத", "ஆஸ்வயுஜ", "கார்த்திக", "மார்கசீர்ஷ",
           "புஷ்ய", "மாக", "பால்குன"],
    "hi": ["चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ़", "श्रावण", "भाद्रपद", "आश्विन", "कार्तिक", "मार्गशीर्ष",
           "पौष", "माघ", "फाल्गुन"],
    "mr": ["चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ", "श्रावण", "भाद्रपद", "आश्विन", "कार्तिक", "मार्गशीर्ष",
           "पौष", "माघ", "फाल्गुन"],
}
# Tamil calendar: solar months; the sankalpam names them by the Sun's rashi
TAMIL_MASA_KEYS = ["Chithirai", "Vaikasi", "Aani", "Aadi", "Aavani", "Purattasi", "Aippasi", "Karthigai",
                   "Margazhi", "Thai", "Maasi", "Panguni"]
RASHI_SA = ["मेष", "वृषभ", "मिथुन", "कर्कटक", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनुर्", "मकर", "कुंभ", "मीन"]
RASHI_RO = ["Mesha", "Vrishabha", "Mithuna", "Karkataka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanur",
            "Makara", "Kumbha", "Mina"]
TAMIL_MASA_TA = ["சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி", "ஐப்பசி", "கார்த்திகை", "மார்கழி",
                 "தை", "மாசி", "பங்குனி"]

RITU_KEYS = ["Vasanta", "Grishma", "Varsha", "Sharada", "Hemanta", "Shishira"]
RITU_SA = ["वसन्तर्तौ", "ग्रीष्मर्तौ", "वर्षर्तौ", "शरदृतौ", "हेमन्तर्तौ", "शिशिरर्तौ"]
RITU_RO = ["Vasanta ritau", "Grishma ritau", "Varsha ritau", "Sharad ritau", "Hemanta ritau", "Shishira ritau"]
RITU_EN = ["spring", "summer", "monsoon", "autumn", "early winter", "late winter"]
RITU_N = {
    "te": ["వసంత ఋతువు", "గ్రీష్మ ఋతువు", "వర్ష ఋతువు", "శరదృతువు", "హేమంత ఋతువు", "శిశిర ఋతువు"],
    "kn": ["ವಸಂತ ಋತು", "ಗ್ರೀಷ್ಮ ಋತು", "ವರ್ಷ ಋತು", "ಶರದ್ ಋತು", "ಹೇಮಂತ ಋತು", "ಶಿಶಿರ ಋತು"],
    "ta": ["வசந்த ருது", "கிரீஷ்ம ருது", "வர்ஷ ருது", "சரத் ருது", "ஹேமந்த ருது", "சிசிர ருது"],
    "hi": ["वसंत ऋतु", "ग्रीष्म ऋतु", "वर्षा ऋतु", "शरद ऋतु", "हेमंत ऋतु", "शिशिर ऋतु"],
    "mr": ["वसंत ऋतू", "ग्रीष्म ऋतू", "वर्षा ऋतू", "शरद ऋतू", "हेमंत ऋतू", "शिशिर ऋतू"],
}

AYANA_SA = {"Uttarayana": "उत्तरायणे", "Dakshinayana": "दक्षिणायने"}
AYANA_RO = {"Uttarayana": "Uttarayane", "Dakshinayana": "Dakshinayane"}
AYANA_N = {
    "te": {"Uttarayana": "ఉత్తరాయణం", "Dakshinayana": "దక్షిణాయనం"},
    "kn": {"Uttarayana": "ಉತ್ತರಾಯಣ", "Dakshinayana": "ದಕ್ಷಿಣಾಯನ"},
    "ta": {"Uttarayana": "உத்தராயணம்", "Dakshinayana": "தட்சிணாயனம்"},
    "hi": {"Uttarayana": "उत्तरायण", "Dakshinayana": "दक्षिणायन"},
    "mr": {"Uttarayana": "उत्तरायण", "Dakshinayana": "दक्षिणायन"},
}
PAKSHA_N = {
    "te": ("శుక్ల పక్షం", "కృష్ణ పక్షం"), "kn": ("ಶುಕ್ಲ ಪಕ್ಷ", "ಕೃಷ್ಣ ಪಕ್ಷ"),
    "ta": ("சுக்ல பட்சம்", "கிருஷ்ண பட்சம்"), "hi": ("शुक्ल पक्ष", "कृष्ण पक्ष"),
    "mr": ("शुक्ल पक्ष", "कृष्ण पक्ष"),
}

SAMVAT_KEYS = ["Prabhava", "Vibhava", "Shukla", "Pramoduta", "Prajotpatti", "Angirasa", "Shrimukha", "Bhava",
               "Yuva", "Dhata", "Ishvara", "Bahudhanya", "Pramathi", "Vikrama", "Vrisha", "Chitrabhanu",
               "Svabhanu", "Tarana", "Parthiva", "Vyaya", "Sarvajit", "Sarvadhari", "Virodhi", "Vikruti",
               "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukhi", "Hevilambi", "Vilambi", "Vikari",
               "Sharvari", "Plava", "Shubhakrut", "Shobhakrut", "Krodhi", "Vishvavasu", "Parabhava",
               "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrut", "Paridhavi", "Pramadicha",
               "Ananda", "Rakshasa", "Nala", "Pingala", "Kalayukti", "Siddharthi", "Raudri", "Durmati",
               "Dundubhi", "Rudhirodgari", "Raktakshi", "Krodhana", "Akshaya"]
SAMVAT_SA = ["प्रभव", "विभव", "शुक्ल", "प्रमोदूत", "प्रजोत्पत्ति", "आंगीरस", "श्रीमुख", "भाव", "युव", "धाता",
             "ईश्वर", "बहुधान्य", "प्रमाथि", "विक्रम", "वृष", "चित्रभानु", "स्वभानु", "तारण", "पार्थिव", "व्यय",
             "सर्वजित्", "सर्वधारि", "विरोधि", "विकृति", "खर", "नन्दन", "विजय", "जय", "मन्मथ", "दुर्मुखि",
             "हेविलम्बि", "विलम्बि", "विकारि", "शार्वरि", "प्लव", "शुभकृत्", "शोभकृत्", "क्रोधि", "विश्वावसु",
             "पराभव", "प्लवंग", "कीलक", "सौम्य", "साधारण", "विरोधिकृत्", "परिधावि", "प्रमादीच", "आनन्द",
             "राक्षस", "नल", "पिंगल", "कालयुक्ति", "सिद्धार्थि", "रौद्रि", "दुर्मति", "दुन्दुभि", "रुधिरोद्गारि",
             "रक्ताक्षि", "क्रोधन", "अक्षय"]

# ── Poojas: deity to please + what is performed ──────────────────────────────
# mode: "vrata" / "puja" use shodashopachara wording; "karma" is a samskara/ritual.
# deity[lang] is already in the case the meaning sentence needs; name[lang] likewise.
_PARAMESHVARA = dict(
    preeti_sa="श्रीपरमेश्वरप्रीत्यर्थं", preeti_ro="Sri Parameshvara prityartham",
    deity_en="Sri Parameshvara",
    deity={"te": "శ్రీ పరమేశ్వరుని", "kn": "ಶ್ರೀ ಪರಮೇಶ್ವರನ", "ta": "ஸ்ரீ பரமேஸ்வரனின்",
           "hi": "श्री परमेश्वर की", "mr": "श्री परमेश्वराच्या"},
)
POOJAS = {
    "saubhagya gauri vratam": dict(
        mode="vrata", act_sa="सौभाग्यगौरीव्रतं", act_ro="Saubhagya Gauri vratam",
        preeti_sa="श्रीसौभाग्यगौरीदेवताप्रीत्यर्थं", preeti_ro="Sri Saubhagya Gauri devata prityartham",
        deity_en="Sri Saubhagya Gauri Devi", name_en="Saubhagya Gauri Vratam",
        deity={"te": "శ్రీ సౌభాగ్య గౌరీ దేవి", "kn": "ಶ್ರೀ ಸೌಭಾಗ್ಯ ಗೌರೀ ದೇವಿಯ", "ta": "ஸ்ரீ சௌபாக்கிய கௌரி தேவியின்",
               "hi": "श्री सौभाग्य गौरी देवी की", "mr": "श्री सौभाग्य गौरी देवीच्या"},
        name={"te": "సౌభాగ్య గౌరీ వ్రతం", "kn": "ಸೌಭಾಗ್ಯ ಗೌರೀ ವ್ರತವನ್ನು", "ta": "சௌபாக்கிய கௌரி விரதத்தை",
              "hi": "सौभाग्य गौरी व्रत", "mr": "सौभाग्य गौरी व्रत"}),
    "ganesh puja": dict(
        mode="puja", act_sa="श्रीमहागणपतिपूजां", act_ro="Sri Mahaganapati pujam",
        preeti_sa="श्रीमहागणपतिप्रीत्यर्थं", preeti_ro="Sri Mahaganapati prityartham",
        deity_en="Sri Mahaganapati", name_en="Ganesh Puja",
        deity={"te": "శ్రీ మహాగణపతి", "kn": "ಶ್ರೀ ಮಹಾಗಣಪತಿಯ", "ta": "ஸ்ரீ மகா கணபதியின்",
               "hi": "श्री महागणपति की", "mr": "श्री महागणपतीच्या"},
        name={"te": "గణపతి పూజ", "kn": "ಗಣಪತಿ ಪೂಜೆಯನ್ನು", "ta": "கணபதி பூஜையை",
              "hi": "गणपति पूजा", "mr": "गणपती पूजा"}),
    "lakshmi puja": dict(
        mode="puja", act_sa="श्रीमहालक्ष्मीपूजां", act_ro="Sri Mahalakshmi pujam",
        preeti_sa="श्रीमहालक्ष्मीप्रीत्यर्थं", preeti_ro="Sri Mahalakshmi prityartham",
        deity_en="Sri Mahalakshmi", name_en="Lakshmi Puja",
        deity={"te": "శ్రీ మహాలక్ష్మి", "kn": "ಶ್ರೀ ಮಹಾಲಕ್ಷ್ಮಿಯ", "ta": "ஸ்ரீ மகாலட்சுமியின்",
               "hi": "श्री महालक्ष्मी की", "mr": "श्री महालक्ष्मीच्या"},
        name={"te": "లక్ష్మీ పూజ", "kn": "ಲಕ್ಷ್ಮೀ ಪೂಜೆಯನ್ನು", "ta": "லட்சுமி பூஜையை",
              "hi": "लक्ष्मी पूजा", "mr": "लक्ष्मी पूजा"}),
    "satyanarayana puja": dict(
        mode="vrata", act_sa="श्रीसत्यनारायणव्रतं", act_ro="Sri Satyanarayana vratam",
        preeti_sa="श्रीसत्यनारायणस्वामिप्रीत्यर्थं", preeti_ro="Sri Satyanarayana Svami prityartham",
        deity_en="Sri Satyanarayana Swami", name_en="Satyanarayana Vratam",
        deity={"te": "శ్రీ సత్యనారాయణ స్వామి", "kn": "ಶ್ರೀ ಸತ್ಯನಾರಾಯಣ ಸ್ವಾಮಿಯ", "ta": "ஸ்ரீ சத்தியநாராயண சுவாமியின்",
               "hi": "श्री सत्यनारायण भगवान की", "mr": "श्री सत्यनारायणाच्या"},
        name={"te": "సత్యనారాయణ స్వామి వ్రతం", "kn": "ಸತ್ಯನಾರಾಯಣ ವ್ರತವನ್ನು", "ta": "சத்தியநாராயண விரதத்தை",
              "hi": "सत्यनारायण व्रत", "mr": "सत्यनारायण व्रत"}),
    "navagraha puja": dict(
        mode="puja", act_sa="नवग्रहपूजां", act_ro="Navagraha pujam",
        preeti_sa="नवग्रहदेवताप्रीत्यर्थं", preeti_ro="Navagraha devata prityartham",
        deity_en="the Navagraha deities", name_en="Navagraha Puja",
        deity={"te": "నవగ్రహ దేవతల", "kn": "ನವಗ್ರಹ ದೇವತೆಗಳ", "ta": "நவக்கிரக தேவதைகளின்",
               "hi": "नवग्रह देवताओं की", "mr": "नवग्रह देवतांच्या"},
        name={"te": "నవగ్రహ పూజ", "kn": "ನವಗ್ರಹ ಪೂಜೆಯನ್ನು", "ta": "நவக்கிரக பூஜையை",
              "hi": "नवग्रह पूजा", "mr": "नवग्रह पूजा"}),
    "rudrabhishekam": dict(
        mode="karma", act_sa="रुद्राभिषेकं", act_ro="Rudrabhishekam",
        preeti_sa="श्रीसाम्बपरमेश्वरप्रीत्यर्थं", preeti_ro="Sri Samba Parameshvara prityartham",
        deity_en="Sri Samba Parameshvara", name_en="Rudrabhishekam",
        deity={"te": "శ్రీ సాంబ పరమేశ్వరుని", "kn": "ಶ್ರೀ ಸಾಂಬ ಪರಮೇಶ್ವರನ", "ta": "ஸ்ரீ சாம்ப பரமேஸ்வரனின்",
               "hi": "श्री साम्ब परमेश्वर की", "mr": "श्री सांब परमेश्वराच्या"},
        name={"te": "రుద్రాభిషేకం", "kn": "ರುದ್ರಾಭಿಷೇಕವನ್ನು", "ta": "ருத்ராபிஷேகத்தை",
              "hi": "रुद्राभिषेक", "mr": "रुद्राभिषेक"}),
    "ayushya homa": dict(
        mode="karma", act_sa="आयुष्यहोमं", act_ro="Ayushya homam",
        preeti_sa="आयुर्देवताप्रीत्यर्थं", preeti_ro="Ayur devata prityartham",
        deity_en="Ayur Devata", name_en="Ayushya Homam",
        deity={"te": "ఆయుర్దేవత", "kn": "ಆಯುರ್ದೇವತೆಯ", "ta": "ஆயுர்தேவதையின்",
               "hi": "आयुर्देवता की", "mr": "आयुर्देवतेच्या"},
        name={"te": "ఆయుష్య హోమం", "kn": "ಆಯುಷ್ಯ ಹೋಮವನ್ನು", "ta": "ஆயுஷ்ய ஹோமத்தை",
              "hi": "आयुष्य होम", "mr": "आयुष्य होम"}),
    "grihapravesham": dict(
        mode="karma", act_sa="गृहप्रवेशकर्म", act_ro="Grihapravesha karma", name_en="Grihapravesham",
        name={"te": "గృహప్రవేశం", "kn": "ಗೃಹಪ್ರವೇಶವನ್ನು", "ta": "கிரகப்பிரவேசத்தை",
              "hi": "गृहप्रवेश", "mr": "गृहप्रवेश"}, **_PARAMESHVARA),
    "vivah (wedding)": dict(
        mode="karma", act_sa="विवाहकर्म", act_ro="Vivaha karma", name_en="Vivaha (wedding)",
        name={"te": "వివాహం", "kn": "ವಿವಾಹವನ್ನು", "ta": "விவாகத்தை",
              "hi": "विवाह संस्कार", "mr": "विवाह संस्कार"}, **_PARAMESHVARA),
    "upanayanam": dict(
        mode="karma", act_sa="उपनयनकर्म", act_ro="Upanayana karma", name_en="Upanayanam",
        name={"te": "ఉపనయనం", "kn": "ಉಪನಯನವನ್ನು", "ta": "உபநயனத்தை",
              "hi": "उपनयन संस्कार", "mr": "उपनयन संस्कार"}, **_PARAMESHVARA),
    "namakaranam": dict(
        mode="karma", act_sa="नामकरणकर्म", act_ro="Namakarana karma", name_en="Namakaranam",
        name={"te": "నామకరణం", "kn": "ನಾಮಕರಣವನ್ನು", "ta": "நாமகரணத்தை",
              "hi": "नामकरण संस्कार", "mr": "नामकरण संस्कार"}, **_PARAMESHVARA),
    "annaprasana": dict(
        mode="karma", act_sa="अन्नप्राशनकर्म", act_ro="Annaprashana karma", name_en="Annaprashana",
        name={"te": "అన్నప్రాశనం", "kn": "ಅನ್ನಪ್ರಾಶನವನ್ನು", "ta": "அன்னப்பிராசனத்தை",
              "hi": "अन्नप्राशन संस्कार", "mr": "अन्नप्राशन संस्कार"}, **_PARAMESHVARA),
    "seemantham": dict(
        mode="karma", act_sa="सीमन्तोन्नयनकर्म", act_ro="Simantonnayana karma", name_en="Seemantham",
        name={"te": "సీమంతం", "kn": "ಸೀಮಂತವನ್ನು", "ta": "சீமந்தத்தை",
              "hi": "सीमंतोन्नयन संस्कार", "mr": "सीमंतोन्नयन संस्कार"}, **_PARAMESHVARA),
    "vastu puja": dict(
        mode="puja", act_sa="वास्तुपूजां", act_ro="Vastu pujam",
        preeti_sa="श्रीवास्तुपुरुषप्रीत्यर्थं", preeti_ro="Sri Vastupurusha prityartham",
        deity_en="Sri Vastu Purusha", name_en="Vastu Puja",
        deity={"te": "శ్రీ వాస్తు పురుషుని", "kn": "ಶ್ರೀ ವಾಸ್ತು ಪುರುಷನ", "ta": "ஸ்ரீ வாஸ்து புருஷரின்",
               "hi": "श्री वास्तु पुरुष की", "mr": "श्री वास्तुपुरुषाच्या"},
        name={"te": "వాస్తు పూజ", "kn": "ವಾಸ್ತು ಪೂಜೆಯನ್ನು", "ta": "வாஸ்து பூஜையை",
              "hi": "वास्तु पूजा", "mr": "वास्तु पूजा"}),
    "durga puja": dict(
        mode="puja", act_sa="श्रीदुर्गापूजां", act_ro="Sri Durga pujam",
        preeti_sa="श्रीदुर्गापरमेश्वरीप्रीत्यर्थं", preeti_ro="Sri Durga Parameshvari prityartham",
        deity_en="Sri Durga Parameshvari", name_en="Durga Puja",
        deity={"te": "శ్రీ దుర్గా పరమేశ్వరి", "kn": "ಶ್ರೀ ದುರ್ಗಾ ಪರಮೇಶ್ವರಿಯ", "ta": "ஸ்ரீ துர்கா பரமேஸ்வரியின்",
               "hi": "श्री दुर्गा परमेश्वरी की", "mr": "श्री दुर्गा परमेश्वरीच्या"},
        name={"te": "దుర్గా పూజ", "kn": "ದುರ್ಗಾ ಪೂಜೆಯನ್ನು", "ta": "துர்கா பூஜையை",
              "hi": "दुर्गा पूजा", "mr": "दुर्गा पूजा"}),
    "karthika deepam": dict(
        mode="karma", act_sa="कार्तिकदीपदानं", act_ro="Kartika dipadanam", name_en="Kartika Deepam",
        name={"te": "కార్తీక దీపారాధన", "kn": "ಕಾರ್ತಿಕ ದೀಪಾರಾಧನೆಯನ್ನು", "ta": "கார்த்திகை தீப வழிபாட்டை",
              "hi": "कार्तिक दीपदान", "mr": "कार्तिक दीपदान"}, **_PARAMESHVARA),
}

def get_pooja(raw: str) -> dict:
    p = POOJAS.get(raw.lower().strip())
    if p:
        return p
    # custom pooja typed by the user: transliterate its name
    deva = name_to_deva(raw.strip() or "Pooja")
    name = {"te": deva_to_script(deva, "telugu"), "kn": deva_to_script(deva, "kannada") + " ಅನ್ನು",
            "ta": deva_to_script(deva, "tamil") + " என்பதை", "hi": deva, "mr": deva}
    return dict(mode="karma", act_sa=deva, act_ro=raw.strip(), name_en=raw.strip(), name=name,
                **_PARAMESHVARA)


# ── Rivers: nearest known river to the location ──────────────────────────────
RIVERS = [
    (27.90, 78.10, "Ganga", "गंगा"), (25.32, 82.97, "Ganga", "गंगा"), (22.57, 88.36, "Ganga", "गंगा"),
    (16.50, 80.62, "Krishna", "कृष्णा"), (17.38, 78.48, "Musi", "मूसी"), (13.08, 80.27, "Kaveri", "कावेरी"),
    (12.97, 77.59, "Kaveri", "कावेरी"), (18.52, 73.85, "Bhima", "भीमा"), (19.07, 72.87, "Godavari", "गोदावरी"),
    (17.00, 81.80, "Godavari", "गोदावरी"), (17.69, 83.22, "Godavari", "गोदावरी"),
    (13.63, 79.42, "Swarnamukhi", "स्वर्णमुखी"), (26.84, 80.94, "Gomati", "गोमती"),
    (15.83, 78.04, "Tungabhadra", "तुंगभद्रा"), (14.40, 75.73, "Tungabhadra", "तुंगभद्रा"),
    (8.50, 76.95, "Pamba", "पंपा"), (9.93, 78.12, "Vaigai", "वैगै"), (21.15, 79.09, "Godavari", "गोदावरी"),
    (28.61, 77.21, "Yamuna", "यमुना"), (23.02, 72.57, "Sabarmati", "साबरमती"),
    (20.30, 85.82, "Mahanadi", "महानदी"),
    (49.19, -122.84, "Fraser", "फ्रेजर"), (43.70, -79.42, "Humber", "हंबर"),
    (45.50, -73.56, "St. Lawrence", "सेंट लॉरेंस"), (51.05, -114.07, "Bow", "बो"),
    (53.55, -113.49, "North Saskatchewan", "सस्केचवन"), (45.42, -75.70, "Ottawa", "ओटावा"),
    (40.71, -74.00, "Hudson", "हडसन"), (47.60, -122.33, "Duwamish", "डुवामिश"),
    (37.34, -121.89, "Guadalupe", "ग्वाडालूप"), (34.05, -118.24, "Los Angeles", "लॉस एंजेलिस"),
    (29.76, -95.36, "Buffalo Bayou", "बफेलो बायू"), (32.78, -96.80, "Trinity", "ट्रिनिटी"),
    (41.88, -87.62, "Chicago", "शिकागो"), (38.89, -77.03, "Potomac", "पोटोमैक"),
    (33.75, -84.39, "Chattahoochee", "चट्टाहूची"), (44.97, -93.27, "Mississippi", "मिसिसिपी"),
    (51.50, -0.12, "Thames", "टेम्स"), (48.85, 2.35, "Seine", "सेन"), (52.52, 13.40, "Spree", "श्प्री"),
    (-33.86, 151.20, "Parramatta", "पर्रामट्टा"), (-37.81, 144.96, "Yarra", "यारा"),
    (-27.46, 153.02, "Brisbane", "ब्रिस्बेन"), (-31.95, 115.86, "Swan", "स्वान"),
    (-33.92, 18.42, "Liesbeek", "लीस्बीक"), (-23.55, -46.63, "Tiete", "तिएते"),
    (1.35, 103.82, "Kallang", "कल्लंग"), (25.20, 55.27, "Dubai Creek", "दुबई क्रीक"),
]

def get_nearest_river(lat, lon):
    best = min(RIVERS, key=lambda r: (r[0] - lat) ** 2 + (r[1] - lon) ** 2)
    return best[2], best[3]


# ── Script helpers ───────────────────────────────────────────────────────────
SCRIPT = {"te": "telugu", "kn": "kannada", "ta": "tamil", "hi": "devanagari", "mr": "devanagari"}

def in_script(deva: str, lang: str) -> str:
    return deva_to_script(deva, SCRIPT[lang])

def stem_native(deva: str, lang: str) -> str:
    """Sanskrit stem → natural spelling of the word in that language."""
    s = in_script(deva, lang)
    if lang == "te":
        s = re.sub("ా$", "", s)
        s = re.sub("ీ$", "ి", s)
    elif lang == "kn":
        s = re.sub("ೀ$", "ಿ", s)
    return s


# Correct native spellings for common places (Devanagari cannot express the
# short e/o of Telugu/Kannada/Tamil, so plain transliteration misspells them).
#            key: (te, kn, ta, hi, mr)
PLACE_NATIVE = {
    "india": ("భారతదేశం", "ಭಾರತ", "இந்தியா", "भारत", "भारत"),
    "telangana": ("తెలంగాణ", "ತೆಲಂಗಾಣ", "தெலங்கானா", "तेलंगाना", "तेलंगणा"),
    "andhra pradesh": ("ఆంధ్రప్రదేశ్", "ಆಂಧ್ರಪ್ರದೇಶ", "ஆந்திரப் பிரதேசம்", "आंध्र प्रदेश", "आंध्र प्रदेश"),
    "karnataka": ("కర్ణాటక", "ಕರ್ನಾಟಕ", "கர்நாடகா", "कर्नाटक", "कर्नाटक"),
    "tamil nadu": ("తమిళనాడు", "ತಮಿಳುನಾಡು", "தமிழ்நாடு", "तमिलनाडु", "तामिळनाडू"),
    "maharashtra": ("మహారాష్ట్ర", "ಮಹಾರಾಷ್ಟ್ರ", "மகாராஷ்டிரா", "महाराष्ट्र", "महाराष्ट्र"),
    "kerala": ("కేరళ", "ಕೇರಳ", "கேரளா", "केरल", "केरळ"),
    "hyderabad": ("హైదరాబాద్", "ಹೈದರಾಬಾದ್", "ஹைதராபாத்", "हैदराबाद", "हैदराबाद"),
    "secunderabad": ("సికింద్రాబాద్", "ಸಿಕಂದರಾಬಾದ್", "செகந்திராபாத்", "सिकंदराबाद", "सिकंदराबाद"),
    "warangal": ("వరంగల్", "ವರಂಗಲ್", "வாரங்கல்", "वारंगल", "वारंगळ"),
    "karimnagar": ("కరీంనగర్", "ಕರೀಂನಗರ", "கரீம்நகர்", "करीमनगर", "करीमनगर"),
    "khammam": ("ఖమ్మం", "ಖಮ್ಮಂ", "கம்மம்", "खम्मम", "खम्मम"),
    "nizamabad": ("నిజామాబాద్", "ನಿಜಾಮಾಬಾದ್", "நிஜாமாபாத்", "निजामाबाद", "निजामाबाद"),
    "vijayawada": ("విజయవాడ", "ವಿಜಯವಾಡ", "விஜயவாடா", "विजयवाड़ा", "विजयवाडा"),
    "visakhapatnam": ("విశాఖపట్నం", "ವಿಶಾಖಪಟ್ಟಣ", "விசாகப்பட்டினம்", "विशाखापत्तनम", "विशाखापट्टणम"),
    "guntur": ("గుంటూరు", "ಗುಂಟೂರು", "குண்டூர்", "गुंटूर", "गुंटूर"),
    "tirupati": ("తిరుపతి", "ತಿರುಪತಿ", "திருப்பதி", "तिरुपति", "तिरुपती"),
    "nellore": ("నెల్లూరు", "ನೆಲ್ಲೂರು", "நெல்லூர்", "नेल्लोर", "नेल्लोर"),
    "kurnool": ("కర్నూలు", "ಕರ್ನೂಲು", "கர்னூல்", "कुरनूल", "कुर्नूल"),
    "rajahmundry": ("రాజమండ్రి", "ರಾಜಮಂಡ್ರಿ", "ராஜமுந்திரி", "राजमुंदरी", "राजमुंद्री"),
    "kakinada": ("కాకినాడ", "ಕಾಕಿನಾಡ", "காக்கிநாடா", "काकीनाडा", "काकीनाडा"),
    "anantapur": ("అనంతపురం", "ಅನಂತಪುರ", "அனந்தபூர்", "अनंतपुर", "अनंतपूर"),
    "bengaluru": ("బెంగళూరు", "ಬೆಂಗಳೂರು", "பெங்களூரு", "बेंगलुरु", "बंगळुरू"),
    "bangalore": ("బెంగళూరు", "ಬೆಂಗಳೂರು", "பெங்களூரு", "बेंगलुरु", "बंगळुरू"),
    "mysuru": ("మైసూరు", "ಮೈಸೂರು", "மைசூரு", "मैसूरु", "म्हैसूर"),
    "chennai": ("చెన్నై", "ಚೆನ್ನೈ", "சென்னை", "चेन्नई", "चेन्नई"),
    "coimbatore": ("కోయంబత్తూరు", "ಕೊಯಮತ್ತೂರು", "கோயம்புத்தூர்", "कोयंबटूर", "कोइम्बतूर"),
    "madurai": ("మదురై", "ಮಧುರೈ", "மதுரை", "मदुरै", "मदुराई"),
    "mumbai": ("ముంబై", "ಮುಂಬೈ", "மும்பை", "मुंबई", "मुंबई"),
    "pune": ("పుణె", "ಪುಣೆ", "புனே", "पुणे", "पुणे"),
    "new delhi": ("న్యూఢిల్లీ", "ನವದೆಹಲಿ", "புது தில்லி", "नई दिल्ली", "नवी दिल्ली"),
    "delhi": ("ఢిల్లీ", "ದೆಹಲಿ", "தில்லி", "दिल्ली", "दिल्ली"),
    "kolkata": ("కోల్‌కతా", "ಕೋಲ್ಕತ್ತಾ", "கொல்கத்தா", "कोलकाता", "कोलकाता"),
    "canada": ("కెనడా", "ಕೆನಡಾ", "கனடா", "कनाडा", "कॅनडा"),
    "united states": ("అమెరికా", "ಅಮೆರಿಕ", "அமெரிக்கா", "अमेरिका", "अमेरिका"),
    "usa": ("అమెరికా", "ಅಮೆರಿಕ", "அமெரிக்கா", "अमेरिका", "अमेरिका"),
    "united kingdom": ("బ్రిటన్", "ಬ್ರಿಟನ್", "பிரிட்டன்", "ब्रिटेन", "ब्रिटन"),
    "australia": ("ఆస్ట్రేలియా", "ಆಸ್ಟ್ರೇಲಿಯಾ", "ஆஸ்திரேலியா", "ऑस्ट्रेलिया", "ऑस्ट्रेलिया"),
    "singapore": ("సింగపూర్", "ಸಿಂಗಾಪುರ", "சிங்கப்பூர்", "सिंगापुर", "सिंगापूर"),
}
_PL_IDX = {"te": 0, "kn": 1, "ta": 2, "hi": 3, "mr": 4, "sa": 3}

def place_name(latin: str, L: str) -> str:
    """Place name in language L (sa = Devanagari used inside the Sanskrit text)."""
    hit = PLACE_NATIVE.get(latin.lower().strip())
    if hit:
        return hit[_PL_IDX[L]]
    deva = name_to_deva(latin)
    return deva if L in ("sa", "hi", "mr") else in_script(deva, L)


class SankalpamGenerator:

    def generate_all_languages(self, panchang, form_data, location):
        c = self._ctx(panchang, form_data, location)
        deva = self._build_sanskrit(c, "sa")
        meaning_en = tidy("Meaning — " + self._meaning_en(c))
        return {
            "sanskrit": tidy(deva) + SEP + meaning_en,
            "english":  tidy(self._build_roman(c)) + SEP + meaning_en,
            "telugu":   tidy(in_script(self._build_sanskrit(c, "te"), "te")) + SEP + tidy(self._meaning(c, "te")),
            "tamil":    tidy(in_script(self._build_sanskrit(c, "ta"), "ta")) + SEP + tidy(self._meaning(c, "ta")),
            "kannada":  tidy(in_script(self._build_sanskrit(c, "kn"), "kn")) + SEP + tidy(self._meaning(c, "kn")),
            "marathi":  tidy(deva) + SEP + tidy(self._meaning(c, "mr")),
            "hindi":    tidy(deva) + SEP + tidy(self._meaning(c, "hi")),
        }

    # ── context ──────────────────────────────────────────────────────────────
    def _ctx(self, panchang, form_data, location):
        def idx(keys, val):
            return keys.index(val) if val in keys else 0

        country = (form_data.get("country") or "India").strip()
        state = (form_data.get("state") or "").strip()
        city = (form_data.get("city") or "").strip()
        river_en, river_sa = get_nearest_river(location.get("latitude", 17.38), location.get("longitude", 78.48))

        tithi = panchang["tithi"]
        if tithi == "Purnima/Amavasya":
            tithi = "Purnima" if "Shukla" in panchang["paksha"] else "Amavasya"

        masa = panchang["masa"]
        adhika = masa.startswith("Adhika ")
        masa = masa.replace("Adhika ", "")
        tamil_cal = masa in TAMIL_MASA_KEYS

        members = [m.strip() for m in (form_data.get("other_members") or "").split(",") if m.strip()]

        return dict(
            country=country, state=state, city=city,
            india=country.lower() in ("india", "bharat", "bharata"),
            river_en=river_en, river_sa=river_sa, dvipa=get_dvipa(country),
            samvat=idx(SAMVAT_KEYS, panchang["samvatsara"]), ayana=panchang["ayana"],
            ritu=idx(RITU_KEYS, panchang["ritu"]),
            masa=idx(TAMIL_MASA_KEYS if tamil_cal else MASA_KEYS, masa),
            tamil_cal=tamil_cal, adhika=adhika, shukla="Shukla" in panchang["paksha"],
            tithi=idx(TITHI_KEYS, tithi), vara=idx(VARA_KEYS, panchang["vara"]),
            nak=idx(NAK_KEYS, panchang["nakshatra"]), yoga=idx(YOGA_KEYS, panchang["yoga"]),
            karana=idx(KARANA_KEYS, panchang["karana"]),
            name=(form_data.get("name") or "").strip(), gothram=(form_data.get("gothram") or "").strip(),
            patni=(form_data.get("dharma_patni_name") or "").strip(), members=members,
            desires=(form_data.get("desires") or "").strip(),
            pooja=get_pooja(form_data.get("pooja_name") or ""),
        )

    # ── Sanskrit (Devanagari) ────────────────────────────────────────────────
    def _place_sa(self, c, L):
        parts = []
        if not c["india"]:
            parts.append(f"{place_name(c['country'], L)} देशे")
        if c["state"]:
            parts.append(f"{place_name(c['state'], L)} राज्ये")
        if c["city"]:
            parts.append(f"{place_name(c['city'], L)} नगरे")
        parts.append(f"{c['river_sa']} नद्याः समीपे")
        return ", ".join(parts)

    def _build_sanskrit(self, c, L="sa"):
        """Devanagari sankalpam; place names already in language L's spelling."""
        p = c["pooja"]
        d = c["dvipa"]
        masa = ("अधिक" if c["adhika"] else "") + \
            (RASHI_SA[c["masa"]] if c["tamil_cal"] else MASA_SA[c["masa"]]) + "मासे"
        person = f"श्रीमान् {name_to_deva(c['gothram'])}गोत्रः {name_to_deva(c['name'])} नामधेयः"
        if c["patni"]:
            person += f", {name_to_deva(c['patni'])} नाम्न्या धर्मपत्न्या सह"
        if c["members"]:
            person += ", " + ", ".join(name_to_deva(m) for m in c["members"]) + " इत्येतैः सह"
        if p["mode"] == "vrata":
            act = f"यथाशक्ति ध्यानावाहनादिषोडशोपचारपूजापूर्वकं {p['act_sa']}"
        elif p["mode"] == "puja":
            act = f"यथाशक्ति ध्यानावाहनादिषोडशोपचारैः {p['act_sa']}"
        else:
            act = f"यथाशक्ति {p['act_sa']}"
        desires = f"\n(संकल्पितकामना: {c['desires']})" if c["desires"] else ""
        return (
            "ॐ। ममोपात्तसमस्तदुरितक्षयद्वारा श्रीपरमेश्वरप्रीत्यर्थं, शुभे शोभने मुहूर्ते, "
            "श्रीमहाविष्णोराज्ञया प्रवर्तमानस्य, अद्य ब्रह्मणः द्वितीयपरार्धे, श्वेतवराहकल्पे, "
            "वैवस्वतमन्वन्तरे, कलियुगे, प्रथमपादे, "
            f"{d[0]}, {d[1]}, {d[2]}, {d[3]}, {self._place_sa(c, L)}, "
            "अस्मिन् वर्तमाने व्यावहारिकचान्द्रमानेन, "
            f"{SAMVAT_SA[c['samvat']]} नाम संवत्सरे, {AYANA_SA[c['ayana']]}, {RITU_SA[c['ritu']]}, "
            f"{masa}, {'शुक्लपक्षे' if c['shukla'] else 'कृष्णपक्षे'}, "
            f"{TITHI_SA[c['tithi']]} शुभतिथौ, {VARA_SA[c['vara']]}, "
            f"{NAK_SA[c['nak']]}नक्षत्रे, {YOGA_SA[c['yoga']]} योगे, {KARANA_SA[c['karana']]}करणे, "
            "एवंगुणविशेषणविशिष्टायाम् अस्यां शुभतिथौ, "
            f"{person}, "
            "मम सकुटुम्बस्य क्षेमस्थैर्यवीर्यविजयायुरारोग्यैश्वर्याभिवृद्ध्यर्थं, "
            "धर्मार्थकाममोक्षचतुर्विधफलपुरुषार्थसिद्ध्यर्थं, इष्टकाम्यार्थसिद्ध्यर्थं, "
            f"{p['preeti_sa']}, {act} करिष्ये ॥{desires}"
        )

    # ── Romanised (English tab) ──────────────────────────────────────────────
    def _build_roman(self, c):
        p = c["pooja"]
        geo = ", ".join(GEO_ROMAN[x] for x in c["dvipa"])
        place = []
        if not c["india"]:
            place.append(f"{c['country']} deshe")
        if c["state"]:
            place.append(f"{c['state']} rajye")
        if c["city"]:
            place.append(f"{c['city']} nagare")
        place.append(f"{c['river_en']} nadyah samipe")
        masa = ("Adhika " if c["adhika"] else "") + \
            (RASHI_RO[c["masa"]] if c["tamil_cal"] else MASA_RO[c["masa"]]) + " mase"
        person = f"Shriman {c['gothram']} gotrah {c['name']} namadheyah"
        if c["patni"]:
            person += f", {c['patni']} namnya dharmapatnya saha"
        if c["members"]:
            person += ", " + ", ".join(c["members"]) + " ityetaih saha"
        if p["mode"] == "vrata":
            act = f"yathashakti dhyana avahanadi shodashopachara puja purvakam {p['act_ro']}"
        elif p["mode"] == "puja":
            act = f"yathashakti dhyana avahanadi shodashopacharaih {p['act_ro']}"
        else:
            act = f"yathashakti {p['act_ro']}"
        desires = f"\n(Personal wishes: {c['desires']})" if c["desires"] else ""
        return (
            "Om. Mamopatta samasta duritakshaya dvara Sri Parameshvara prityartham, shubhe shobhane "
            "muhurte, Sri Mahavishnor ajnaya pravartamanasya, adya Brahmanah dvitiya parardhe, "
            "Shvetavaraha kalpe, Vaivasvata manvantare, Kaliyuge, prathama pade, "
            f"{geo}, {', '.join(place)}, asmin vartamane vyavaharika chandramanena, "
            f"{SAMVAT_KEYS[c['samvat']]} nama samvatsare, {AYANA_RO[c['ayana']]}, {RITU_RO[c['ritu']]}, "
            f"{masa}, {'Shukla pakshe' if c['shukla'] else 'Krishna pakshe'}, "
            f"{TITHI_RO[c['tithi']]} shubha tithau, {VARA_RO[c['vara']]}, "
            f"{NAK_RO[c['nak']]} nakshatre, {YOGA_RO[c['yoga']]} yoge, {KARANA_RO[c['karana']]} karane, "
            "evam guna visheshana vishishtayam asyam shubha tithau, "
            f"{person}, mama sakutumbasya kshema sthairya virya vijaya ayur arogya aishvarya "
            "abhivriddhyartham, dharma artha kama moksha chaturvidha phala purushartha siddhyartham, "
            f"ishta kamyartha siddhyartham, {p['preeti_ro']}, {act} karishye.{desires}"
        )

    # ── Meanings ─────────────────────────────────────────────────────────────
    def _meaning_en(self, c):
        p = c["pooja"]
        masa = (TAMIL_MASA_KEYS if c["tamil_cal"] else MASA_RO)[c["masa"]]
        if c["adhika"]:
            masa = "Adhika " + masa
        place = ", ".join(x for x in (c["city"], c["state"], c["country"]) if x)
        with_ = ""
        if c["patni"]:
            with_ += f", together with my wife {c['patni']}"
        if c["members"]:
            m = c["members"]
            names = m[0] if len(m) == 1 else ", ".join(m[:-1]) + " and " + m[-1]
            with_ += (" and with " if c["patni"] else ", together with ") + names
        wishes = f"\n(Personal wishes: {c['desires']})" if c["desires"] else ""
        return (
            "To remove all my accumulated sins and to please the Supreme Lord, at this auspicious "
            "moment, in the age governed by the command of Sri Maha Vishnu — in the second half of "
            "Brahma's life, in the Shveta Varaha Kalpa, in the Vaivasvata Manvantara, in the first "
            f"quarter of Kali Yuga — at {place}, near the {c['river_en']} river, "
            f"in the {SAMVAT_KEYS[c['samvat']]} year, in {c['ayana']}, in the {RITU_KEYS[c['ritu']]} "
            f"({RITU_EN[c['ritu']]}) season, in the month of {masa}, in the "
            f"{'bright' if c['shukla'] else 'dark'} fortnight, on {TITHI_KEYS[c['tithi']]} tithi, "
            f"a {VARA_EN[c['vara']]}, under {NAK_KEYS[c['nak']]} nakshatra, in {YOGA_RO[c['yoga']]} yoga "
            f"and {KARANA_RO[c['karana']]} karana — on this auspicious day, "
            f"I, {c['name']} of the {c['gothram']} gotra{with_}, for the safety, stability, courage, "
            "success, long life, health and prosperity of my family, for attaining the four goals "
            "of life (dharma, artha, kama and moksha) and for the fulfilment of our wishes, "
            f"to please {p['deity_en']}, perform the {p['name_en']} to the best of my ability.{wishes}"
        )

    def _meaning(self, c, L):
        p = c["pooja"]
        n = lambda latin: in_script(name_to_deva(latin), L) if latin else ""
        place = ", ".join(place_name(x, L) for x in (c["city"], c["state"], c["country"]) if x)
        samvat = stem_native(SAMVAT_SA[c["samvat"]], L)
        ayana = AYANA_N[L][c["ayana"]]
        ritu = RITU_N[L][c["ritu"]]
        if c["tamil_cal"] and L == "ta":
            masa = TAMIL_MASA_TA[c["masa"]]
        elif c["tamil_cal"]:
            masa = stem_native(RASHI_SA[c["masa"]].rstrip("र्"), L)
        else:
            masa = MASA_N[L][c["masa"]]
        paksha = PAKSHA_N[L][0 if c["shukla"] else 1]
        tithi = TITHI_N[L][c["tithi"]]
        vara = VARA_N[L][c["vara"]]
        nak = NAK_N[L][c["nak"]]
        yoga = stem_native(YOGA_SA[c["yoga"]], L)
        karana = stem_native(KARANA_SA[c["karana"]], L)
        river = stem_native(c["river_sa"], L)
        if L == "te":  # Telugu names drop the final long ā: సీత, ప్రియ
            n = lambda latin: " ".join(stem_native(name_to_deva(w), "te") for w in latin.split()) if latin else ""
        name, gotra, patni = n(c["name"]), n(c["gothram"]), n(c["patni"])
        members = ", ".join(n(m) for m in c["members"])
        deity, act, wishes = p["deity"][L], p["name"][L], c["desires"]

        if L == "te":
            adhika = "అధిక " if c["adhika"] else ""
            with_ = (f", ధర్మపత్ని {patni}తో" if patni else "") + (f", {members}లతో" if members else "")
            return (
                "అర్థం — నా పాపాలన్నీ తొలగి, పరమేశ్వరుని అనుగ్రహం కలగాలని, ఈ శుభ ముహూర్తంలో, "
                "శ్రీ మహావిష్ణువు ఆజ్ఞచే నడుస్తున్న ఈ కాలంలో — బ్రహ్మదేవుని ద్వితీయ పరార్ధంలో, "
                "శ్వేతవరాహ కల్పంలో, వైవస్వత మన్వంతరంలో, కలియుగ ప్రథమ పాదంలో — "
                f"ప్రదేశం: {place}; {river} నది సమీపంలో, {samvat} నామ సంవత్సరం, {ayana}, {ritu}, "
                f"{adhika}{masa} మాసం, {paksha}, {tithi} తిథి, {vara}, {nak} నక్షత్రం, "
                f"{yoga} యోగం, {karana} కరణం గల ఈ శుభ దినాన — {gotra} గోత్రానికి చెందిన "
                f"{name} అనే నేను{with_}, మా కుటుంబ క్షేమం, స్థైర్యం, వీర్యం, విజయం, ఆయురారోగ్యాలు, "
                "ఐశ్వర్యం వృద్ధి చెందాలని, ధర్మ, అర్థ, కామ, మోక్షాలనే నాలుగు పురుషార్థాలు సిద్ధించాలని, "
                f"కోరిన కోరికలు నెరవేరాలని, {deity} ప్రీతి కొరకు, యథాశక్తి {act} ఆచరిస్తున్నాను."
                + (f"\n(కోరికలు: {wishes})" if wishes else "")
            )
        if L == "kn":
            adhika = "ಅಧಿಕ " if c["adhika"] else ""
            with_ = (f", ಧರ್ಮಪತ್ನಿ {patni} ಅವರೊಂದಿಗೆ" if patni else "") + \
                    (f", {members} ಅವರೊಂದಿಗೆ" if members else "")
            return (
                "ಅರ್ಥ — ನನ್ನ ಎಲ್ಲಾ ಪಾಪಗಳು ನಿವಾರಣೆಯಾಗಿ ಪರಮೇಶ್ವರನ ಅನುಗ್ರಹ ದೊರೆಯಲೆಂದು, ಈ ಶುಭ ಮುಹೂರ್ತದಲ್ಲಿ, "
                "ಶ್ರೀ ಮಹಾವಿಷ್ಣುವಿನ ಆಜ್ಞೆಯಂತೆ ನಡೆಯುತ್ತಿರುವ ಈ ಕಾಲದಲ್ಲಿ — ಬ್ರಹ್ಮನ ದ್ವಿತೀಯ ಪರಾರ್ಧದಲ್ಲಿ, "
                "ಶ್ವೇತವರಾಹ ಕಲ್ಪದಲ್ಲಿ, ವೈವಸ್ವತ ಮನ್ವಂತರದಲ್ಲಿ, ಕಲಿಯುಗದ ಪ್ರಥಮ ಪಾದದಲ್ಲಿ — "
                f"ಸ್ಥಳ: {place}; {river} ನದಿಯ ಸಮೀಪದಲ್ಲಿ, {samvat} ನಾಮ ಸಂವತ್ಸರ, {ayana}, {ritu}, "
                f"{adhika}{masa} ಮಾಸ, {paksha}, {tithi} ತಿಥಿ, {vara}, {nak} ನಕ್ಷತ್ರ, {yoga} ಯೋಗ, "
                f"{karana} ಕರಣಗಳಿಂದ ಕೂಡಿದ ಈ ಶುಭ ದಿನದಂದು — {gotra} ಗೋತ್ರದ {name} ಎಂಬ ನಾನು{with_}, "
                "ನಮ್ಮ ಕುಟುಂಬದ ಕ್ಷೇಮ, ಸ್ಥೈರ್ಯ, ವೀರ್ಯ, ವಿಜಯ, ಆಯುರಾರೋಗ್ಯ ಮತ್ತು ಐಶ್ವರ್ಯಗಳ ಅಭಿವೃದ್ಧಿಗಾಗಿ, "
                "ಧರ್ಮ, ಅರ್ಥ, ಕಾಮ, ಮೋಕ್ಷಗಳೆಂಬ ನಾಲ್ಕು ಪುರುಷಾರ್ಥಗಳ ಸಿದ್ಧಿಗಾಗಿ, ಇಷ್ಟಾರ್ಥ ಸಿದ್ಧಿಗಾಗಿ, "
                f"{deity} ಪ್ರೀತಿಗಾಗಿ, ಯಥಾಶಕ್ತಿ {act} ಮಾಡುತ್ತೇನೆ."
                + (f"\n(ಇಷ್ಟಾರ್ಥಗಳು: {wishes})" if wishes else "")
            )
        if L == "ta":
            adhika = "அதிக " if c["adhika"] else ""
            with_ = (f", தர்மபத்தினி {patni} அவர்களுடன்" if patni else "") + \
                    (f", {members} ஆகியோருடன்" if members else "")
            return (
                "பொருள் — என் பாவங்கள் அனைத்தும் நீங்கி, பரமேஸ்வரனின் அருள் கிடைக்க, இந்த சுப முகூர்த்தத்தில், "
                "ஸ்ரீ மகாவிஷ்ணுவின் ஆணைப்படி நடக்கும் இக்காலத்தில் — பிரம்மாவின் இரண்டாம் பரார்த்தத்தில், "
                "ஸ்வேத வராக கல்பத்தில், வைவஸ்வத மன்வந்தரத்தில், கலியுகத்தின் முதல் பாதத்தில் — "
                f"இடம்: {place}; {river} நதிக்கு அருகில், {samvat} வருடம், {ayana}, {ritu}, "
                f"{adhika}{masa} மாதம், {paksha}, {tithi} திதி, {vara}, {nak} நட்சத்திரம், {yoga} யோகம், "
                f"{karana} கரணம் கூடிய இந்த சுப நாளில் — {gotra} கோத்திரத்தைச் சேர்ந்த {name} என்னும் நான்{with_}, "
                "எங்கள் குடும்பத்தின் நலம், உறுதி, வீரம், வெற்றி, நீண்ட ஆயுள், ஆரோக்கியம், செல்வம் பெருகவும், "
                "அறம், பொருள், இன்பம், வீடு என்னும் நான்கு புருஷார்த்தங்களும் கைகூடவும், "
                f"விரும்பியவை நிறைவேறவும், {deity} அருளுக்காக, என்னால் இயன்ற அளவு {act} செய்கிறேன்."
                + (f"\n(விருப்பங்கள்: {wishes})" if wishes else "")
            )
        if L == "hi":
            adhika = "अधिक " if c["adhika"] else ""
            with_ = (f", धर्मपत्नी {patni} के साथ" if patni else "") + (f", {members} सहित" if members else "")
            return (
                "अर्थ — अपने सभी पापों के क्षय और परमेश्वर की प्रसन्नता के लिए, इस शुभ मुहूर्त में, "
                "श्री महाविष्णु की आज्ञा से चल रहे इस काल में — ब्रह्मा जी के द्वितीय परार्ध में, "
                "श्वेतवराह कल्प में, वैवस्वत मन्वंतर में, कलियुग के प्रथम चरण में — "
                f"स्थान: {place}; {river} नदी के समीप, {samvat} नामक संवत्सर, {ayana}, {ritu}, "
                f"{adhika}{masa} मास, {paksha}, {tithi} तिथि, {vara}, {nak} नक्षत्र, {yoga} योग "
                f"और {karana} करण से युक्त इस शुभ दिन — मैं, {gotra} गोत्र का {name}{with_}, "
                "अपने परिवार के कल्याण, स्थिरता, पराक्रम, विजय, दीर्घायु, आरोग्य और ऐश्वर्य की वृद्धि के लिए, "
                "धर्म, अर्थ, काम और मोक्ष — इन चारों पुरुषार्थों की सिद्धि के लिए, मनोकामनाओं की पूर्ति के लिए, "
                f"{deity} प्रसन्नता हेतु, यथाशक्ति {act} करने का संकल्प करता हूँ।"
                + (f"\n(मनोकामनाएँ: {wishes})" if wishes else "")
            )
        # Marathi
        adhika = "अधिक " if c["adhika"] else ""
        with_ = (f", धर्मपत्नी {patni} यांच्यासह" if patni else "") + (f", {members} यांच्यासह" if members else "")
        return (
            "अर्थ — माझ्या सर्व पापांचा क्षय व्हावा आणि परमेश्वराची कृपा लाभावी म्हणून, या शुभ मुहूर्तावर, "
            "श्री महाविष्णूंच्या आज्ञेने चालणाऱ्या या काळात — ब्रह्मदेवाच्या द्वितीय परार्धात, "
            "श्वेतवराह कल्पात, वैवस्वत मन्वंतरात, कलियुगाच्या प्रथम चरणात — "
            f"स्थान: {place}; {river} नदीच्या जवळ, {samvat} नाम संवत्सर, {ayana}, {ritu}, "
            f"{adhika}{masa} महिना, {paksha}, {tithi} तिथी, {vara}, {nak} नक्षत्र, {yoga} योग "
            f"आणि {karana} करण असलेल्या या शुभ दिवशी — {gotra} गोत्राचा मी {name}{with_}, "
            "आमच्या कुटुंबाचे कल्याण, स्थैर्य, पराक्रम, विजय, दीर्घायुष्य, आरोग्य आणि ऐश्वर्य वाढावे म्हणून, "
            "धर्म, अर्थ, काम आणि मोक्ष या चार पुरुषार्थांच्या सिद्धीसाठी, मनोकामना पूर्ण व्हाव्यात म्हणून, "
            f"{deity} प्रसन्नतेसाठी, यथाशक्ती {act} करीत आहे."
            + (f"\n(मनोकामना: {wishes})" if wishes else "")
        )
