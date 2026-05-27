import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Blood & Kidney Analyzer", page_icon="🩸", layout="wide")
st.title("🩸 Blood & Kidney Test Analyzer")
st.caption("Analyze CBC and kidney function · For educational use only")

with st.sidebar:
    st.header("Enter Test Values")
    st.subheader("CBC (Blood Count)")
    hemoglobin = st.slider("Hemoglobin (g/dL)", 4.0, 20.0, 13.5)
    wbc = st.slider("WBC (x10³/µL)", 1.0, 30.0, 7.0)
    platelets = st.slider("Platelets (x10³/µL)", 50.0, 800.0, 250.0)
    st.subheader("Kidney Function")
    creatinine = st.slider("Creatinine (mg/dL)", 0.4, 15.0, 1.0)
    bun = st.slider("BUN (mg/dL)", 5.0, 100.0, 15.0)
    egfr = st.slider("eGFR (mL/min)", 5.0, 120.0, 90.0)

def calculate_risks(hgb, wbc_val, plt_val, cr, bun_val, egfr_val):
    risks = {}
    if hgb < 8:
        risks['Anemia'] = 90
    elif hgb < 11:
        risks['Anemia'] = 65
    elif hgb < 12:
        risks['Anemia'] = 35
    else:
        risks['Anemia'] = 5

    if wbc_val > 20:
        risks['Infection'] = 85
    elif wbc_val > 11:
        risks['Infection'] = 55
    elif wbc_val < 3:
        risks['Infection'] = 70
    else:
        risks['Infection'] = 10

    if plt_val < 50:
        risks['Bleeding Risk'] = 90
    elif plt_val < 100:
        risks['Bleeding Risk'] = 60
    elif plt_val < 150:
        risks['Bleeding Risk'] = 25
    else:
        risks['Bleeding Risk'] = 5

    if egfr_val < 15:
        risks['Kidney Failure'] = 95
    elif egfr_val < 30:
        risks['Kidney Failure'] = 80
    elif egfr_val < 60:
        risks['Kidney Failure'] = 55
    elif egfr_val < 90:
        risks['Kidney Failure'] = 25
    else:
        risks['Kidney Failure'] = 5

    return risks

risks = calculate_risks(hemoglobin, wbc, platelets, creatinine, bun, egfr)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Risk Summary")
    for condition, risk in risks.items():
        color = "🔴" if risk > 60 else "🟡" if risk > 30 else "🟢"
        st.metric(label=f"{color} {condition}", value=f"{risk}%")

with col2:
    colors = ["#e74c3c" if v > 60 else "#f39c12" if v > 30 else "#2ecc71" for v in risks.values()]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(risks.keys()), y=list(risks.values()), marker_color=colors))
    fig.update_layout(title="Risk Levels", yaxis=dict(range=[0, 100], title="Risk %"), height=350)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("📋 Normal Reference Ranges")
ref_data = {
    "Test": ["Hemoglobin", "WBC", "Platelets", "Creatinine", "BUN", "eGFR"],
    "Normal Range": ["12-17 g/dL", "4-11 x10³/µL", "150-400 x10³/µL", "0.6-1.2 mg/dL", "7-20 mg/dL", ">90 mL/min"],
    "Your Value": [str(hemoglobin), str(wbc), str(platelets), str(creatinine), str(bun), str(egfr)]
}
st.dataframe(pd.DataFrame(ref_data), use_container_width=True)
st.caption("⚠️ For educational purposes only. Always consult a doctor.")