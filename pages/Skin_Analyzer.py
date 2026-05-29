import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
import json

st.set_page_config(page_title="Skin Analyzer", page_icon="🧴", layout="wide")

@st.cache_resource
def load_model():
    model = tf.keras.models.load_model('skin_disease_model.h5')
    with open('classes.json', 'r') as f:
        classes = json.load(f)
    return model, classes

DISEASE_INFO = {
    'nv': ('Melanocytic Nevi', 'Normal mole - Safe!', 'No treatment needed.', '#27ae60'),
    'mel': ('Melanoma', 'Serious skin cancer!', 'See doctor immediately!', '#e74c3c'),
    'bkl': ('Benign Keratosis', 'Harmless skin growth!', 'Not cancer - dont worry.', '#f39c12'),
    'bcc': ('Basal Cell Carcinoma', 'Common skin cancer.', 'Doctor visit needed.', '#e67e22'),
    'akiec': ('Actinic Keratosis', 'Pre-cancerous lesion!', 'See doctor soon.', '#c0392b'),
    'vasc': ('Vascular Lesion', 'Blood vessel related.', 'Usually safe.', '#3498db'),
    'df': ('Dermatofibroma', 'Harmless nodule.', 'Safe - not cancer.', '#9b59b6'),
}

st.title("Skin Analyzer AI")
st.caption("Upload skin photo - AI will analyze it")
st.markdown("---")

try:
    model, classes = load_model()
    st.success("AI Model loaded!")
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

uploaded = st.file_uploader("Upload skin photo", type=['jpg', 'jpeg', 'png'])

if uploaded:
    image = Image.open(uploaded).convert('RGB')
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(image, caption="Your Photo", use_container_width=True)

    with col2:
        with st.spinner("Analyzing..."):
            img = image.resize((128, 128))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            predictions = model.predict(img_array)[0]
            top_idx = np.argmax(predictions)
            top_class = classes[top_idx]
            confidence = predictions[top_idx] * 100
            name, status, advice, color = DISEASE_INFO.get(top_class, (top_class, 'Unknown', 'See doctor', '#666'))

            st.subheader("Result:")
            st.write(f"**Condition:** {name}")
            st.write(f"**Status:** {status}")
            st.write(f"**Advice:** {advice}")
            st.write(f"**Confidence:** {confidence:.1f}%")

            if confidence > 80:
                st.success("High confidence result!")
            elif confidence > 50:
                st.warning("Medium confidence - confirm with doctor!")
            else:
                st.error("Low confidence - please see doctor!")

            st.subheader("All Predictions:")
            for cls, prob in sorted(zip(classes, predictions), key=lambda x: x[1], reverse=True):
                pname = DISEASE_INFO.get(cls, (cls,))[0]
                st.progress(float(prob), text=f"{pname}: {prob*100:.1f}%")

            st.warning("Educational use only - not a substitute for doctor!")

st.markdown("---")
st.caption("Built by Harsh Pandey - HAM10000 Dataset - 10015 images - 7 conditions")