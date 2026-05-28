import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="BMI Calculator", page_icon="⚖️", layout="wide")
st.title("⚖️ BMI Calculator & Health Analyzer")
st.caption("Calculate your BMI and get personalized health insights")

with st.sidebar:
    st.header("Enter Your Details")
    unit = st.radio("Unit System", ["Metric (kg/cm)", "Imperial (lbs/ft)"])
    
    if unit == "Metric (kg/cm)":
        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0)
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
        height_m = height / 100
    else:
        weight_lbs = st.number_input("Weight (lbs)", min_value=1.0, max_value=700.0, value=154.0)
        height_ft = st.number_input("Height (ft)", min_value=1.0, max_value=8.0, value=5.0)
        height_in = st.number_input("Height (inches)", min_value=0.0, max_value=11.0, value=7.0)
        weight = weight_lbs * 0.453592
        height_m = (height_ft * 12 + height_in) * 0.0254

    age = st.number_input("Age", min_value=1, max_value=120, value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])

# Calculate BMI
bmi = weight / (height_m ** 2)
bmi = round(bmi, 1)

# BMI Category
if bmi < 18.5:
    category = "Underweight"
    color = "#3498db"
    emoji = "📉"
    advice = "You are underweight. Consider a nutritious diet with more calories."
elif bmi < 25:
    category = "Normal Weight"
    color = "#2ecc71"
    emoji = "✅"
    advice = "Great! You have a healthy weight. Keep maintaining your lifestyle."
elif bmi < 30:
    category = "Overweight"
    color = "#f39c12"
    emoji = "⚠️"
    advice = "You are slightly overweight. Consider more physical activity and a balanced diet."
else:
    category = "Obese"
    color = "#e74c3c"
    emoji = "🔴"
    advice = "Your BMI indicates obesity. Please consult a doctor for a health plan."

# Ideal weight range
ideal_min = round(18.5 * (height_m ** 2), 1)
ideal_max = round(24.9 * (height_m ** 2), 1)

# Display
col1, col2 = st.columns([1, 2])

with col1:
    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bmi,
        number={'suffix': ' BMI', 'font': {'size': 40}},
        title={'text': f"{emoji} {category}"},
        gauge={
            'axis': {'range': [10, 40]},
            'bar': {'color': color},
            'steps': [
                {'range': [10, 18.5], 'color': '#d6eaf8'},
                {'range': [18.5, 25], 'color': '#d5f5e3'},
                {'range': [25, 30], 'color': '#fdebd0'},
                {'range': [30, 40], 'color': '#fadbd8'}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': bmi
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div style="background:{color}20; border-left: 4px solid {color}; padding:12px; border-radius:8px;">
        <b>Your BMI: {bmi}</b><br>
        Category: {category}<br>
        Ideal weight: {ideal_min} - {ideal_max} kg
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("📊 BMI Categories")
    categories = ["Underweight", "Normal", "Overweight", "Obese"]
    ranges = ["< 18.5", "18.5 - 24.9", "25 - 29.9", "≥ 30"]
    colors_list = ["#3498db", "#2ecc71", "#f39c12", "#e74c3c"]
    
    for cat, rng, clr in zip(categories, ranges, colors_list):
        marker = "◀ You are here" if cat.lower() in category.lower() or (cat == "Normal" and category == "Normal Weight") else ""
        st.markdown(f"""
        <div style="display:flex; align-items:center; margin:8px 0;">
            <div style="width:20px; height:20px; background:{clr}; border-radius:4px; margin-right:10px;"></div>
            <span><b>{cat}</b> (BMI {rng})</span>
            <span style="color:{clr}; margin-left:10px; font-weight:bold;">{marker}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("💡 Personal Advice")
    st.info(advice)

    # Health metrics
    st.subheader("📋 Your Health Summary")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("BMI", bmi)
    with col_b:
        st.metric("Category", category)
    with col_c:
        weight_diff = round(weight - ideal_min, 1) if bmi > 24.9 else round(ideal_min - weight, 1) if bmi < 18.5 else 0
        if bmi > 24.9:
            st.metric("To lose", f"{weight_diff} kg")
        elif bmi < 18.5:
            st.metric("To gain", f"{weight_diff} kg")
        else:
            st.metric("Status", "✅ Ideal")

st.markdown("---")

# Tips section
st.subheader("🥗 Health Tips")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🍎 Diet Tips**
    - Eat more fruits & vegetables
    - Reduce processed foods
    - Stay hydrated (8 glasses/day)
    - Control portion sizes
    """)

with col2:
    st.markdown("""
    **🏃 Exercise Tips**
    - 30 min walk daily
    - Strength training 3x/week
    - Yoga for flexibility
    - Take stairs instead of lift
    """)

with col3:
    st.markdown("""
    **😴 Lifestyle Tips**
    - Sleep 7-8 hours daily
    - Reduce stress
    - Avoid smoking & alcohol
    - Regular health checkups
    """)

st.caption("⚠️ BMI is a general indicator. Consult a doctor for complete health assessment.")