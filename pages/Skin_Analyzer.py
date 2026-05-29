import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Skin Analyzer", page_icon="🧴", layout="wide")

st.title("🧴 AI Skin Analyzer")
st.caption("Upload skin photo - AI will analyze it")
st.markdown("---")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

uploaded = st.file_uploader("Upload skin photo", type=['jpg', 'jpeg', 'png'])

if not uploaded:
    st.info("Please upload a skin photo!")
else:
    image = Image.open(uploaded)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(image, caption="Your Photo", use_container_width=True)

    with col2:
        model = genai.GenerativeModel("gemini-1.5-flash")
        with st.spinner("AI analyzing..."):
            prompt = """You are a dermatology AI assistant. Analyze this skin image and provide:
1. What condition this might be (simple name)
2. Is it serious or not? (Yes/No with reason)
3. Simple advice in easy language
4. Should they see a doctor? (Yes/No)
Keep response simple and easy to understand."""

            response = model.generate_content([prompt, image])
            st.markdown("### Result:")
            st.write(response.text)
            st.warning("Educational use only - always consult a dermatologist!")

st.markdown("---")
st.caption("Built by Harsh Pandey - AI Skin Analysis")