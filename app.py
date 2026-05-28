import streamlit as st
st.set_page_config(page_title="Healthcare AI Platform", page_icon="🏥", layout="wide")
st.markdown("<h1 style='text-align:center;'>🏥 Healthcare AI Platform</h1>", unsafe_allow_html=True)
st.markdown("---")
tools = [
    ("🫀", "Heart Disease Predictor", "#e74c3c", "pages/Heart_Disease.py"),
    ("🩸", "Blood & Kidney Analyzer", "#e67e22", "pages/Blood_Kidney.py"),
    ("⚖️", "BMI Calculator", "#27ae60", "pages/BMI_Calculator.py"),
    ("👨‍⚕️", "Doctor Finder", "#2980b9", "pages/Doctor_Finder.py"),
    ("🔬", "Medical Image AI", "#8e44ad", "pages/Medical_Image.py"),
    ("🧴", "Skin Analyzer", "#16a085", "pages/Skin_Analyzer.py"),
    ("🎤", "Voice Assistant", "#d35400", "pages/Voice_Assistant.py"),
    ("📄", "Lab Report Analyzer", "#c0392b", "pages/Lab_Report.py"),
]
cols = st.columns(4)
for i, (emoji, title, color, page) in enumerate(tools):
    with cols[i % 4]:
        st.markdown(f"<div style='padding:20px;border-top:4px solid {color};border-radius:12px;border:1px solid #eee;margin:8px 0;'><div style='font-size:32px'>{emoji}</div><div style='font-weight:700;color:{color}'>{title}</div></div>", unsafe_allow_html=True)
        if st.button("Open", key=f"btn_{i}"):
            st.switch_page(page)
st.markdown("---")
st.caption("For educational use only · Built by Harsh Pandey")