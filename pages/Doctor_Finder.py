import streamlit as st
import pandas as pd

st.set_page_config(page_title="Doctor Finder", page_icon="👨‍⚕️", layout="wide")
st.title("👨‍⚕️ Doctor Finder")
st.caption("Find the best doctors by specialty and ratings")

# Sample doctor data
doctors = [
    {"name": "Dr. Rajesh Sharma", "specialty": "Cardiologist", "rating": 4.9, "experience": 15, "location": "Delhi", "fee": 800, "available": True},
    {"name": "Dr. Priya Mehta", "specialty": "Cardiologist", "rating": 4.7, "experience": 12, "location": "Mumbai", "fee": 1000, "available": True},
    {"name": "Dr. Amit Verma", "specialty": "Cardiologist", "rating": 4.5, "experience": 8, "location": "Bangalore", "fee": 700, "available": False},
    {"name": "Dr. Sunita Rao", "specialty": "Nephrologist", "rating": 4.8, "experience": 14, "location": "Delhi", "fee": 900, "available": True},
    {"name": "Dr. Vikram Singh", "specialty": "Nephrologist", "rating": 4.6, "experience": 10, "location": "Mumbai", "fee": 850, "available": True},
    {"name": "Dr. Kavita Joshi", "specialty": "Nephrologist", "rating": 4.4, "experience": 7, "location": "Chennai", "fee": 750, "available": False},
    {"name": "Dr. Rohit Gupta", "specialty": "General Physician", "rating": 4.7, "experience": 11, "location": "Delhi", "fee": 500, "available": True},
    {"name": "Dr. Meena Patel", "specialty": "General Physician", "rating": 4.5, "experience": 9, "location": "Ahmedabad", "fee": 400, "available": True},
    {"name": "Dr. Arjun Nair", "specialty": "General Physician", "rating": 4.3, "experience": 6, "location": "Bangalore", "fee": 450, "available": True},
    {"name": "Dr. Deepa Krishnan", "specialty": "Hematologist", "rating": 4.9, "experience": 16, "location": "Chennai", "fee": 1100, "available": True},
    {"name": "Dr. Sanjay Malhotra", "specialty": "Hematologist", "rating": 4.6, "experience": 13, "location": "Delhi", "fee": 950, "available": False},
    {"name": "Dr. Anita Desai", "specialty": "Hematologist", "rating": 4.4, "experience": 8, "location": "Mumbai", "fee": 800, "available": True},
    {"name": "Dr. Ravi Kumar", "specialty": "Diabetologist", "rating": 4.8, "experience": 14, "location": "Hyderabad", "fee": 700, "available": True},
    {"name": "Dr. Pooja Agarwal", "specialty": "Diabetologist", "rating": 4.6, "experience": 10, "location": "Delhi", "fee": 650, "available": True},
    {"name": "Dr. Kiran Shah", "specialty": "Diabetologist", "rating": 4.5, "experience": 9, "location": "Mumbai", "fee": 750, "available": False},
    {"name": "Dr. Suresh Iyer", "specialty": "Pulmonologist", "rating": 4.7, "experience": 12, "location": "Bangalore", "fee": 850, "available": True},
    {"name": "Dr. Nalini Reddy", "specialty": "Pulmonologist", "rating": 4.5, "experience": 8, "location": "Hyderabad", "fee": 800, "available": True},
    {"name": "Dr. Anil Chopra", "specialty": "Orthopedic", "rating": 4.8, "experience": 15, "location": "Delhi", "fee": 900, "available": True},
    {"name": "Dr. Smita Kulkarni", "specialty": "Orthopedic", "rating": 4.6, "experience": 11, "location": "Pune", "fee": 850, "available": False},
    {"name": "Dr. Manoj Tiwari", "specialty": "Neurologist", "rating": 4.9, "experience": 18, "location": "Delhi", "fee": 1200, "available": True},
]

df = pd.DataFrame(doctors)

# Filters
with st.sidebar:
    st.header("🔍 Filter Doctors")
    specialty = st.selectbox("Specialty", ["All"] + sorted(df["specialty"].unique().tolist()))
    location = st.selectbox("Location", ["All"] + sorted(df["location"].unique().tolist()))
    min_rating = st.slider("Minimum Rating", 1.0, 5.0, 4.0, 0.1)
    available_only = st.checkbox("Available Only", value=False)
    sort_by = st.selectbox("Sort By", ["Rating (High to Low)", "Fee (Low to High)", "Experience (High to Low)"])

# Apply filters
filtered = df.copy()
if specialty != "All":
    filtered = filtered[filtered["specialty"] == specialty]
if location != "All":
    filtered = filtered[filtered["location"] == location]
filtered = filtered[filtered["rating"] >= min_rating]
if available_only:
    filtered = filtered[filtered["available"] == True]

# Sort
if sort_by == "Rating (High to Low)":
    filtered = filtered.sort_values("rating", ascending=False)
elif sort_by == "Fee (Low to High)":
    filtered = filtered.sort_values("fee", ascending=True)
else:
    filtered = filtered.sort_values("experience", ascending=False)

# Results count
st.markdown(f"### Found {len(filtered)} doctors")
st.markdown("---")

# Display doctor cards
if len(filtered) == 0:
    st.warning("No doctors found with selected filters. Try adjusting the filters.")
else:
    cols = st.columns(3)
    for idx, (_, doctor) in enumerate(filtered.iterrows()):
        with cols[idx % 3]:
            availability = "🟢 Available" if doctor["available"] else "🔴 Busy"
            stars = "⭐" * int(doctor["rating"])
            
            st.markdown(f"""
            <div style="
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                background: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            ">
                <h3 style="margin:0; color:#1a1a2e; font-size:16px;">{doctor['name']}</h3>
                <p style="margin:4px 0; color:#4a90d9; font-weight:600;">{doctor['specialty']}</p>
                <p style="margin:4px 0;">⭐ {doctor['rating']} &nbsp;|&nbsp; 📍 {doctor['location']}</p>
                <p style="margin:4px 0;">🏥 {doctor['experience']} years exp &nbsp;|&nbsp; 💰 ₹{doctor['fee']}</p>
                <p style="margin:4px 0;">{availability}</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("⚠️ Sample data for educational purposes. Always verify doctor credentials.")