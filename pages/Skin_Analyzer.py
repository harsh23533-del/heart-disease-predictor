import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Skin Analyzer", page_icon="🧴", layout="wide")

st.title("🧴 AI Skin Analyzer")
st.caption("Upload skin photo - AI will analyze it")
st.markdown("---")

with st.sidebar:
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("---")
    st.markdown("**How to use:**")
    st.markdown("1. Enter Gemini API Key")
    st.markdown("2. Upload skin photo")
    st.markdown("3. AI will analyze it")

uploaded = st.file_uploader("Upload skin photo", type=['jpg', 'jpeg', 'png'])

if not api_key:
    st.warning("Please enter Gemini API key in sidebar!")
elif not uploaded:
    st.info("Please upload a skin photo!")
else:
    image = Image.open(uploaded)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(image, caption="Your Photo", use_container_width=True)

    with col2:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")

        with st.spinner("AI analyzing..."):
            prompt = """You are a dermatology AI assistant. Analyze this skin image and provide:
1. What condition this might be (simple name)
2. Is it serious or not? (Yes/No with reason)
3. Simple advice in easy language
4. Should they see a doctor? (Yes/No)

Keep response simple - imagine explaining to someone with no medical knowledge.
Format your response clearly with these 4 points."""

            response = model.generate_content([prompt, image])

            st.markdown("### Result:")
            st.write(response.text)
            st.warning("Educational use only - always consult a dermatologist!")

st.markdown("---")
st.caption("Built by Harsh Pandey - AI Skin Analysis")