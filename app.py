import streamlit as st

st.set_page_config(page_title="Healthcare AI Platform", page_icon="🏥", layout="wide")

st.markdown("""
<style>
.tool-card {
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    border: 1.5px solid #e0e0e0;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.tool-emoji { font-size: 36px; }
.tool-title { font-size: 17px; font-weight: 700; margin: 8px 0 4px 0; }
.tool-desc { font-size: 13px; color: #666; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🏥 Healthcare AI Platform</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888; font-size:16px;'>AI-powered health tools — simple enough for everyone</p>", unsafe_allow_html=True)
st.markdown("---")

tools = [
    ("🫀", "Heart Disease Predictor", "XGBoost + SHAP explainability for heart risk", "#e74c3c", "pages/Heart_Disease.py"),
    ("🩸", "Blood & Kidney Analyzer", "CBC and kidney function test analysis", "#e67e22", "pages/Blood_Kidney.py"),
    ("⚖️", "BMI Calculator", "Body Mass Index with health insights", "#27ae60", "pages/BMI_Calculator.py"),
    ("👨‍⚕️", "Doctor Finder", "Find top-rated doctors by specialty", "#2980b9", "pages/Doctor_Finder.py"),
    ("🔬", "Medical Image AI", "Upload X-ray or scan — AI analyzes it", "#8e44ad", "pages/Medical_Image.py"),
    ("🧴", "Skin Analyzer", "AI skin condition + nearby dermatologists", "#16a085", "pages/Skin_Analyzer.py"),
    ("🎤", "Voice Assistant", "Ask health questions, get spoken answers", "#d35400", "pages/Voice_Assistant.py"),
    ("📄", "Lab Report Analyzer", "Upload report photo — AI reads & explains", "#c0392b", "pages/Lab_Report.py"),
]

cols = st.columns(4)
for i, (emoji, title, desc, color, page) in enumerate(tools):
    with cols[i % 4]:
        st.markdown(f"""
        <div class="tool-card" style="border-top: 4px solid {color};">
            <div class="tool-emoji">{emoji}</div>
            <div class="tool-title" style="color:{color};">{title}</div>
            <div class="tool-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Open {title}", key=f"btn_{i}"):
            st.switch_page(page)

st.markdown("---")
st.caption("For educational use only · Not a substitute for medical advice · Built by Harsh Pandey")