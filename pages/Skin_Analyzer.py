import streamlit as st
import numpy as np
from PIL import Image
import os, json

st.set_page_config(page_title="Skin Analyzer", page_icon="🧴", layout="wide")
st.title("🧴 Skin Disease Analyzer")
st.caption("AI-powered skin condition detection | DermNet Dataset")
st.markdown("---")

if not os.path.exists("skin_disease_model.onnx"):
    st.warning("Model not found. Train first using train_skin_dermnet.py")
    st.info("1. Download DermNet from Kaggle\n2. Run train_skin_dermnet.py\n3. Push skin_disease_model.onnx to repo")
    st.stop()

@st.cache_resource
def load_model():
    import onnxruntime as ort
    session = ort.InferenceSession("skin_disease_model.onnx")
    with open("classes.json") as f:
        classes = json.load(f)
    return session, classes

session, CLASSES = load_model()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Upload Image")
    uploaded = st.file_uploader("Upload skin image", type=["jpg","jpeg","png"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, use_column_width=True)

with col2:
    st.subheader("Result")
    if not uploaded:
        st.info("Upload an image to start")
    else:
        img = Image.open(uploaded)
        arr = np.expand_dims(np.array(img.convert("RGB").resize((224,224)), dtype=np.float32)/255.0, axis=0)
        preds = session.run(None, {session.get_inputs()[0].name: arr})[0][0]
        for idx in preds.argsort()[-3:][::-1]:
            conf = float(preds[idx])*100
            st.markdown(f"**{CLASSES[idx]}** — {conf:.1f}%")
            st.progress(conf/100)

st.warning("For educational use only.")



