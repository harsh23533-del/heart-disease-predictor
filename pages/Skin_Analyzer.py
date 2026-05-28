import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import math

st.set_page_config(page_title="Skin Analyzer", page_icon="🧴", layout="wide")
st.title("🧴 AI Skin Analyzer")
st.caption("Upload skin/face image — AI analyzes condition and finds nearby dermatologists")

# Sidebar
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if "skin_messages" not in st.session_state:
    st.session_state.skin_messages = []
if "skin_image" not in st.session_state:
    st.session_state.skin_image = None

with st.sidebar:
    st.markdown("---")
    st.header("📍 Your Location")
    location_method = st.radio("Choose location method", ["Enter City Manually", "Enter Coordinates"])
    
    if location_method == "Enter City Manually":
        city = st.text_input("Enter your city", placeholder="e.g. Lucknow, Delhi, Mumbai")
        lat, lon = None, None
    else:
        lat = st.number_input("Latitude", value=26.8467, format="%.4f")
        lon = st.number_input("Longitude", value=80.9462, format="%.4f")
        city = None

    st.markdown("---")
    st.header("🖼️ Upload Skin Image")
    uploaded_file = st.file_uploader("Upload face or skin photo", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        st.session_state.skin_image = image
        if st.button("Clear Analysis"):
            st.session_state.skin_messages = []
            st.rerun()

# Functions
def get_coords_from_city(city_name):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        headers = {"User-Agent": "HealthcareAI/1.0"}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"]
        return None, None, None
    except:
        return None, None, None

def get_nearby_dermatologists(lat, lon, radius=5000):
    try:
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="doctors"]["healthcare:speciality"="dermatology"](around:{radius},{lat},{lon});
          node["amenity"="clinic"]["healthcare:speciality"="dermatology"](around:{radius},{lat},{lon});
          node["amenity"="hospital"](around:{radius},{lat},{lon});
          node["healthcare"="doctor"]["healthcare:speciality"="dermatology"](around:{radius},{lat},{lon});
          way["amenity"="hospital"](around:{radius},{lat},{lon});
        );
        out body;
        """
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            timeout=30
        )
        data = response.json()
        doctors = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name", "Unknown Clinic/Hospital")
            if name == "Unknown Clinic/Hospital":
                continue
            elem_lat = element.get("lat", lat)
            elem_lon = element.get("lon", lon)
            
            # Calculate distance
            dlat = math.radians(elem_lat - lat)
            dlon = math.radians(elem_lon - lon)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(elem_lat)) * math.sin(dlon/2)**2
            distance = round(6371 * 2 * math.asin(math.sqrt(a)), 2)
            
            doctors.append({
                "name": name,
                "address": tags.get("addr:full", tags.get("addr:street", "Address not available")),
                "phone": tags.get("phone", tags.get("contact:phone", "Not available")),
                "distance": distance,
                "type": tags.get("amenity", "clinic").title()
            })
        
        doctors.sort(key=lambda x: x["distance"])
        return doctors[:10]
    except Exception as e:
        return []

# Main UI
if not api_key:
    st.warning("👈 Enter your Gemini API key in the sidebar to begin")
else:
    tab1, tab2 = st.tabs(["🔬 Skin Analysis", "👨‍⚕️ Nearby Dermatologists"])
    
    with tab1:
        if not st.session_state.skin_image:
            st.info("👈 Upload a skin or face image from the sidebar to begin")
            st.markdown("""
            **What AI can detect:**
            - Acne & pimples
            - Rashes & redness
            - Dark spots & pigmentation
            - Dry skin & eczema
            - Sun damage
            - General skin health assessment
            
            ⚠️ *For educational purposes only. Always consult a dermatologist.*
            """)
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            
            if len(st.session_state.skin_messages) == 0:
                with st.spinner("AI is analyzing your skin..."):
                    try:
                        response = model.generate_content([
                            """You are an expert dermatology AI assistant. Analyze this skin/face image carefully.
                            
                            Provide:
                            1. **Skin Condition Assessment** - What you observe
                            2. **Possible Conditions** - What it might indicate
                            3. **Severity** - Mild/Moderate/Severe
                            4. **Recommended Care** - Home remedies and lifestyle tips
                            5. **When to See a Doctor** - Warning signs to watch for
                            
                            Be specific, helpful, and always recommend professional consultation for proper diagnosis.
                            Format your response clearly with these sections.""",
                            st.session_state.skin_image
                        ])
                        st.session_state.skin_messages.append({
                            "role": "assistant",
                            "content": response.text
                        })
                    except Exception as e:
                        st.error("Rate limit reached. Please wait a minute and try again.")
                        st.stop()
            
            for msg in st.session_state.skin_messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
            
            if prompt := st.chat_input("Ask about your skin condition..."):
                st.session_state.skin_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            history = "\n".join([
                                f"{m['role'].upper()}: {m['content']}"
                                for m in st.session_state.skin_messages[:-1]
                            ])
                            full_prompt = f"""You are a dermatology AI assistant.
Previous conversation: {history}
User question: {prompt}
Answer based on the skin image and conversation history."""
                            response = model.generate_content([full_prompt, st.session_state.skin_image])
                            st.write(response.text)
                            st.session_state.skin_messages.append({
                                "role": "assistant",
                                "content": response.text
                            })
                        except:
                            st.error("Rate limit reached. Please wait a minute.")
    
    with tab2:
        st.subheader("👨‍⚕️ Nearby Dermatologists & Hospitals")
        
        search_lat, search_lon = None, None
        location_name = ""
        
        if location_method == "Enter City Manually" and city:
            with st.spinner(f"Finding location for {city}..."):
                search_lat, search_lon, location_name = get_coords_from_city(city)
                if not search_lat:
                    st.error("City not found. Try a different spelling.")
        elif location_method == "Enter Coordinates":
            search_lat, search_lon = lat, lon
            location_name = f"Lat: {lat}, Lon: {lon}"
        
        if search_lat and search_lon:
            radius = st.slider("Search radius (km)", 1, 20, 5) * 1000
            
            with st.spinner("Finding nearby dermatologists..."):
                doctors = get_nearby_dermatologists(search_lat, search_lon, radius)
            
            if doctors:
                st.success(f"Found {len(doctors)} clinics/hospitals near {location_name}")
                
                cols = st.columns(2)
                for idx, doc in enumerate(doctors):
                    with cols[idx % 2]:
                        st.markdown(f"""
                        <div style="
                            border: 1px solid #e0e0e0;
                            border-radius: 12px;
                            padding: 16px;
                            margin-bottom: 12px;
                            background: white;
                            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                        ">
                            <h4 style="margin:0; color:#1a1a2e;">{doc['name']}</h4>
                            <p style="margin:4px 0; color:#666;">🏥 {doc['type']}</p>
                            <p style="margin:4px 0;">📍 {doc['address']}</p>
                            <p style="margin:4px 0;">📞 {doc['phone']}</p>
                            <p style="margin:4px 0; color:#4a90d9;">📏 {doc['distance']} km away</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No dermatologists found nearby. Try increasing the search radius.")
                st.info("💡 Tip: Try searching for a nearby major city for more results.")
        else:
            if location_method == "Enter City Manually":
                st.info("👈 Enter your city name in the sidebar and press Enter")
            else:
                st.info("👈 Enter your coordinates in the sidebar")

st.markdown("---")
st.caption("⚠️ For educational use only. Always consult a qualified dermatologist.")