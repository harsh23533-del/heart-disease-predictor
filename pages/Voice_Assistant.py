import streamlit as st
import os
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Voice Assistant", page_icon="🎤", layout="centered")

st.markdown("""
<style>
    .title { text-align: center; font-size: 2.5rem; font-weight: 700; color: #f0a500; margin-bottom: 0.2rem; }
    .subtitle { text-align: center; color: #aaaaaa; font-size: 1rem; margin-bottom: 2rem; }
    .response-box { background: #1e1e2e; border-left: 4px solid #f0a500; border-radius: 10px; padding: 1rem 1.5rem; margin-top: 1rem; color: #e0e0e0; font-size: 1rem; line-height: 1.6; }
    .transcript-box { background: #1a1a2e; border-left: 4px solid #00bcd4; border-radius: 10px; padding: 0.8rem 1.2rem; margin-top: 0.5rem; color: #90caf9; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎤 Voice Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Speak your health question — AI will answer</div>', unsafe_allow_html=True)

HF_API_KEY = os.environ.get("HF_API_KEY", "")
try:
    if not HF_API_KEY:
        HF_API_KEY = st.secrets.get("HF_API_KEY", "")
except:
    pass

def ask_hf(question):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    prompt = f"<s>[INST] You are a helpful healthcare AI assistant. Answer this health question clearly in under 150 words using simple language.\n\nQuestion: {question} [/INST]"
    models = ["mistralai/Mistral-7B-Instruct-v0.3", "HuggingFaceH4/zephyr-7b-beta"]
    for model_id in models:
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_id}",
                headers=headers,
                json={"inputs": prompt, "parameters": {"max_new_tokens": 300, "temperature": 0.7, "return_full_text": False}},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and result:
                    text = result[0].get("generated_text", "").strip()
                    if text:
                        return text
        except:
            continue
    return "⚠️ Model loading, please try again in 30 seconds."

if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""
if "history" not in st.session_state:
    st.session_state.history = []

speech_html = """
<div style="display:flex;flex-direction:column;align-items:center;gap:16px;padding:20px;">
    <button id="micBtn" onclick="toggleListening()" style="width:100px;height:100px;border-radius:50%;background:linear-gradient(135deg,#f0a500,#e65c00);border:none;cursor:pointer;font-size:2.5rem;box-shadow:0 4px 20px rgba(240,165,0,0.4);">🎤</button>
    <div id="statusText" style="color:#aaa;font-size:0.9rem;">Click mic to speak</div>
    <div id="transcriptDiv" style="background:#1a1a2e;border-left:4px solid #00bcd4;border-radius:10px;padding:12px 16px;width:100%;color:#90caf9;font-size:0.95rem;min-height:40px;display:none;"></div>
    <button id="sendBtn" onclick="sendTranscript()" style="display:none;padding:10px 30px;background:linear-gradient(135deg,#00bcd4,#0097a7);color:white;border:none;border-radius:25px;font-size:1rem;cursor:pointer;">Send to AI ✨</button>
</div>
<script>
let recognition, isListening=false, finalTranscript="";
function toggleListening(){if(isListening){recognition.stop();}else{startListening();}}
function startListening(){
    if(!('webkitSpeechRecognition' in window)&&!('SpeechRecognition' in window)){document.getElementById('statusText').innerText='Use Chrome browser.';return;}
    const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
    recognition=new SR();recognition.lang='en-IN';recognition.interimResults=true;recognition.continuous=false;
    recognition.onstart=()=>{isListening=true;finalTranscript="";document.getElementById('micBtn').style.background='linear-gradient(135deg,#e53935,#b71c1c)';document.getElementById('micBtn').innerHTML='⏹️';document.getElementById('statusText').innerText='🔴 Listening...';document.getElementById('transcriptDiv').style.display='block';document.getElementById('transcriptDiv').innerText='';document.getElementById('sendBtn').style.display='none';};
    recognition.onresult=(e)=>{let interim='';for(let i=e.resultIndex;i<e.results.length;i++){if(e.results[i].isFinal){finalTranscript+=e.results[i][0].transcript;}else{interim+=e.results[i][0].transcript;}}document.getElementById('transcriptDiv').innerText=finalTranscript||interim;};
    recognition.onend=()=>{isListening=false;document.getElementById('micBtn').style.background='linear-gradient(135deg,#f0a500,#e65c00)';document.getElementById('micBtn').innerHTML='🎤';document.getElementById('statusText').innerText='✅ Done! Click Send.';if(finalTranscript.trim()){document.getElementById('sendBtn').style.display='block';}};
    recognition.onerror=(e)=>{isListening=false;document.getElementById('micBtn').style.background='linear-gradient(135deg,#f0a500,#e65c00)';document.getElementById('micBtn').innerHTML='🎤';document.getElementById('statusText').innerText='❌ Error: '+e.error;};
    recognition.start();
}
function sendTranscript(){if(finalTranscript.trim()){window.parent.postMessage({type:'voice_transcript',text:finalTranscript.trim()},'*');document.getElementById('statusText').innerText='⏳ Sending...';document.getElementById('sendBtn').style.display='none';}}
</script>
"""
components.html(speech_html, height=280)

transcript_input = st.text_input("Or type your question here:", placeholder="e.g. What are symptoms of diabetes?")
col1, col2 = st.columns([3, 1])
with col1:
    ask_btn = st.button("🤖 Ask AI", use_container_width=True, type="primary")
with col2:
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

if clear_btn:
    st.session_state.transcript = ""
    st.session_state.ai_response = ""
    st.session_state.history = []
    st.rerun()

if ask_btn and transcript_input.strip():
    st.session_state.transcript = transcript_input.strip()
    if not HF_API_KEY:
        st.error("⚠️ HF_API_KEY not set in Streamlit secrets.")
    else:
        with st.spinner("🤖 AI is thinking..."):
            answer = ask_hf(st.session_state.transcript)
            st.session_state.ai_response = answer
            st.session_state.history.append({"q": st.session_state.transcript, "a": answer})

if st.session_state.transcript:
    st.markdown(f'<div class="transcript-box">🗣️ <b>You:</b> {st.session_state.transcript}</div>', unsafe_allow_html=True)

if st.session_state.ai_response:
    st.markdown(f'<div class="response-box">🤖 <b>AI:</b><br><br>{st.session_state.ai_response}</div>', unsafe_allow_html=True)
    safe_text = st.session_state.ai_response.replace("'", "\\'").replace("`", "")
    tts_html = f"<script>function speakResponse(){{const u=new SpeechSynthesisUtterance('{safe_text}');u.lang='en-IN';u.rate=0.9;window.speechSynthesis.speak(u);}}</script><div style='margin-top:10px;text-align:center;'><button onclick='speakResponse()' style='padding:8px 20px;background:linear-gradient(135deg,#7b1fa2,#4a148c);color:white;border:none;border-radius:20px;cursor:pointer;'>🔊 Read Aloud</button></div>"
    components.html(tts_html, height=60)

if len(st.session_state.history) > 1:
    st.markdown("---")
    st.markdown("### 📜 Conversation History")
    for item in reversed(st.session_state.history[:-1]):
        with st.expander(f"Q: {item['q'][:60]}"):
            st.markdown(f"**You:** {item['q']}")
            st.markdown(f"**AI:** {item['a']}")

st.markdown("---")
st.caption("🎤 Chrome Web Speech API | 🤖 HuggingFace Mistral | ⚕️ Not medical advice")