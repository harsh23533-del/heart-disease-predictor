import streamlit as st

st.set_page_config(page_title="Healthcare AI Platform", page_icon="🏥", layout="wide")

st.title("🏥 Healthcare AI Platform")
st.caption("AI-powered health risk prediction tools")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.info("🫀 **Heart Disease Predictor**\n\nPredict heart disease risk using XGBoost + SHAP explainability")
    if st.button("Open Heart Disease Tool"):
        st.switch_page("pages/Heart_Disease.py")

with col2:
    st.warning("🩸 **Blood & Kidney Test Analyzer**\n\nAnalyze CBC and kidney function test results")
    if st.button("Open Blood & Kidney Tool"):
        st.switch_page("pages/Blood_Kidney.py")

st.markdown("---")
st.caption("For educational use only · Not a substitute for medical advice")