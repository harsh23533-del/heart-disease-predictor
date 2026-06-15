# 🏥 Healthcare AI Platform

A multi-page Streamlit web app offering AI-powered health analysis tools — heart disease risk prediction, blood & kidney report analysis, BMI calculator, multilingual lab report summarizer, skin condition analyzer, and a doctor finder.

🔗 **Live App:** [https://heart-disease-predictor-kwyhoqzo9kzch75zvokxrc.streamlit.app/]

---

## ✨ Features

### ❤️ Heart Disease Predictor
- ML-based risk prediction using **XGBoost (94.53% AUC-ROC)**
- Interactive **Plotly risk gauge**
- **SHAP-based explainability** charts showing feature contributions

### 🩸 Blood & Kidney Analyzer
- AI-powered analysis of blood and kidney function reports
- Powered by **Gemini API**

### 📋 Lab Report Analyzer
- Multilingual lab report summarizer (Hindi, English + 5 Indian languages)
- Rule-based — works without any API

### 🧮 BMI Calculator
- Calculates BMI and health category instantly

### 👨‍⚕️ Doctor Finder
- Helps users find relevant doctors/specialists based on condition

### 🩹 Skin Analyzer
- Skin disease classification using an **ONNX** model (converted from TensorFlow for Streamlit Cloud compatibility)
- Powered by **Gemini API**

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit (multi-page app)
- **ML/DL:** XGBoost, TensorFlow → ONNX Runtime
- **Explainability/Viz:** SHAP, Plotly
- **AI/LLM:** Google Gemini API (multi-key rotation for rate limit handling)
- **Deployment:** Streamlit Cloud

---

## 📂 Project Structure

```
heart-disease-predictor/
├── app.py                          # Main entry point
├── pages/
│   ├── 1_Heart_Disease_Predictor.py
│   ├── 2_Blood_Kidney_Analyzer.py
│   ├── 3_BMI_Calculator.py
│   ├── 4_Doctor_Finder.py
│   ├── 5_Lab_Report_Analyzer.py
│   └── 6_Skin_Analyzer.py
├── models/
│   ├── heart_model.pkl
│   └── skin_model.onnx
├── requirements.txt
└── .streamlit/
    └── secrets.toml                # API keys (NOT committed)
```

---

## ⚙️ Setup & Installation

```bash
git clone https://github.com/harsh23533-del/heart-disease-predictor.git
cd heart-disease-predictor

conda create -n heart_env python=3.10
conda activate heart_env

pip install -r requirements.txt
```

---

## 🔑 Configuration

Add API keys in `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY_1 = "your-key-here"
GEMINI_API_KEY_2 = "your-backup-key"
```

⚠️ Never commit `secrets.toml` — add it to `.gitignore`.

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

---

## 📊 Model Details

| Model | Algorithm | Metric | Format |
|---|---|---|---|
| Heart Disease Predictor | XGBoost | 94.53% AUC-ROC | `.pkl` |
| Skin Analyzer | CNN (transfer learning) | — | `.onnx` |

---

## 🚀 Deployment

Deployed on **Streamlit Cloud** with API keys managed via Streamlit Secrets.

---

## 🔮 Future Improvements

- Add more disease prediction modules
- Expand multilingual support
- Add user authentication & history tracking

---

## 📄 License

This project is licensed under the MIT License.
