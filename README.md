🚀 Live App: https://heart-disease-predictor-kwyhoqzo9kzch75zvokxrc.streamlit.app/
# 🏥 Healthcare AI Platform

A multi-page **Streamlit** app with a **Smart Scanner** that reads an uploaded lab report (PDF/image/text), auto-detects the medical parameters in it, and routes you straight to the right tool — pre-filled.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-AUC--ROC%200.9453-orange)
![ONNX](https://img.shields.io/badge/ONNX%20Runtime-enabled-blue)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

> ⚠️ For educational use only. Not a substitute for professional medical advice.

---

## 🔍 Smart Scanner (entry point — `app.py`)

- Upload a PDF, image (PNG/JPG), or TXT report
- Extracts text via `pdfplumber` (PDF) or `pytesseract` OCR (image)
- Regex-matches 20+ known lab parameters (hemoglobin, glucose, creatinine, cholesterol, TSH, etc.) via `scanner_engine.py`
- Auto-routes to **Heart Disease**, **Blood & Kidney**, or **Lab Report** based on which parameters were found (falls back to symptom-keyword matching if no numeric values are detected)
- Pre-fills the destination page's sliders with the detected values

## 🧰 Tools

| Tool | File | What it does |
|---|---|---|
| 🫀 Heart Disease Predictor | `pages/Heart_Disease.py` | XGBoost model (trained on UCI Cleveland dataset, **AUC-ROC 0.9453**) + SHAP explainability, auto-trains on first run if `model.pkl` is missing |
| 🩸 Blood & Kidney Analyzer | `pages/Blood_Kidney.py` | Rule-based CBC + kidney function (creatinine, BUN, eGFR) analysis with slider inputs |
| ⚖️ BMI Calculator | `pages/BMI_Calculator.py` | Metric/Imperial BMI + category, with Plotly visualization |
| 👨‍⚕️ Doctor Finder | `pages/Doctor_Finder.py` | Live nearby doctor search using GPS + OpenStreetMap Overpass API, distance via geopy, map via folium |
| 🧴 Skin Analyzer | `pages/Skin_Analyzer.py` | 23-class skin condition classifier (DermNet categories) via ONNX Runtime |
| 📄 Lab Report Summarizer | `pages/Lab_Report.py` | Rule-based multilingual (7+ languages) PDF/TXT lab report parser — no API needed |
| 🎤 Voice Assistant | `pages/Voice_Assistant.py` | Speech-to-text health Q&A in 7 Indian languages, answered via an LLM through OpenRouter API |

> Note: `app.py`'s tool grid also links a "Medical Image AI" card (`pages/Medical_Image.py`) — that page doesn't exist in the repo yet.

## 🛠️ Tech Stack

- **Frontend:** Streamlit (multi-page)
- **ML/DL:** XGBoost, Optuna (hyperparameter tuning in `train.py`), scikit-learn, ONNX Runtime
- **Explainability/Viz:** SHAP, Plotly
- **OCR/Parsing:** pdfplumber, pytesseract
- **Maps/Location:** Overpass API, folium, streamlit-folium, geopy
- **AI Chat:** OpenRouter API (Voice Assistant only)
- **Containerized:** Dockerfile included (Python 3.11-slim)

## 📂 Project Structure

```
heart-disease-predictor/
├── app.py                  # Main entry — Smart Scanner + tool grid
├── Home.py                 # Simpler 2-tool landing page (alt entry)
├── scanner_engine.py       # Text extraction, parameter detection, routing logic
├── data_loader.py          # Loads + preprocesses UCI Cleveland heart dataset
├── train.py                # Optuna-tuned XGBoost training script
├── classes.json            # 23 skin condition class labels
├── skin_disease_model.onnx / .h5 / skin_model.tflite
├── pages/
│   ├── Heart_Disease.py
│   ├── Blood_Kidney.py
│   ├── BMI_Calculator.py
│   ├── Doctor_Finder.py
│   ├── Skin_Analyzer.py
│   ├── Lab_Report.py
│   └── Voice_Assistant.py
├── Dockerfile
└── requirements.txt
```

## ⚙️ Setup

```bash
git clone https://github.com/harsh23533-del/heart-disease-predictor.git
cd heart-disease-predictor
pip install -r requirements.txt
```

For the **Voice Assistant**, add in `.streamlit/secrets.toml`:

```toml
OPENROUTER_API_KEY = "your-key-here"
```

For image OCR (**Smart Scanner**), also install the system package `tesseract-ocr` — pip alone isn't enough.

## ▶️ Run

```bash
streamlit run app.py
```

## 🐳 Docker

```bash
docker build -t healthcare-ai .
docker run -p 8501:8501 healthcare-ai
```

## 📄 License

MIT — for educational use only. Not a substitute for professional medical advice.
