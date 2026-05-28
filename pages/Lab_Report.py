import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

st.set_page_config(page_title="Lab Report Analyzer", page_icon="🔬", layout="wide")

LANGUAGES = {
    "English": {
        "title": "🔬 Lab Report Analyzer",
        "caption": "Upload your lab report — AI will read and analyze it automatically",
        "upload_header": "📄 Upload Lab Report",
        "upload_text": "Upload blood test report image",
        "api_warning": "👈 Enter your Gemini API key in the sidebar to begin",
        "analyzing": "🔍 AI is reading your report...",
        "detected": "Test Detected",
        "result_title": "📊 Your Results",
        "normal": "Normal", "high": "High ⚠️", "low": "Low ⚠️",
        "consult": "⚠️ Please consult a doctor for proper diagnosis",
        "speak": "🔊 Read Results Aloud",
        "enter_key": "Enter Gemini API Key",
        "how_to": "How to use",
        "step1": "1️⃣ Enter Gemini API Key",
        "step2": "2️⃣ Select your language",
        "step3": "3️⃣ Upload lab report photo",
        "step4": "4️⃣ AI reads & analyzes automatically",
    },
    "Hindi": {
        "title": "🔬 लैब रिपोर्ट विश्लेषक",
        "caption": "अपनी लैब रिपोर्ट अपलोड करें — AI स्वचालित रूप से पढ़ेगा",
        "upload_header": "📄 लैब रिपोर्ट अपलोड करें",
        "upload_text": "रक्त परीक्षण रिपोर्ट की छवि अपलोड करें",
        "api_warning": "👈 शुरू करने के लिए Gemini API key डालें",
        "analyzing": "🔍 AI आपकी रिपोर्ट पढ़ रहा है...",
        "detected": "परीक्षण पहचाना गया",
        "result_title": "📊 आपके परिणाम",
        "normal": "सामान्य", "high": "अधिक ⚠️", "low": "कम ⚠️",
        "consult": "⚠️ कृपया डॉक्टर से परामर्श करें",
        "speak": "🔊 परिणाम जोर से पढ़ें",
        "enter_key": "Gemini API Key दर्ज करें",
        "how_to": "कैसे उपयोग करें",
        "step1": "1️⃣ Gemini API Key दर्ज करें",
        "step2": "2️⃣ अपनी भाषा चुनें",
        "step3": "3️⃣ लैब रिपोर्ट की फोटो अपलोड करें",
        "step4": "4️⃣ AI स्वचालित रूप से विश्लेषण करता है",
    },
    "Tamil": {
        "title": "🔬 ஆய்வக அறிக்கை பகுப்பாய்வி",
        "caption": "உங்கள் அறிக்கையை பதிவேற்றவும் — AI தானாக படிக்கும்",
        "upload_header": "📄 அறிக்கையை பதிவேற்றவும்",
        "upload_text": "இரத்த பரிசோதனை அறிக்கை படத்தை பதிவேற்றவும்",
        "api_warning": "👈 தொடங்க Gemini API key உள்ளிடவும்",
        "analyzing": "🔍 AI உங்கள் அறிக்கையை படிக்கிறது...",
        "detected": "சோதனை கண்டறியப்பட்டது",
        "result_title": "📊 உங்கள் முடிவுகள்",
        "normal": "சாதாரண", "high": "அதிகம் ⚠️", "low": "குறைவு ⚠️",
        "consult": "⚠️ மருத்துவரை அணுகவும்",
        "speak": "🔊 முடிவுகளை சத்தமாக படிக்கவும்",
        "enter_key": "Gemini API Key உள்ளிடவும்",
        "how_to": "எப்படி பயன்படுத்துவது",
        "step1": "1️⃣ Gemini API Key உள்ளிடவும்",
        "step2": "2️⃣ மொழியை தேர்ந்தெடுக்கவும்",
        "step3": "3️⃣ அறிக்கை படத்தை பதிவேற்றவும்",
        "step4": "4️⃣ AI தானாக படிக்கும்",
    },
    "Telugu": {
        "title": "🔬 ల్యాబ్ నివేదిక విశ్లేషకుడు",
        "caption": "మీ నివేదికను అప్లోడ్ చేయండి — AI స్వయంచాలకంగా చదువుతుంది",
        "upload_header": "📄 నివేదికను అప్లోడ్ చేయండి",
        "upload_text": "రక్త పరీక్ష నివేదిక చిత్రాన్ని అప్లోడ్ చేయండి",
        "api_warning": "👈 Gemini API key నమోదు చేయండి",
        "analyzing": "🔍 AI మీ నివేదికను చదువుతోంది...",
        "detected": "పరీక్ష గుర్తించబడింది",
        "result_title": "📊 మీ ఫలితాలు",
        "normal": "సాధారణ", "high": "అధికం ⚠️", "low": "తక్కువ ⚠️",
        "consult": "⚠️ వైద్యుడిని సంప్రదించండి",
        "speak": "🔊 ఫలితాలను బిగ్గరగా చదవండి",
        "enter_key": "Gemini API Key నమోదు చేయండి",
        "how_to": "ఎలా ఉపయోగించాలి",
        "step1": "1️⃣ Gemini API Key నమోదు చేయండి",
        "step2": "2️⃣ భాషను ఎంచుకోండి",
        "step3": "3️⃣ నివేదిక చిత్రాన్ని అప్లోడ్ చేయండి",
        "step4": "4️⃣ AI స్వయంచాలకంగా చదువుతుంది",
    },
    "Bengali": {
        "title": "🔬 ল্যাব রিপোর্ট বিশ্লেষক",
        "caption": "আপনার রিপোর্ট আপলোড করুন — AI স্বয়ংক্রিয়ভাবে পড়বে",
        "upload_header": "📄 রিপোর্ট আপলোড করুন",
        "upload_text": "রক্ত পরীক্ষার রিপোর্টের ছবি আপলোড করুন",
        "api_warning": "👈 Gemini API key দিন",
        "analyzing": "🔍 AI আপনার রিপোর্ট পড়ছে...",
        "detected": "পরীক্ষা সনাক্ত করা হয়েছে",
        "result_title": "📊 আপনার ফলাফল",
        "normal": "স্বাভাবিক", "high": "বেশি ⚠️", "low": "কম ⚠️",
        "consult": "⚠️ ডাক্তারের পরামর্শ নিন",
        "speak": "🔊 ফলাফল জোরে পড়ুন",
        "enter_key": "Gemini API Key দিন",
        "how_to": "কীভাবে ব্যবহার করবেন",
        "step1": "1️⃣ Gemini API Key দিন",
        "step2": "2️⃣ ভাষা বেছে নিন",
        "step3": "3️⃣ রিপোর্টের ছবি আপলোড করুন",
        "step4": "4️⃣ AI স্বয়ংক্রিয়ভাবে পড়বে",
    },
    "Marathi": {
        "title": "🔬 लॅब रिपोर्ट विश्लेषक",
        "caption": "तुमची लॅब रिपोर्ट अपलोड करा — AI आपोआप वाचेल",
        "upload_header": "📄 रिपोर्ट अपलोड करा",
        "upload_text": "रक्त चाचणी रिपोर्टची प्रतिमा अपलोड करा",
        "api_warning": "👈 Gemini API key टाका",
        "analyzing": "🔍 AI तुमची रिपोर्ट वाचत आहे...",
        "detected": "चाचणी ओळखली गेली",
        "result_title": "📊 तुमचे निकाल",
        "normal": "सामान्य", "high": "जास्त ⚠️", "low": "कमी ⚠️",
        "consult": "⚠️ डॉक्टरांचा सल्ला घ्या",
        "speak": "🔊 निकाल मोठ्याने वाचा",
        "enter_key": "Gemini API Key टाका",
        "how_to": "कसे वापरावे",
        "step1": "1️⃣ Gemini API Key टाका",
        "step2": "2️⃣ भाषा निवडा",
        "step3": "3️⃣ रिपोर्टचा फोटो अपलोड करा",
        "step4": "4️⃣ AI आपोआप वाचेल",
    },
    "Gujarati": {
        "title": "🔬 લેબ રિપોર્ટ વિશ્લેષક",
        "caption": "તમારો રિપોર્ટ અપલોડ કરો — AI આપમેળે વાંચશે",
        "upload_header": "📄 રિપોર્ટ અપલોડ કરો",
        "upload_text": "રક્ત પરીક્ષણ રિપોર્ટની છબી અપલોડ કરો",
        "api_warning": "👈 Gemini API key દાખલ કરો",
        "analyzing": "🔍 AI તમારો રિપોર્ટ વાંચી રહ્યું છે...",
        "detected": "પરીક્ષણ શોધાયું",
        "result_title": "📊 તમારા પરિણામો",
        "normal": "સામાન્ય", "high": "વધારે ⚠️", "low": "ઓછું ⚠️",
        "consult": "⚠️ ડૉક્ટરની સલાહ લો",
        "speak": "🔊 પરિણામો મોટેથી વાંચો",
        "enter_key": "Gemini API Key દાખલ કરો",
        "how_to": "કેવી રીતે ઉપયોગ કરવો",
        "step1": "1️⃣ Gemini API Key દાખલ કરો",
        "step2": "2️⃣ ભાષા પસંદ કરો",
        "step3": "3️⃣ રિપોર્ટનો ફોટો અપલોડ કરો",
        "step4": "4️⃣ AI આપમેળે વાંચશે",
    }
}

LANG_CODES = {
    "English": "en-US", "Hindi": "hi-IN", "Tamil": "ta-IN",
    "Telugu": "te-IN", "Bengali": "bn-IN", "Marathi": "mr-IN", "Gujarati": "gu-IN"
}

NORMAL_RANGES = {
    "LFT": {
        "SGOT": (10, 40, "U/L"), "AST": (10, 40, "U/L"),
        "SGPT": (7, 56, "U/L"), "ALT": (7, 56, "U/L"),
        "BILIRUBIN TOTAL": (0.2, 1.2, "mg/dL"),
        "BILIRUBIN DIRECT": (0.0, 0.3, "mg/dL"),
        "ALKALINE PHOSPHATASE": (44, 147, "U/L"),
        "TOTAL PROTEIN": (6.3, 8.2, "g/dL"),
        "ALBUMIN": (3.5, 5.0, "g/dL"),
    },
    "Thyroid": {
        "TSH": (0.4, 4.0, "mIU/L"),
        "T3": (80, 200, "ng/dL"),
        "T4": (5.0, 12.0, "µg/dL"),
        "FREE T3": (2.3, 4.2, "pg/mL"),
        "FREE T4": (0.8, 1.8, "ng/dL"),
    },
    "Diabetes": {
        "FASTING GLUCOSE": (70, 100, "mg/dL"),
        "POST PRANDIAL": (70, 140, "mg/dL"),
        "HBA1C": (4.0, 5.6, "%"),
        "RANDOM BLOOD SUGAR": (70, 140, "mg/dL"),
    },
    "Lipid": {
        "TOTAL CHOLESTEROL": (0, 200, "mg/dL"),
        "HDL": (40, 60, "mg/dL"),
        "LDL": (0, 100, "mg/dL"),
        "TRIGLYCERIDES": (0, 150, "mg/dL"),
        "VLDL": (5, 40, "mg/dL"),
    },
    "CBC": {
        "HEMOGLOBIN": (12, 17, "g/dL"),
        "WBC": (4000, 11000, "cells/µL"),
        "PLATELETS": (150000, 400000, "cells/µL"),
        "RBC": (4.5, 5.5, "million/µL"),
        "HEMATOCRIT": (36, 50, "%"),
    }
}

with st.sidebar:
    selected_lang = st.selectbox("🌐 Language / भाषा", list(LANGUAGES.keys()))
    t = LANGUAGES[selected_lang]
    st.markdown("---")
    api_key = st.text_input(t["enter_key"], type="password")
    st.markdown("---")
    st.markdown(f"**{t['how_to']}**")
    st.markdown(t["step1"])
    st.markdown(t["step2"])
    st.markdown(t["step3"])
    st.markdown(t["step4"])
    st.markdown("---")
    st.header(t["upload_header"])
    uploaded_file = st.file_uploader(t["upload_text"], type=["jpg", "jpeg", "png", "webp"])

t = LANGUAGES[selected_lang]
st.title(t["title"])
st.caption(t["caption"])

if not api_key:
    st.warning(t["api_warning"])
    st.markdown("---")
    st.markdown("### 🏥 Supported Tests")
    cols = st.columns(5)
    tests = [
        ("🫀", "Heart/CBC", "#e74c3c"),
        ("🫁", "LFT", "#f39c12"),
        ("🦋", "Thyroid", "#9b59b6"),
        ("🩸", "Diabetes", "#e67e22"),
        ("💧", "Lipid", "#3498db"),
    ]
    for col, (emoji, name, color) in zip(cols, tests):
        with col:
            st.markdown(f"""
            <div style="text-align:center; padding:20px; background:{color}20;
                border-radius:12px; border: 2px solid {color};">
                <div style="font-size:40px;">{emoji}</div>
                <div style="font-weight:bold; color:{color};">{name}</div>
            </div>
            """, unsafe_allow_html=True)

elif not uploaded_file:
    st.markdown("""
    <div style="text-align:center; padding:60px; background:#f8f9fa;
        border-radius:20px; border: 3px dashed #dee2e6;">
        <div style="font-size:80px;">📄</div>
        <h2>Upload Your Lab Report</h2>
        <p style="font-size:18px; color:#666;">Take a photo of your blood test report and upload it</p>
        <p style="font-size:16px; color:#999;">👈 Use the sidebar to upload</p>
    </div>
    """, unsafe_allow_html=True)

else:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(image, caption="Uploaded Report", use_container_width=True)

    with col2:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")

        with st.spinner(t["analyzing"]):
            try:
                extract_prompt = """You are a medical lab report AI. Analyze this lab report image.
1. Identify what type of test this is (LFT, Thyroid, Diabetes, Lipid, CBC, or Other)
2. Extract ALL test values from the report

Respond ONLY in this exact JSON format with no extra text:
{
  "test_type": "LFT",
  "values": {
    "parameter_name": "value with unit"
  }
}"""
                response = model.generate_content([extract_prompt, image])
                raw = response.text.strip()
                raw = re.sub(r'```json|```', '', raw).strip()
                data = json.loads(raw)
                test_type = data.get("test_type", "Unknown")
                values = data.get("values", {})

                st.success(f"✅ {t['detected']}: **{test_type}**")
                st.markdown(f"### {t['result_title']}")

                normal_ref = NORMAL_RANGES.get(test_type, {})
                results_text = f"{test_type} Test Results:\n"

                for param, value in values.items():
                    num_val = None
                    try:
                        num_val = float(re.findall(r'[\d.]+', str(value))[0])
                    except Exception:
                        pass

                    status = t["normal"]
                    color = "#2ecc71"

                    for ref_param, (low, high, unit) in normal_ref.items():
                        if ref_param in param.upper():
                            if num_val is not None:
                                if num_val < low:
                                    status = t["low"]
                                    color = "#3498db"
                                elif num_val > high:
                                    status = t["high"]
                                    color = "#e74c3c"
                            break

                    results_text += f"{param}: {value} — {status}\n"
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center;
                        padding:10px 16px; margin:4px 0; border-radius:8px;
                        background:{color}15; border-left: 4px solid {color};">
                        <span style="font-weight:600;">{param}</span>
                        <span style="font-size:18px; font-weight:bold;">{value}</span>
                        <span style="color:{color}; font-weight:600;">{status}</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")
                with st.spinner("Generating analysis..."):
                    analysis_prompt = f"""You are a medical AI assistant.
Analyze these {test_type} test results and explain them in {selected_lang} language.
Keep it simple so even an uneducated person can understand.

Results:
{results_text}

Provide:
1. Simple explanation of what these results mean
2. Which values are concerning (if any)
3. Simple advice
4. When to see a doctor

IMPORTANT: Respond ENTIRELY in {selected_lang} language only."""

                    analysis = model.generate_content(analysis_prompt)
                    st.markdown("### 🩺 Analysis")
                    st.write(analysis.text)

                    safe_text = analysis.text[:800].replace('`', '').replace('"', '').replace("'", "")
                    lang_code = LANG_CODES.get(selected_lang, "en-US")

                    if st.button(t["speak"]):
                        st.markdown(f"""
                        <script>
                        var msg = new SpeechSynthesisUtterance("{safe_text}");
                        msg.lang = '{lang_code}';
                        msg.rate = 0.85;
                        window.speechSynthesis.speak(msg);
                        </script>
                        """, unsafe_allow_html=True)
                        st.success("🔊 Speaking...")

                st.warning(t["consult"])

            except json.JSONDecodeError:
                st.error("Could not read report clearly. Please upload a clearer image.")
            except Exception as e:
                st.error("Rate limit reached or error occurred. Please wait a minute and try again.")

st.markdown("---")
st.caption("⚠️ For educational use only. Always consult a qualified doctor.")