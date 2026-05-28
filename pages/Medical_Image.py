import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Medical Image AI", page_icon="🔬", layout="wide")
st.title("🔬 Medical Image AI Analyzer")
st.caption("Upload any medical image — AI will analyze it and answer your questions")

api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

with st.sidebar:
    st.header("Upload Medical Image")
    uploaded_file = st.file_uploader(
        "Upload X-ray, scan, or report",
        type=["jpg", "jpeg", "png", "webp"]
    )
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        st.session_state.uploaded_image = image
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.rerun()

if not api_key:
    st.warning("👈 Enter your Gemini API key in the sidebar to begin")

elif not st.session_state.uploaded_image:
    st.info("👈 Upload a medical image from the sidebar to begin analysis")
    st.markdown("""
    **What you can upload:**
    - X-rays (chest, bone, dental)
    - MRI or CT scan images
    - Blood test reports
    - Prescription documents

    **What AI can do:**
    - Describe what it sees
    - Explain medical terms
    - Answer your follow-up questions
    """)

else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    if len(st.session_state.messages) == 0:
        with st.spinner("AI is analyzing your image..."):
            response = model.generate_content([
                "You are a medical AI assistant. Analyze this medical image carefully. "
                "Describe what you see, identify any notable findings, and explain them "
                "in simple language a patient can understand. Always remind the user to "
                "consult a doctor for proper diagnosis.",
                st.session_state.uploaded_image
            ])
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.text
            })

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ask a question about the image..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                history = "\n".join([
                    f"{m['role'].upper()}: {m['content']}"
                    for m in st.session_state.messages[:-1]
                ])
                full_prompt = f"""You are a medical AI assistant. 
Previous conversation:
{history}

User's new question: {prompt}

Answer based on the medical image provided and the conversation history."""

                response = model.generate_content([
                    full_prompt,
                    st.session_state.uploaded_image
                ])
                st.write(response.text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.text
                })

st.markdown("---")
st.caption("⚠️ For educational use only. Always consult a qualified doctor.")