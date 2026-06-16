import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import urllib.parse

st.set_page_config(page_title="Doctor Finder", page_icon="🏥", layout="wide")

st.markdown("""
<style>
.doctor-card {
    background: #1a1a2e;
    border: 1px solid #16213e;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
}
.doctor-card:hover { border-color: #0f3460; }
.badge-open { background: #1a4731; color: #4ade80; padding: 2px 10px; border-radius: 20px; font-size: 12px; }
.badge-closed { background: #3b1e1e; color: #f87171; padding: 2px 10px; border-radius: 20px; font-size: 12px; }
.dist-badge { background: #1e3a5f; color: #60a5fa; padding: 2px 10px; border-radius: 20px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🏥 Doctor Finder — Live Nearby Search")
st.caption("Finds real hospitals, clinics & doctors near your current location using OpenStreetMap")

# ── Sidebar Controls ──────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Search Settings")
    specialty = st.selectbox("Specialty", [
        "All (Doctors & Clinics)",
        "Hospital",
        "Clinic / General Physician",
        "Pharmacy",
        "Dentist",
        "Physiotherapy",
        "Eye / Ophthalmology",
    ])
    radius_km = st.slider("Search Radius (km)", 1, 20, 5)
    max_results = st.slider("Max Results", 5, 30, 15)
    st.markdown("---")
    st.info("📍 Location is fetched from your browser or entered manually below.")

# ── Location Input ────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    location_method = st.radio(
        "How to get your location?",
        ["📍 Enter City / Address", "🌐 Enter Coordinates Manually"],
        horizontal=True
    )

with col2:
    st.empty()

lat, lon = None, None
location_name = ""

if location_method == "📍 Enter City / Address":
    address_input = st.text_input(
        "Enter your location",
        placeholder="e.g. Hazratganj, Lucknow  or  Sultanpur, UP",
        help="Be specific — add city name for best results"
    )
    if address_input:
        with st.spinner("📡 Locating..."):
            try:
                geo = Nominatim(user_agent="healthcare_ai_platform_harsh")
                loc = geo.geocode(address_input + ", India", timeout=10)
                if loc:
                    lat, lon = loc.latitude, loc.longitude
                    location_name = loc.address
                    st.success(f"📍 Found: {location_name[:80]}...")
                else:
                    st.error("Location not found. Try adding city name.")
            except Exception as e:
                st.error(f"Geocoding error: {e}")

else:
    c1, c2 = st.columns(2)
    with c1:
        lat = st.number_input("Latitude", value=26.8467, format="%.6f")
    with c2:
        lon = st.number_input("Longitude", value=80.9462, format="%.6f")
    location_name = f"{lat}, {lon}"

# ── Overpass API Query ─────────────────────────────────────────────
def build_overpass_query(lat, lon, radius_m, specialty):
    amenity_map = {
        "All (Doctors & Clinics)": '["amenity"~"hospital|clinic|doctors|pharmacy"]',
        "Hospital": '["amenity"="hospital"]',
        "Clinic / General Physician": '["amenity"~"clinic|doctors"]',
        "Pharmacy": '["amenity"="pharmacy"]',
        "Dentist": '["amenity"="dentist"]',
        "Physiotherapy": '["healthcare"="physiotherapist"]',
        "Eye / Ophthalmology": '["healthcare"~"optometrist|ophthalmology"]',
    }
    tag_filter = amenity_map.get(specialty, '["amenity"~"hospital|clinic|doctors"]')
    return f"""
    [out:json][timeout:25];
    (
      node{tag_filter}(around:{radius_m},{lat},{lon});
      way{tag_filter}(around:{radius_m},{lat},{lon});
    );
    out center tags;
    """

def fetch_nearby_doctors(lat, lon, radius_km, specialty, max_results):
    radius_m = radius_km * 1000
    query = build_overpass_query(lat, lon, radius_m, specialty)
    url = "https://overpass-api.de/api/interpreter"
    try:
        resp = requests.post(url, data={"data": query}, timeout=30)
        resp.raise_for_status()
        elements = resp.json().get("elements", [])
        results = []
        for el in elements:
            tags = el.get("tags", {})
            # Get coordinates
            if el["type"] == "node":
                elat, elon = el.get("lat"), el.get("lon")
            else:
                center = el.get("center", {})
                elat, elon = center.get("lat"), center.get("lon")
            if not elat or not elon:
                continue
            name = tags.get("name") or tags.get("name:en") or tags.get("amenity", "Unknown")
            dist = geodesic((lat, lon), (elat, elon)).km
            results.append({
                "name": name,
                "lat": elat,
                "lon": elon,
                "dist_km": round(dist, 2),
                "amenity": tags.get("amenity", tags.get("healthcare", "—")),
                "phone": tags.get("phone") or tags.get("contact:phone") or "—",
                "opening_hours": tags.get("opening_hours", "—"),
                "addr": ", ".join(filter(None, [
                    tags.get("addr:housenumber", ""),
                    tags.get("addr:street", ""),
                    tags.get("addr:city", ""),
                ])) or "—",
                "website": tags.get("website") or tags.get("contact:website") or "",
                "speciality": tags.get("healthcare:speciality", tags.get("medical_system", "")),
            })
        results.sort(key=lambda x: x["dist_km"])
        return results[:max_results]
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

# ── Main Search ───────────────────────────────────────────────────
if lat and lon:
    search_btn = st.button("🔍 Find Nearby Doctors & Clinics", type="primary", use_container_width=True)

    if search_btn or ("results" in st.session_state and st.session_state.get("last_search") == (lat, lon, radius_km, specialty)):
        if search_btn:
            with st.spinner("🗺️ Searching OpenStreetMap for nearby healthcare..."):
                results = fetch_nearby_doctors(lat, lon, radius_km, specialty, max_results)
            st.session_state["results"] = results
            st.session_state["last_search"] = (lat, lon, radius_km, specialty)
        else:
            results = st.session_state.get("results", [])

        if not results:
            st.warning("No results found. Try increasing radius or changing specialty.")
        else:
            st.success(f"✅ Found **{len(results)}** healthcare locations within {radius_km} km")

            # ── Map ──
            m = folium.Map(location=[lat, lon], zoom_start=14, tiles="CartoDB dark_matter")

            # User location marker
            folium.Marker(
                [lat, lon],
                popup="📍 You are here",
                icon=folium.Icon(color="red", icon="home", prefix="fa"),
                tooltip="Your Location"
            ).add_to(m)

            # Draw radius circle
            folium.Circle(
                [lat, lon],
                radius=radius_km * 1000,
                color="#3b82f6",
                fill=True,
                fill_opacity=0.05,
                tooltip=f"{radius_km} km radius"
            ).add_to(m)

            color_map = {
                "hospital": "red",
                "clinic": "blue",
                "doctors": "green",
                "pharmacy": "purple",
                "dentist": "orange",
            }

            for i, r in enumerate(results):
                color = color_map.get(r["amenity"], "cadetblue")
                gmaps_url = f"https://www.google.com/maps/dir/?api=1&destination={r['lat']},{r['lon']}"
                popup_html = f"""
                <b>{r['name']}</b><br>
                🏥 {r['amenity'].title()}<br>
                📏 {r['dist_km']} km away<br>
                📞 {r['phone']}<br>
                <a href="{gmaps_url}" target="_blank">🗺️ Get Directions</a>
                """
                folium.Marker(
                    [r["lat"], r["lon"]],
                    popup=folium.Popup(popup_html, max_width=250),
                    icon=folium.Icon(color=color, icon="plus", prefix="fa"),
                    tooltip=f"{i+1}. {r['name']} ({r['dist_km']} km)"
                ).add_to(m)

            st_folium(m, width="100%", height=480)

            # ── Result Cards ──
            st.subheader(f"📋 Results — sorted by distance")
            for i, r in enumerate(results):
                gmaps_url = f"https://www.google.com/maps/dir/?api=1&destination={r['lat']},{r['lon']}"
                gmaps_search = f"https://www.google.com/maps/search/{urllib.parse.quote(r['name'])}/@{r['lat']},{r['lon']},17z"

                with st.container():
                    st.markdown(f"""
<div class="doctor-card">
  <b style="font-size:16px">#{i+1} &nbsp; {r['name']}</b> &nbsp;
  <span class="dist-badge">📏 {r['dist_km']} km</span> &nbsp;
  <span style="color:#94a3b8; font-size:13px">🏥 {r['amenity'].title()}</span>
  {"<br><span style='color:#a78bfa; font-size:13px'>🩺 " + r['speciality'] + "</span>" if r['speciality'] else ""}
  <br><br>
  {"📞 <b>" + r['phone'] + "</b> &nbsp;&nbsp;" if r['phone'] != '—' else ""}
  {"🕐 " + r['opening_hours'] + " &nbsp;&nbsp;" if r['opening_hours'] != '—' else ""}
  {"📍 " + r['addr'] if r['addr'] != '—' else ""}
</div>
""", unsafe_allow_html=True)

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.link_button("🗺️ Get Directions (Google Maps)", gmaps_url)
                    with c2:
                        st.link_button("🔍 View on Google Maps", gmaps_search)
                    if r["website"]:
                        with c3:
                            st.link_button("🌐 Website", r["website"])

            # ── Export ──
            import pandas as pd
            df = pd.DataFrame(results)[["name", "amenity", "dist_km", "phone", "opening_hours", "addr"]]
            df.columns = ["Name", "Type", "Distance (km)", "Phone", "Hours", "Address"]
            st.download_button(
                "⬇️ Download Results as CSV",
                df.to_csv(index=False),
                file_name="nearby_doctors.csv",
                mime="text/csv"
            )

else:
    st.info("👆 Enter your location above and click **Find Nearby Doctors**")
    st.markdown("""
    ### How it works
    - Uses **OpenStreetMap + Overpass API** — completely free, no API key needed
    - Searches real hospitals, clinics, pharmacies around you
    - Shows interactive map with **one-click directions** to any doctor
    - Works anywhere in India (and worldwide)
    """)