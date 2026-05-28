import streamlit as st
import google.generativeai as genai
import tempfile
import os

st.set_page_config(page_title="Voice Assistant", page_icon="🎤", layout="wide")
st.title("🎤 Medical Voice Assistant")
st.caption("Ask health questions by voice or text — AI will answer")

api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.markdown("---")
    st.markdown("""
    **How to use:**
    - Type your health question below
    - AI will answer in detail
    - Ask follow-up questions
    
    **Example questions:**
    - What does high creatinine mean?
    - Explain my chest X-ray findings
    - What foods to avoid with kidney disease?
    - What are symptoms of heart disease?
    """)

if not api_key:
    st.warning("👈 Enter your Gemini API key in the sidebar to begin")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Text input
    if prompt := st.chat_input("Ask any health question..."):
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    history = "\n".join([
                        f"{m['role'].upper()}: {m['content']}"
                        for m in st.session_state.chat_history[:-1]
                    ])

                    full_prompt = f"""You are a helpful medical AI assistant. 
Answer health questions in simple, clear language.
Always remind users to consult a doctor for serious concerns.

Previous conversation:
{history}

User question: {prompt}

Give a helpful, accurate, and easy to understand answer."""

                    response = model.generate_content(full_prompt)
                    answer = response.text

                    st.write(answer)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })

                    # Text to speech using browser
                    st.markdown(f"""
                    <script>
                    function speak() {{
                        var msg = new SpeechSynthesisUtterance(`{answer[:500]}`);
                        msg.lang = 'en-US';
                        msg.rate = 0.9;
                        window.speechSynthesis.speak(msg);
                    }}
                    </script>
                    """, unsafe_allow_html=True)

                    if st.button("🔊 Read Answer Aloud", key=f"speak_{len(st.session_state.chat_history)}"):
                        st.markdown(f"""
                        <script>
                        var msg = new SpeechSynthesisUtterance(`{answer[:500].replace('`', '')}`);
                        msg.lang = 'en-US';
                        msg.rate = 0.9;
                        window.speechSynthesis.speak(msg);
                        </script>
                        """, unsafe_allow_html=True)
                        st.success("🔊 Speaking...")

                except Exception as e:
                    st.error("Rate limit reached. Please wait a minute and try again.")

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

st.markdown("---")
st.caption("⚠️ For educational use only. Always consult a qualified doctor.")