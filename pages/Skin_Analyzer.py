import streamlit as st
import numpy as np
from PIL import Image
import json

st.set_page_config(page_title="Skin Analyzer", page_icon="🧴", layout="wide")

DISEASE_INFO = {
    "nv":    ("Melanocytic Nevi",     "✅ Normal mole - Safe hai",        "Koi treatment nahi. Agar size badle toh doctor dikhao.", "#27ae60"),
    "mel":   ("Melanoma",             "🚨 Serious skin cancer ho sakta",  "ABHI doctor ke paas jao - deri mat karo!",              "#e74c3c"),
    "bkl":   ("Benign Keratosis",     "✅ Harmless skin growth",          "Cancer nahi hai - chinta mat karo.",                    "#f39c12"),
    "bcc":   ("Basal Cell Carcinoma", "⚠️ Common skin cancer",           "Doctor visit zaruri hai.",                              "#e67e22"),
    "akiec": ("Actinic Keratosis",    "⚠️ Pre-cancerous lesion",         "Jaldi doctor se milein.",                               "#c0392b"),
    "vasc":  ("Vascular Lesion",      "✅ Blood vessel related",          "Usually safe - dard ho toh doctor dikhao.",             "#3498db"),
    "df":    ("Dermatofibroma",       "✅ Harmless nodule",               "Safe hai - cancer nahi.",                               "#9b59b6"),
}

@st.cache_resource
def load_model():
    import onnxruntime as ort
    sess = ort.InferenceSession("skin_model.onnx")
    with open("classes.json") as f:
        classes = json.load(f)
    return sess, classes

def predict(image, sess, classes):
    img = image.resize((128, 128))
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)
    inp_name = sess.get_inputs()[0].name
    preds = sess.run(None, {inp_name: arr})[0][0]
    return preds

st.markdown("<h1 style='text-align:center'>🧴 AI Skin Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888'>Trained on 10,015 real images (HAM10000 Dataset)</p>", unsafe_allow_html=True)
st.markdown("---")

try:
    sess, classes = load_model()
    st.success("✅ AI Model loaded!")
except Exception as e:
    st.error(f"Model load failed: {e}")
    st.info("skin_model.onnx aur classes.json project root mein hone chahiye.")
    st.stop()

uploaded = st.file_uploader("📸 Skin photo upload karo", type=["jpg","jpeg","png"])

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(image, use_container_width=True)

    with col2:
        with st.spinner("Analyzing..."):
            preds   = predict(image, sess, classes)
            top_idx = int(np.argmax(preds))
            top_cls = classes[top_idx]
            conf    = float(preds[top_idx]) * 100
            name, status, advice, color = DISEASE_INFO.get(top_cls, (top_cls, "Unknown", "Doctor se milein", "#666"))

        st.markdown(
            f"<div style='padding:20px;border-radius:12px;border-left:6px solid {color};background:{color}22'>"
            f"<h2 style='color:{color};margin:0'>{name}</h2>"
            f"<h3>{status}</h3>"
            f"<p>💡 {advice}</p>"
            f"<b>Confidence: {conf:.1f}%</b></div>",
            unsafe_allow_html=True
        )

        if conf > 80:
            st.success("🎯 High confidence result!")
        elif conf > 50:
            st.warning("🤔 Medium confidence - doctor se confirm karo.")
        else:
            st.error("❓ Low confidence - please doctor se milein.")

        st.markdown("### 📊 All Predictions")
        for cls, prob in sorted(zip(classes, preds), key=lambda x: x[1], reverse=True):
            pname = DISEASE_INFO.get(cls, (cls,))[0]
            st.progress(float(prob), text=f"{pname}: {prob*100:.1f}%")

        st.warning("⚠️ Educational use only - doctor ki jagah nahi hai.")

st.markdown("---")
st.caption("Built by Harsh Pandey · HAM10000 · 10,015 images · 7 conditions")
