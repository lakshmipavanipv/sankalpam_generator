"""
transliteration.py (v4) – comprehensive known-terms + Unicode offset conversion
"""

DEVA_START, DEVA_END = 0x0900, 0x097F

OFFSETS = {
    "devanagari": 0,
    "telugu":     0x0C00 - 0x0900,
    "kannada":    0x0C80 - 0x0900,
}

DEVA_TO_TAMIL = {
    'अ':'அ','आ':'ஆ','इ':'இ','ई':'ஈ','उ':'உ','ऊ':'ஊ','ए':'எ','ऐ':'ஐ','ओ':'ஒ','औ':'ஔ','ऋ':'ரி',
    'ा':'ா','ि':'ி','ी':'ீ','ु':'ு','ू':'ூ','े':'ே','ै':'ை','ो':'ோ','ौ':'ௌ','ृ':'ரி',
    'ं':'ம்','ः':'ஹ்','्':'்','ँ':'ம்',
    'क':'க','ख':'க','ग':'க','घ':'க','ङ':'ங',
    'च':'ச','छ':'ச','ज':'ஜ','झ':'ஜ','ञ':'ஞ',
    'ट':'ட','ठ':'ட','ड':'ட','ढ':'ட','ण':'ண',
    'त':'த','थ':'த','द':'த','ध':'த','न':'ன',
    'प':'ப','फ':'ப','ब':'ப','भ':'ப','म':'ம',
    'य':'ய','र':'ர','ल':'ல','व':'வ','ळ':'ள',
    'श':'ஶ','ष':'ஷ','स':'ஸ','ह':'ஹ',
    '०':'0','१':'1','२':'2','३':'3','४':'4','५':'5','६':'6','७':'7','८':'8','९':'9',
    ' ':' ','\n':'\n',',':',','.':'.',':':':','।':'।','॥':'॥','(':' (', ')':') ','—':'—',
    'ॐ':'ஓம்',
}

def deva_to_script(text: str, script: str) -> str:
    if not text: return text
    if script == "devanagari": return text
    if script == "tamil":
        return "".join(DEVA_TO_TAMIL.get(ch, ch) for ch in text)
    offset = OFFSETS.get(script, 0)
    out = []
    for ch in text:
        cp = ord(ch)
        out.append(chr(cp + offset) if DEVA_START <= cp <= DEVA_END else ch)
    return "".join(out)

# ── Comprehensive known-terms dict: Latin → Devanagari ───────────────────────
KNOWN = {
    # ── Samvatsaras (all 60) ──────────────────────────────────────────────────
    "prabhava":"प्रभव","vibhava":"विभव","shukla":"शुक्ल","pramoda":"प्रमोद",
    "prajapati":"प्रजापति","angirasa":"अंगिरस","shrimukha":"श्रीमुख","bhava":"भव",
    "yuva":"युव","dhata":"धाता","ishvara":"ईश्वर","bahudhanya":"बहुधान्य",
    "pramadi":"प्रमादी","vikrama":"विक्रम","vrisha":"वृष","chitrabhanu":"चित्रभानु",
    "svabhanu":"स्वभानु","tarana":"तारण","parthiva":"पार्थिव","vyaya":"व्यय",
    "sarvajit":"सर्वजित्","sarvadhari":"सर्वधारी","virodhi":"विरोधी","vikruti":"विकृति",
    "khara":"खर","nandana":"नन्दन","vijaya":"विजय","jaya":"जय","manmatha":"मन्मथ",
    "durmukhi":"दुर्मुखी","hevilambi":"हेविलम्बी","vilambi":"विलम्बी","vikari":"विकारी",
    "sharvari":"शार्वरी","plava":"प्लव","shubhakrut":"शुभकृत्","shobhakrut":"शोभकृत्",
    "krodhi":"क्रोधी","vishvavasu":"विश्वावसु","parabhava":"पराभव","plavanga":"प्लवंग",
    "kilaka":"किलक","saumya":"सौम्य","sadharana":"साधारण","virodhikrut":"विरोधिकृत्",
    "paridhavi":"परिधावी","ananda":"आनन्द","rakshasa":"राक्षस","nala":"नल",
    "pingala":"पिंगल","kalayukti":"कलयुक्ति","siddharthi":"सिद्धार्थी","raudra":"रौद्र",
    "durmati":"दुर्मति","dundubhi":"दुन्दुभि","rudhirodgari":"रुधिरोद्गारी",
    "raktakshi":"रक्ताक्षी","krodhana":"क्रोधन","akshaya":"अक्षय",
    # ── Gotra names ───────────────────────────────────────────────────────────
    "kashyapa":"काश्यप","bharadwaja":"भारद्वाज","atreya":"अत्रेय",
    "atreyasa":"अत्रेयस","athreyasa":"अत्रेयस","atreyas":"अत्रेयस",
    "vasishtha":"वसिष्ठ","vishwamitra":"विश्वामित्र","gautama":"गौतम",
    "agastya":"अगस्त्य","kaundinya":"कौण्डिन्य","harita":"हारित",
    "sandilya":"शाण्डिल्य","garga":"गर्ग","vatsa":"वत्स","parashara":"पाराशर",
    "jamadagni":"जमदग्नि","srivatsa":"श्रीवत्स","mudgala":"मुद्गल",
    "upamanyu":"उपमन्यु","dhananjaya":"धनञ्जय","kaushika":"कौशिक",
    "vatsyayan":"वात्स्यायन","shaunaka":"शौनक","maudgalya":"मौद्गल्य",
    # ── Common South Indian personal names ───────────────────────────────────
    "venkata":"वेंकट","phaneendra":"फणींद्र","phani":"फणि","phanindra":"फणींद्र",
    "lakshmi":"लक्ष्मी","pavani":"पावनी","laxmi":"लक्ष्मी",
    "rama":"राम","rao":"राव","krishna":"कृष्ण","prasad":"प्रसाद",
    "suresh":"सुरेश","ramesh":"रमेश","mahesh":"महेश","ganesh":"गणेश",
    "ravi":"रवि","rajesh":"राजेश","naresh":"नरेश","dinesh":"दिनेश",
    "srinivas":"श्रीनिवास","venkateswara":"वेंकटेश्वर","subramanya":"सुब्रमण्य",
    "murali":"मुरली","mohan":"मोहन","siva":"शिव","shiva":"शिव",
    "satya":"सत्य","narayana":"नारायण","satyanarayana":"सत्यनारायण",
    "priya":"प्रिया","radha":"राधा","meena":"मीना","geetha":"गीता",
    "rani":"रानी","rani":"रानी","radha":"राधा","rekha":"रेखा",
    "rohini":"रोहिणी","roopa":"रूपा","rupa":"रूपा","revathi":"रेवती",
    "sujatha":"सुजाता","sujata":"सुजाता","sunita":"सुनीता","swathi":"स्वाति",
    "swati":"स्वाति","saritha":"सरिता","sarita":"सरिता","suma":"सुमा",
    "usha":"उषा","vijaya":"विजया","vimala":"विमला","yamuna":"यमुना",
    "aruna":"अरुणा","asha":"आशा","bhavani":"भवानी","chandra":"चंद्र",
    "deepa":"दीपा","deepthi":"दीप्ति","divya":"दिव्या","gayathri":"गायत्री",
    "gayatri":"गायत्री","gowri":"गौरी","hema":"हेमा","indu":"इंदु",
    "jyothi":"ज्योति","jyoti":"ज्योति","kamala":"कमला","kiran":"किरण",
    "komala":"कोमला","latha":"लता","leela":"लीला","madhavi":"माधवी",
    "mallika":"मल्लिका","mangala":"मंगला","manju":"मंजु","manjula":"मंजुला",
    "nirmala":"निर्मला","nisha":"निशा","pooja":"पूजा","pushpa":"पुष्पा",
    "rajani":"रजनी","ratna":"रत्ना","renuka":"रेणुका","rukmini":"रुक्मिणी",
    "sangeetha":"संगीता","sangita":"संगीता","saraswati":"सरस्वती",
    "savitri":"सावित्री","shanthi":"शांति","shanti":"शांति",
    "sharada":"शारदा","shobha":"शोभा","shruti":"श्रुति","sindhu":"सिंधु",
    "sridevi":"श्रीदेवी","sudha":"सुधा","sulochana":"सुलोचना",
    "sumathi":"सुमति","sumati":"सुमति","suseela":"सुशीला","sushila":"सुशीला",
    "tulasi":"तुलसी","tulsi":"तुलसी","vasantha":"वसंत","vasanta":"वसंत",
    "venkatalakshmi":"वेंकटलक्ष्मी","vidya":"विद्या","vijayalakshmi":"विजयलक्ष्मी",
    # Male names not yet covered
    "anil":"अनिल","ajay":"अजय","ajit":"अजीत","akash":"आकाश",
    "amit":"अमित","amith":"अमित","anand":"आनंद","arun":"अरुण",
    "ashok":"अशोक","balaji":"बालाजी","bhaskar":"भास्कर","deepak":"दीपक",
    "harish":"हरीश","hemant":"हेमंत","jagadish":"जगदीश","karthik":"कार्तिक",
    "kishore":"किशोर","madhu":"मधु","manoj":"मनोज","narayan":"नारायण",
    "narayana":"नारायण","nikhil":"निखिल","pavan":"पवन","praveen":"प्रवीण",
    "pradeep":"प्रदीप","pramod":"प्रमोद","raghu":"रघु","raghunath":"रघुनाथ",
    "rajiv":"राजीव","rakesh":"राकेश","ramakrishna":"रामकृष्ण",
    "ramarao":"रामाराव","ramesh":"रमेश","ravi":"रवि","rohit":"रोहित",
    "sainath":"साईनाथ","sai":"साई","sampath":"संपत्","sandeep":"संदीप",
    "santosh":"संतोष","sathish":"सतीश","satish":"सतीश","sekhar":"शेखर",
    "shankar":"शंकर","shiva":"शिव","siva":"शिव","srikanth":"श्रीकांत",
    "srinath":"श्रीनाथ","sudhir":"सुधीर","sunil":"सुनील","suresh":"सुरेश",
    "surya":"सूर्य","vamsi":"वंशी","venkat":"वेंकट","venu":"वेणु",
    "vijay":"विजय","vikram":"विक्रम","viswanath":"विश्वनाथ",
    "yadav":"यादव","yashwant":"यशवंत",
    "sita":"सीता","padma":"पद्मा","latha":"लता","kavitha":"कविता",
    "anitha":"अनिता","sunitha":"सुनीता","savitha":"सविता","lalitha":"ललिता",
    "kumar":"कुमार","reddy":"रेड्डी","sharma":"शर्मा","verma":"वर्मा",
    "petluri":"पेटलूरि","dash":"दाश","das":"दास","devi":"देवी",
    "singh":"सिंह","nair":"नायर","pillai":"पिल्लई","menon":"मेनन",
    "iyer":"अय्यर","iyengar":"अय्यंगार","naidu":"नायडू","chetty":"चेट्टी",
    # ── Pooja / ritual names ──────────────────────────────────────────────────
    "satyanarayana":"सत्यनारायण","ganesh puja":"गणेशपूजां","lakshmi puja":"लक्ष्मीपूजां",
    "navagraha":"नवग्रह","rudrabhishekam":"रुद्राभिषेकम्","ayushya":"आयुष्य",
    "grihapravesham":"गृहप्रवेशम्","vivah":"विवाह","upanayanam":"उपनयनम्",
    "namakaranam":"नामकरणम्","annaprasana":"अन्नप्राशन","seemantham":"सीमन्तम्",
    "vastu":"वास्तु","durga":"दुर्गा","karthika":"कार्तिक",
    # ── Rivers ────────────────────────────────────────────────────────────────
    "ganga":"गंगा","fraser":"फ्रेज़र","thames":"टेम्स","seine":"सेन",
    "parramatta":"पर्रामट्टा","yarra":"यर्रा","hudson":"हडसन",
    "mississippi":"मिसिसिपी","potomac":"पोटोमैक","humber":"हम्बर",
    "st. lawrence":"सेंट लॉरेंस","duwamish":"दुवामिश","sacramento":"सैक्रामेंटो",
    "buffalo bayou":"बफैलो बेयू","chicago":"शिकागो","spree":"श्प्री",
    "isar":"ईज़र","amstel":"एम्स्टल","tiete":"तिएटे","kallang":"कल्लंग",
    "klang":"क्लंग","liesbeek":"लीस्बीक","musi":"मूसी","cooum":"कूवम",
    "arkavathi":"अर्कावती","hooghly":"हुगली","gomti":"गोमती",
    "ulhas":"उल्हास","pamba":"पम्बा","tungabhadra":"तुंगभद्रा",
    "godavari":"गोदावरी","cauvery":"कावेरी","brahmaputra":"ब्रह्मपुत्र",
    "swan":"स्वान","brisbane":"ब्रिस्बेन",
    # ── Countries ─────────────────────────────────────────────────────────────
    "india":"भारत","canada":"कनाडा","usa":"अमेरिका","united states":"अमेरिका",
    "australia":"आस्ट्रेलिया","uk":"ब्रिटेन","united kingdom":"ब्रिटेन",
    "germany":"जर्मनी","france":"फ्रांस","singapore":"सिंगापुर",
    "malaysia":"मलेशिया","uae":"यूएई","new zealand":"न्यूज़ीलैंड",
    "south africa":"दक्षिण अफ्रीका","brazil":"ब्राज़ील","netherlands":"नीदरलैंड",
    "sri lanka":"श्रीलंका","nepal":"नेपाल","bangladesh":"बांग्लादेश",
    # ── States / Provinces ────────────────────────────────────────────────────
    "telangana":"तेलंगाना","andhra pradesh":"आन्ध्रप्रदेश","karnataka":"कर्नाटक",
    "tamil nadu":"तमिलनाडु","kerala":"केरल","maharashtra":"महाराष्ट्र",
    "gujarat":"गुजरात","rajasthan":"राजस्थान","punjab":"पंजाब",
    "british columbia":"ब्रिटिशकोलम्बिया","ontario":"ओन्टेरियो","quebec":"क्यूबेक",
    "alberta":"अल्बर्टा","new south wales":"न्यूसाउथवेल्स","victoria":"विक्टोरिया",
    "queensland":"क्वींसलैंड","california":"कैलिफोर्निया","texas":"टेक्सास",
    "new york":"न्यूयॉर्क","florida":"फ्लोरिडा","washington":"वाशिंगटन",
    # ── Cities ────────────────────────────────────────────────────────────────
    "hyderabad":"हैदराबाद","chennai":"चेन्नई","bangalore":"बेंगलुरु",
    "bengaluru":"बेंगलुरु","mumbai":"मुम्बई","kolkata":"कोलकाता",
    "pune":"पुणे","ahmedabad":"अहमदाबाद","tirupati":"तिरुपति",
    "vijayawada":"विजयवाड़ा","visakhapatnam":"विशाखापट्टणम",
    "toronto":"टोरन्टो","vancouver":"वैंकूवर","surrey":"सरे",
    "white rock":"व्हाइट रॉक","burnaby":"बर्नेबी","richmond":"रिचमंड",
    "mississauga":"मिसिसागा","brampton":"ब्रैम्पटन","calgary":"कैलगरी",
    "edmonton":"एडमन्टन","ottawa":"ओटावा","montreal":"मॉन्ट्रियल",
    "sydney":"सिडनी","melbourne":"मेलबर्न","perth":"पर्थ","adelaide":"एडिलेड",
    "london":"लन्दन","paris":"पेरिस","berlin":"बर्लिन","amsterdam":"एम्स्टर्डम",
    "new york city":"न्यूयॉर्क","los angeles":"लॉस एंजिलिस",
    "houston":"ह्यूस्टन","seattle":"सिएटल","dallas":"डैलस","miami":"मायामी",
    "dubai":"दुबई","kuala lumpur":"क्वालालम्पुर",
    "abbotsford":"एबट्सफोर्ड","langley":"लैंगली","coquitlam":"कोक्विटलम",
    "delta":"डेल्टा","north vancouver":"नॉर्थ वैंकूवर",
}

def name_to_deva(text: str) -> str:
    """Convert Latin name/term to Devanagari. Known dict first, then phoneme fallback."""
    if not text or not text.strip(): return text
    key = text.lower().strip()
    # full phrase lookup
    if key in KNOWN: return KNOWN[key]
    # word-by-word
    words = text.split()
    if len(words) > 1:
        return " ".join(KNOWN.get(w.lower(), _phoneme(w)) for w in words)
    return _phoneme(text)

def _phoneme(text: str) -> str:
    PAIRS = [
        ("shri","श्री"),("sri","श्री"),("ksh","क्ष"),
        ("aa","आ"),("ee","ई"),("ii","ई"),("oo","ऊ"),("uu","ऊ"),
        ("ai","ऐ"),("au","औ"),("sh","श"),("th","थ"),("gh","घ"),
        ("kh","ख"),("ph","फ"),("bh","भ"),("dh","ध"),("ch","च"),
        ("jh","झ"),("ng","ङ"),("rr","ऋ"),("ri","रि"),
        ("a","अ"),("e","ए"),("i","इ"),("o","ओ"),("u","उ"),
        ("b","ब"),("c","क"),("d","द"),("f","फ"),("g","ग"),("h","ह"),
        ("j","ज"),("k","क"),("l","ल"),("m","म"),("n","न"),
        ("p","प"),("q","क"),("r","र"),("s","स"),("t","त"),
        ("v","व"),("w","व"),("x","क्स"),("y","य"),("z","ज"),
        (" "," "),(","," "),("."," "),("-"," "),("'",""),
    ]
    result, s, i = [], text.lower(), 0
    while i < len(s):
        matched = False
        for pat, rep in PAIRS:
            if s[i:i+len(pat)] == pat:
                result.append(rep); i += len(pat); matched = True; break
        if not matched: result.append(s[i]); i += 1
    return "".join(result)

def to_script(text: str, script: str) -> str:
    return deva_to_script(name_to_deva(text), script)
