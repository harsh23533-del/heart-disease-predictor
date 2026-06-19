import streamlit as st
from scanner_engine import extract_text, detect_parameters, decide_route, build_prefill, PDF_OK, OCR_OK

st.set_page_config(page_title="Healthcare AI Platform", page_icon="🏥", layout="wide")

st.markdown("<h1 style='text-align:center;'>🏥 Healthcare AI Platform</h1>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# SMART SCANNER — big, prominent, sits above everything else
# ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='padding:28px;border-radius:16px;
                background:linear-gradient(135deg,#2980b9 0%,#6dd5fa 100%);
                margin-bottom:20px;'>
        <div style='font-size:42px;text-align:center;'>🔍</div>
        <h2 style='text-align:center;color:white;margin:6px 0;'>Smart Scanner</h2>
        <p style='text-align:center;color:#eaf6ff;font-size:16px;margin:0;'>
            Upload a lab report or prescription (PDF or image) — we'll read it,
            figure out which tool fits, and pre-fill it for you.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

scan_file = st.file_uploader(
    "Drop a PDF or image of your report here",
    type=["pdf", "png", "jpg", "jpeg", "txt"],
    label_visibility="collapsed",
    key="scanner_upload",
)

if not PDF_OK:
    st.info("📦 PDF reading isn't available right now — `pdfplumber` failed to import.")
if not OCR_OK:
    st.info(
        "📦 Image scanning needs `pytesseract` plus the `tesseract-ocr` system package "
        "installed on this machine. PDFs and TXT files work without it."
    )

if scan_file is not None:
    with st.spinner("Reading your report..."):
        raw_text = extract_text(scan_file)

    if not raw_text.strip():
        st.error(
            "Couldn't pull any text out of that file. If it's a scanned image, "
            "make sure tesseract-ocr is installed — or try a clearer PDF/TXT."
        )
    else:
        found = detect_parameters(raw_text)
        route = decide_route(found, raw_text)
        prefill = build_prefill(found)

        if found:
            st.success(f"Found {len(found)} recognized value(s): {', '.join(found.keys())}")
        else:
            st.warning("Couldn't recognize specific lab values — routing based on general content instead.")

        # stash for the destination page to pick up
        st.session_state["prefill"] = prefill
        st.session_state["prefill_target"] = route

        page_map = {
            "Heart_Disease": "pages/Heart_Disease.py",
            "Blood_Kidney": "pages/Blood_Kidney.py",
            "Lab_Report": "pages/Lab_Report.py",
        }
        st.info(f"Sending you to **{route.replace('_', ' ')}**...")
        st.switch_page(page_map[route])

st.markdown("---")

# ─────────────────────────────────────────────────────────────────
# Existing tool grid (unchanged)
# ─────────────────────────────────────────────────────────────────
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