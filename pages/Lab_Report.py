import streamlit as st
import re
try:
    import pdfplumber
    PDF_OK = True
except ImportError:
    PDF_OK = False

st.set_page_config(page_title="Medical Report Summarizer", page_icon="📄", layout="wide")

# ─── Language Strings ───────────────────────────────────────────────
LANG = {
    "English": {
        "title": "📄 Medical Report Summarizer",
        "subtitle": "Upload your lab report — get instant AI summary",
        "upload": "Upload Lab Report (PDF or TXT)",
        "analyzing": "Analyzing your report...",
        "summary": "📋 Report Summary",
        "findings": "🔬 Key Findings",
        "normal": "✅ Normal",
        "abnormal": "⚠️ Abnormal / Needs Attention",
        "advice": "💡 General Advice",
        "disclaimer": "⚠️ For educational use only. Please consult a doctor.",
        "no_text": "Could not extract text. Please upload a valid PDF or TXT file.",
        "select_lang": "Select Language",
        "parameters": "📊 Detected Parameters",
        "high": "HIGH",
        "low": "LOW",
        "ok": "NORMAL",
    },
    "Hindi": {
        "title": "📄 मेडिकल रिपोर्ट समराइज़र",
        "subtitle": "अपनी लैब रिपोर्ट अपलोड करें — तुरंत AI सारांश पाएं",
        "upload": "लैब रिपोर्ट अपलोड करें (PDF या TXT)",
        "analyzing": "आपकी रिपोर्ट का विश्लेषण हो रहा है...",
        "summary": "📋 रिपोर्ट सारांश",
        "findings": "🔬 मुख्य निष्कर्ष",
        "normal": "✅ सामान्य",
        "abnormal": "⚠️ असामान्य / ध्यान दें",
        "advice": "💡 सामान्य सलाह",
        "disclaimer": "⚠️ केवल शैक्षिक उद्देश्य के लिए। कृपया डॉक्टर से सलाह लें।",
        "no_text": "टेक्स्ट नहीं निकाल सका। कृपया सही PDF या TXT फ़ाइल अपलोड करें।",
        "select_lang": "भाषा चुनें",
        "parameters": "📊 मिले पैरामीटर",
        "high": "अधिक",
        "low": "कम",
        "ok": "सामान्य",
    },
    "Tamil": {
        "title": "📄 மருத்துவ அறிக்கை சுருக்கம்",
        "subtitle": "உங்கள் ஆய்வக அறிக்கையை பதிவேற்றவும் — உடனடி AI சுருக்கம்",
        "upload": "ஆய்வக அறிக்கையை பதிவேற்றவும் (PDF அல்லது TXT)",
        "analyzing": "உங்கள் அறிக்கை பகுப்பாய்வு செய்யப்படுகிறது...",
        "summary": "📋 அறிக்கை சுருக்கம்",
        "findings": "🔬 முக்கிய கண்டுபிடிப்புகள்",
        "normal": "✅ இயல்பான",
        "abnormal": "⚠️ அசாதாரண / கவனம் தேவை",
        "advice": "💡 பொது அறிவுரை",
        "disclaimer": "⚠️ கல்வி நோக்கங்களுக்காக மட்டுமே. மருத்துவரை அணுகவும்।",
        "no_text": "உரையை பிரிக்க முடியவில்லை. சரியான PDF அல்லது TXT கோப்பை பதிவேற்றவும்।",
        "select_lang": "மொழியை தேர்ந்தெடுக்கவும்",
        "parameters": "📊 கண்டறியப்பட்ட அளவுருக்கள்",
        "high": "அதிகம்",
        "low": "குறைவு",
        "ok": "இயல்பு",
    },
    "Telugu": {
        "title": "📄 వైద్య నివేదిక సారాంశం",
        "subtitle": "మీ లాబ్ నివేదికను అప్‌లోడ్ చేయండి — తక్షణ AI సారాంశం",
        "upload": "లాబ్ నివేదికను అప్‌లోడ్ చేయండి (PDF లేదా TXT)",
        "analyzing": "మీ నివేదిక విశ్లేషించబడుతోంది...",
        "summary": "📋 నివేదిక సారాంశం",
        "findings": "🔬 ముఖ్య అన్వేషణలు",
        "normal": "✅ సాధారణం",
        "abnormal": "⚠️ అసాధారణం / శ్రద్ధ అవసరం",
        "advice": "💡 సాధారణ సలహా",
        "disclaimer": "⚠️ విద్యా ప్రయోజనాల కోసం మాత్రమే. దయచేసి వైద్యుడిని సంప్రదించండి।",
        "no_text": "వచనాన్ని సేకరించడం సాధ్యం కాలేదు. సరైన PDF లేదా TXT ఫైల్ అప్‌లోడ్ చేయండి।",
        "select_lang": "భాషను ఎంచుకోండి",
        "parameters": "📊 గుర్తించబడిన పారామీటర్లు",
        "high": "అధికం",
        "low": "తక్కువ",
        "ok": "సాధారణం",
    },
    "Bengali": {
        "title": "📄 মেডিকেল রিপোর্ট সারসংক্ষেপ",
        "subtitle": "আপনার ল্যাব রিপোর্ট আপলোড করুন — তাৎক্ষণিক AI সারসংক্ষেপ পান",
        "upload": "ল্যাব রিপোর্ট আপলোড করুন (PDF বা TXT)",
        "analyzing": "আপনার রিপোর্ট বিশ্লেষণ হচ্ছে...",
        "summary": "📋 রিপোর্ট সারসংক্ষেপ",
        "findings": "🔬 মূল অনুসন্ধান",
        "normal": "✅ স্বাভাবিক",
        "abnormal": "⚠️ অস্বাভাবিক / মনোযোগ প্রয়োজন",
        "advice": "💡 সাধারণ পরামর্শ",
        "disclaimer": "⚠️ শুধুমাত্র শিক্ষামূলক উদ্দেশ্যে। অনুগ্রহ করে ডাক্তারের পরামর্শ নিন।",
        "no_text": "টেক্সট বের করা সম্ভব হয়নি। সঠিক PDF বা TXT ফাইল আপলোড করুন।",
        "select_lang": "ভাষা নির্বাচন করুন",
        "parameters": "📊 সনাক্তকৃত প্যারামিটার",
        "high": "বেশি",
        "low": "কম",
        "ok": "স্বাভাবিক",
    },
}

# ─── Lab Parameters Database ────────────────────────────────────────
PARAMS = {
    "hemoglobin":    {"aliases": ["hemoglobin", "hb", "haemoglobin"],          "min": 12.0, "max": 17.5, "unit": "g/dL"},
    "glucose":       {"aliases": ["glucose", "blood sugar", "fasting sugar"],   "min": 70,   "max": 100,  "unit": "mg/dL"},
    "hba1c":         {"aliases": ["hba1c", "glycated", "a1c"],                  "min": 4.0,  "max": 5.7,  "unit": "%"},
    "creatinine":    {"aliases": ["creatinine", "serum creatinine"],            "min": 0.6,  "max": 1.2,  "unit": "mg/dL"},
    "urea":          {"aliases": ["urea", "blood urea", "bun"],                 "min": 7,    "max": 20,   "unit": "mg/dL"},
    "cholesterol":   {"aliases": ["cholesterol", "total cholesterol"],          "min": 0,    "max": 200,  "unit": "mg/dL"},
    "triglycerides": {"aliases": ["triglycerides", "tg"],                       "min": 0,    "max": 150,  "unit": "mg/dL"},
    "hdl":           {"aliases": ["hdl", "hdl cholesterol"],                    "min": 40,   "max": 999,  "unit": "mg/dL"},
    "ldl":           {"aliases": ["ldl", "ldl cholesterol"],                    "min": 0,    "max": 100,  "unit": "mg/dL"},
    "wbc":           {"aliases": ["wbc", "white blood", "leukocytes"],          "min": 4000, "max": 11000,"unit": "cells/μL"},
    "rbc":           {"aliases": ["rbc", "red blood"],                          "min": 4.2,  "max": 5.9,  "unit": "million/μL"},
    "platelets":     {"aliases": ["platelets", "plt", "thrombocytes"],          "min": 150000,"max":400000,"unit": "cells/μL"},
    "tsh":           {"aliases": ["tsh", "thyroid stimulating"],                "min": 0.4,  "max": 4.0,  "unit": "mIU/L"},
    "sodium":        {"aliases": ["sodium", "na+", "serum sodium"],             "min": 136,  "max": 145,  "unit": "mEq/L"},
    "potassium":     {"aliases": ["potassium", "k+", "serum potassium"],        "min": 3.5,  "max": 5.0,  "unit": "mEq/L"},
    "calcium":       {"aliases": ["calcium", "serum calcium"],                  "min": 8.5,  "max": 10.5, "unit": "mg/dL"},
    "uric acid":     {"aliases": ["uric acid", "urate"],                        "min": 3.5,  "max": 7.2,  "unit": "mg/dL"},
    "bilirubin":     {"aliases": ["bilirubin", "total bilirubin"],              "min": 0.2,  "max": 1.2,  "unit": "mg/dL"},
    "sgpt":          {"aliases": ["sgpt", "alt", "alanine"],                    "min": 7,    "max": 40,   "unit": "U/L"},
    "sgot":          {"aliases": ["sgot", "ast", "aspartate"],                  "min": 10,   "max": 40,   "unit": "U/L"},
}

ADVICE = {
    "English": {
        "hemoglobin":    "Eat iron-rich foods like spinach, lentils, meat. Low Hb may indicate anemia.",
        "glucose":       "Limit sugar intake. Exercise regularly. Monitor fasting sugar.",
        "hba1c":         "Long-term blood sugar control. Consult endocrinologist if high.",
        "creatinine":    "Drink plenty of water. Avoid excess protein. May indicate kidney stress.",
        "cholesterol":   "Reduce fried foods, exercise daily. High cholesterol risks heart disease.",
        "triglycerides": "Avoid sugary drinks and refined carbs. Exercise helps.",
        "hdl":           "Low HDL is bad. Exercise and healthy fats (nuts, fish) increase HDL.",
        "ldl":           "High LDL increases heart risk. Reduce saturated fats.",
        "wbc":           "Abnormal WBC may indicate infection or immune issue. See doctor.",
        "tsh":           "Thyroid issue detected. Consult endocrinologist.",
        "uric acid":     "High uric acid causes gout. Drink water, avoid red meat and alcohol.",
        "sgpt":          "Elevated liver enzyme. Avoid alcohol, fatty food. See doctor.",
        "sgot":          "Elevated liver/heart enzyme. Medical evaluation needed.",
    },
    "Hindi": {
        "hemoglobin":    "पालक, दाल, मांस जैसे आयरन युक्त खाद्य पदार्थ खाएं। कम Hb एनीमिया का संकेत हो सकता है।",
        "glucose":       "चीनी कम खाएं। नियमित व्यायाम करें। फास्टिंग शुगर की निगरानी करें।",
        "hba1c":         "दीर्घकालिक रक्त शर्करा नियंत्रण। अधिक होने पर एंडोक्रिनोलॉजिस्ट से मिलें।",
        "creatinine":    "खूब पानी पिएं। अधिक प्रोटीन से बचें। किडनी पर असर हो सकता है।",
        "cholesterol":   "तले खाने से बचें, रोज व्यायाम करें। हृदय रोग का खतरा बढ़ सकता है।",
        "triglycerides": "मीठे पेय और रिफाइंड कार्ब से बचें। व्यायाम फायदेमंद है।",
        "hdl":           "कम HDL खराब है। व्यायाम और स्वस्थ वसा (मेवे, मछली) HDL बढ़ाते हैं।",
        "ldl":           "अधिक LDL हृदय जोखिम बढ़ाता है। संतृप्त वसा कम करें।",
        "wbc":           "असामान्य WBC संक्रमण का संकेत हो सकता है। डॉक्टर से मिलें।",
        "tsh":           "थायरॉइड समस्या मिली। एंडोक्रिनोलॉजिस्ट से परामर्श लें।",
        "uric acid":     "अधिक यूरिक एसिड गाउट का कारण बनता है। पानी पिएं, रेड मीट और शराब से बचें।",
        "sgpt":          "लिवर एंजाइम बढ़ा हुआ है। शराब और वसायुक्त भोजन से बचें।",
        "sgot":          "लिवर/हृदय एंजाइम बढ़ा हुआ। चिकित्सीय मूल्यांकन जरूरी।",
    },
    "Tamil": {
        "hemoglobin":    "கீரை, பருப்பு, இறைச்சி போன்ற இரும்புச்சத்து உணவுகளை சாப்பிடுங்கள்.",
        "glucose":       "சர்க்கரையை குறையுங்கள். தினமும் உடற்பயிற்சி செய்யுங்கள்.",
        "hba1c":         "நீண்டகால இரத்த சர்க்கரை கட்டுப்பாடு. அதிகமாக இருந்தால் மருத்துவரை அணுகவும்.",
        "creatinine":    "அதிக தண்ணீர் குடிக்கவும். சிறுநீரக அழுத்தம் இருக்கலாம்.",
        "cholesterol":   "வறுத்த உணவுகளை தவிர்க்கவும். இதய நோய் அபாயம் உள்ளது.",
        "triglycerides": "இனிப்பு பானங்களை தவிர்க்கவும். உடற்பயிற்சி உதவும்.",
        "hdl":           "குறைந்த HDL தீங்கானது. உடற்பயிற்சி மற்றும் ஆரோக்கியமான கொழுப்புகள் உதவும்.",
        "ldl":           "அதிக LDL இதய அபாயத்தை அதிகரிக்கும்.",
        "wbc":           "அசாதாரண WBC தொற்றை குறிக்கலாம். மருத்துவரை அணுகவும்.",
        "tsh":           "தைராய்டு பிரச்சினை. மருத்துவரை அணுகவும்.",
        "uric acid":     "அதிக யூரிக் அமிலம் கீல்வாதத்தை ஏற்படுத்தும்.",
        "sgpt":          "கல்லீரல் என்சைம் அதிகமாக உள்ளது. ஆல்கஹால் தவிர்க்கவும்.",
        "sgot":          "கல்லீரல் என்சைம் அதிகம். மருத்துவ மதிப்பீடு தேவை.",
    },
    "Telugu": {
        "hemoglobin":    "పాలకూర, పప్పు, మాంసం వంటి ఇనుము అధికంగా ఉన్న ఆహారాలు తినండి.",
        "glucose":       "చక్కెర తక్కువగా తినండి. రోజూ వ్యాయామం చేయండి.",
        "hba1c":         "దీర్ఘకాలిక రక్తంలో చక్కెర నియంత్రణ. ఎక్కువగా ఉంటే వైద్యుడిని సంప్రదించండి.",
        "creatinine":    "నీరు ఎక్కువగా తాగండి. మూత్రపిండ సమస్య ఉండవచ్చు.",
        "cholesterol":   "వేయించిన ఆహారాలు తగ్గించండి. గుండె జబ్బు ప్రమాదం ఉంది.",
        "triglycerides": "తీపి పానీయాలు తగ్గించండి. వ్యాయామం సహాయపడుతుంది.",
        "hdl":           "తక్కువ HDL చెడ్డది. వ్యాయామం మరియు ఆరోగ్యకరమైన కొవ్వులు సహాయపడతాయి.",
        "ldl":           "అధిక LDL గుండె ప్రమాదాన్ని పెంచుతుంది.",
        "wbc":           "అసాధారణ WBC సంక్రమణను సూచించవచ్చు. వైద్యుడిని సంప్రదించండి.",
        "tsh":           "థైరాయిడ్ సమస్య గుర్తించబడింది. వైద్యుడిని సంప్రదించండి.",
        "uric acid":     "అధిక యూరిక్ యాసిడ్ వల్ల గౌట్ వస్తుంది. నీరు తాగండి.",
        "sgpt":          "కాలేయ ఎంజైమ్ అధికంగా ఉంది. మద్యం మానుకోండి.",
        "sgot":          "కాలేయ/గుండె ఎంజైమ్ అధికంగా ఉంది. వైద్య మూల్యాంకనం అవసరం.",
    },
    "Bengali": {
        "hemoglobin":    "পালং শাক, ডাল, মাংসের মতো আয়রন সমৃদ্ধ খাবার খান।",
        "glucose":       "চিনি কমান। নিয়মিত ব্যায়াম করুন। ফাস্টিং সুগার পর্যবেক্ষণ করুন।",
        "hba1c":         "দীর্ঘমেয়াদী রক্তের সুগার নিয়ন্ত্রণ। বেশি হলে ডাক্তার দেখান।",
        "creatinine":    "প্রচুর পানি পান করুন। কিডনির সমস্যা হতে পারে।",
        "cholesterol":   "ভাজা খাবার কমান। হৃদরোগের ঝুঁকি আছে।",
        "triglycerides": "মিষ্টি পানীয় এড়িয়ে চলুন। ব্যায়াম উপকারী।",
        "hdl":           "কম HDL খারাপ। ব্যায়াম ও স্বাস্থ্যকর চর্বি HDL বাড়ায়।",
        "ldl":           "বেশি LDL হৃদয়ের ঝুঁকি বাড়ায়।",
        "wbc":           "অস্বাভাবিক WBC সংক্রমণ নির্দেশ করতে পারে। ডাক্তার দেখান।",
        "tsh":           "থাইরয়েড সমস্যা পাওয়া গেছে। বিশেষজ্ঞ দেখান।",
        "uric acid":     "বেশি ইউরিক এসিড গেঁটেবাত সৃষ্টি করে। পানি পান করুন।",
        "sgpt":          "লিভার এনজাইম বেশি। মদ্যপান ও চর্বিযুক্ত খাবার এড়ান।",
        "sgot":          "লিভার এনজাইম বেশি। চিকিৎসা মূল্যায়ন দরকার।",
    },
}

# ─── Helper Functions ────────────────────────────────────────────────

def extract_text_from_pdf(file):
    if not PDF_OK:
        return ""
    try:
        import pdfplumber
        with pdfplumber.open(file) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except:
        return ""

def extract_text_from_txt(file):
    try:
        return file.read().decode("utf-8", errors="ignore")
    except:
        return ""

def find_value(text, aliases):
    text_lower = text.lower()
    for alias in aliases:
        pattern = rf"{re.escape(alias)}[\s:=\|]+([0-9]+\.?[0-9]*)"
        match = re.search(pattern, text_lower)
        if match:
            return float(match.group(1))
    return None

def analyze_report(text, lang):
    results = []
    L = LANG[lang]
    A = ADVICE.get(lang, ADVICE["English"])

    for param, info in PARAMS.items():
        val = find_value(text, info["aliases"])
        if val is None:
            continue
        mn, mx = info["min"], info["max"]
        if val < mn:
            status = L["low"]
            flag = "low"
        elif val > mx:
            status = L["high"]
            flag = "high"
        else:
            status = L["ok"]
            flag = "ok"
        advice = A.get(param, "")
        results.append({
            "param": param.title(),
            "value": val,
            "unit": info["unit"],
            "min": mn,
            "max": mx,
            "status": status,
            "flag": flag,
            "advice": advice,
        })
    return results

def get_overall_summary(results, lang):
    L = LANG[lang]
    abnormal = [r for r in results if r["flag"] != "ok"]
    normal = [r for r in results if r["flag"] == "ok"]
    if not results:
        return "No standard lab parameters detected in this report."
    if not abnormal:
        return L["normal"] + f" — All {len(normal)} detected parameters are within normal range. Great health indicators!"
    return L["abnormal"] + f" — {len(abnormal)} out of {len(results)} parameters need attention."

# ─── UI ─────────────────────────────────────────────────────────────

lang = st.sidebar.selectbox("🌐 " + "Language / भाषा", list(LANG.keys()))
L = LANG[lang]

st.markdown(f"<h1 style='text-align:center'>{L['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;color:#888'>{L['subtitle']}</p>", unsafe_allow_html=True)
st.markdown("---")

if not PDF_OK:
    st.warning("📦 pdfplumber not installed — PDF support disabled. TXT files work fine.")

uploaded = st.file_uploader(L["upload"], type=["pdf", "txt"])

if uploaded:
    with st.spinner(L["analyzing"]):
        if uploaded.name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded)
        else:
            text = extract_text_from_txt(uploaded)

    if not text.strip():
        st.error(L["no_text"])
        st.stop()

    results = analyze_report(text, lang)
    summary = get_overall_summary(results, lang)

    # Summary box
    color = "#27ae60" if all(r["flag"] == "ok" for r in results) else "#e74c3c"
    st.markdown(
        f"<div style='padding:16px;border-left:6px solid {color};border-radius:8px;background:{color}18'>"
        f"<h3>{L['summary']}</h3><p style='font-size:16px'>{summary}</p></div>",
        unsafe_allow_html=True
    )
    st.markdown("")

    if results:
        st.markdown(f"### {L['parameters']}")
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

        for i, r in enumerate(results):
            with cols[i % 3]:
                if r["flag"] == "ok":
                    bg, border = "#27ae6018", "#27ae60"
                elif r["flag"] == "high":
                    bg, border = "#e74c3c18", "#e74c3c"
                else:
                    bg, border = "#f39c1218", "#f39c12"

                st.markdown(
                    f"<div style='padding:12px;margin:6px 0;border-radius:8px;border-left:4px solid {border};background:{bg}'>"
                    f"<b>{r['param']}</b><br>"
                    f"<span style='font-size:22px;font-weight:bold'>{r['value']} {r['unit']}</span><br>"
                    f"<span style='color:{border}'>{r['status']}</span><br>"
                    f"<small>Normal: {r['min']}–{r['max']} {r['unit']}</small>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        # Advice for abnormal
        abnormal = [r for r in results if r["flag"] != "ok" and r["advice"]]
        if abnormal:
            st.markdown(f"### {L['advice']}")
            for r in abnormal:
                st.info(f"**{r['param']}** — {r['advice']}")

    else:
        st.warning("No standard lab parameters detected. Make sure your report contains values like Hemoglobin, Glucose, Creatinine etc.")

    with st.expander("📄 Raw Extracted Text"):
        st.text(text[:3000])

st.markdown("---")
st.warning(L["disclaimer"])
st.caption("Built by Harsh Pandey · No API required · Works offline")
