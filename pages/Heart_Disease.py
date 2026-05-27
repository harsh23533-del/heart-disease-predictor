import os
import streamlit as st
import pandas as pd
import numpy as np
import shap, joblib, plotly.graph_objects as go
from data_loader import load_data, preprocess
from xgboost import XGBClassifier

# Auto-train if model files missing (needed for cloud deployment)
if not os.path.exists('model.pkl'):
    st.warning("Training model for the first time... please wait 2-3 minutes ⏳")
    df = load_data()
    X_train, X_test, y_train, y_test, scaler, feature_names = preprocess(df)
    model = XGBClassifier(n_estimators=200, max_depth=5, learning_rate=0.05,
                          subsample=0.8, colsample_bytree=0.8, random_state=42,
                          eval_metric='logloss')
    model.fit(X_train, y_train)
    joblib.dump(model, 'model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    joblib.dump(feature_names, 'features.pkl')

model         = joblib.load('model.pkl')
scaler        = joblib.load('scaler.pkl')
feature_names = joblib.load('features.pkl')
explainer     = shap.TreeExplainer(model)

st.set_page_config(page_title="Heart Disease Risk Predictor", page_icon="🫀", layout="wide")
st.title("🫀 Heart Disease Risk Predictor")
st.caption("XGBoost model trained on Cleveland Heart Disease dataset · For educational use only")

with st.sidebar:
    st.header("Patient Information")
    age      = st.slider("Age", 20, 80, 50)
    sex      = st.selectbox("Sex", [0, 1], format_func=lambda x: "Female" if x==0 else "Male")
    cp       = st.selectbox("Chest pain type", [0,1,2,3],
                            format_func=lambda x: ['Typical angina','Atypical angina',
                                                   'Non-anginal','Asymptomatic'][x])
    trestbps = st.slider("Resting blood pressure (mmHg)", 90, 200, 120)
    chol     = st.slider("Cholesterol (mg/dl)", 100, 600, 200)
    fbs      = st.selectbox("Fasting blood sugar > 120 mg/dl", [0,1], format_func=lambda x: "No" if x==0 else "Yes")
    restecg  = st.selectbox("Resting ECG", [0,1,2])
    thalach  = st.slider("Max heart rate achieved", 60, 220, 150)
    exang    = st.selectbox("Exercise-induced angina", [0,1], format_func=lambda x: "No" if x==0 else "Yes")
    oldpeak  = st.slider("ST depression (oldpeak)", 0.0, 6.5, 1.0, 0.1)
    slope    = st.selectbox("Slope of peak exercise ST", [0,1,2])
    ca       = st.selectbox("Major vessels coloured by fluoroscopy", [0,1,2,3])
    thal     = st.selectbox("Thalassemia", [1,2,3], format_func=lambda x: ['','Fixed defect','Normal','Reversible defect'][x])

input_data = pd.DataFrame([[age,sex,cp,trestbps,chol,fbs,restecg,
                            thalach,exang,oldpeak,slope,ca,thal]],
                          columns=feature_names)
input_scaled = scaler.transform(input_data)

prob     = model.predict_proba(input_scaled)[0][1]
risk_pct = int(prob * 100)

col1, col2 = st.columns([1, 2])

with col1:
    color = "#e74c3c" if prob > 0.5 else "#2ecc71"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_pct,
        number={'suffix': '%', 'font': {'size': 48}},
        title={'text': "Heart Disease Risk"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': color},
               'steps': [{'range':[0,40],'color':'#d5f5e3'},
                         {'range':[40,70],'color':'#fdebd0'},
                         {'range':[70,100],'color':'#fadbd8'}],
               'threshold': {'line':{'color':'red','width':4},'thickness':0.75,'value':50}}
    ))
    fig.update_layout(height=300, margin=dict(t=40,b=0,l=0,r=0))
    st.plotly_chart(fig, use_container_width=True)
    verdict = "⚠️ **High Risk**" if prob > 0.5 else "✅ **Low Risk**"
    st.markdown(f"### {verdict}")

with col2:
    shap_values = explainer.shap_values(input_scaled)
    vals = shap_values[0] if isinstance(shap_values, list) else shap_values[0]
    shap_df = pd.DataFrame({'Feature': feature_names, 'SHAP': vals}).sort_values('SHAP')
    colors = ['#e74c3c' if v > 0 else '#2ecc71' for v in shap_df['SHAP']]
    fig2 = go.Figure(go.Bar(x=shap_df['SHAP'], y=shap_df['Feature'],
                            orientation='h', marker_color=colors))
    fig2.update_layout(title="Feature Impact (SHAP values)",
                       xaxis_title="Impact on prediction",
                       height=420, margin=dict(t=40,b=0,l=0,r=0))
    st.plotly_chart(fig2, use_container_width=True)