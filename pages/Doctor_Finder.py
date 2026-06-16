import streamlit as st
import streamlit.components.v1 as components
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
.dist-badge { background: #1e3a5f; color: #60a5fa; padding: 2px 10px; border-radius: 20px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🏥 Doctor Finder — Live Nearby Search")
st.caption("Finds real hospitals, clinics & doctors near your current location using OpenStreetMap")

with st.sidebar:
    st.header("🔍 Search Settings")
    specialty = st.selectbox("Specialty / Type", [
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

# ── Read GPS from URL params ───────────────────────────────────────
params = st.query_params
gps_lat = params.get("gps_lat")
gps_lon = params.get("gps_lon")

if gps_lat and gps_lon:
    try:
        st.session_state["gps_lat"] = float(gps_lat)
        st.session_state["gps_lon"] = float(gps_lon)
        # Clear URL params after reading
        st.query_params.clear()
    except:
        pass

lat, lon = None, None
location_source = ""

GPS_HTML = """
<div style="font-family:sans-serif; padding:4px;">
  <button onclick="getLocation()" style="
      background:#2563eb; color:white; border:none;
      padding:10px 24px; border-radius:8px; font-size:15px;
      cursor:pointer; width:100%;">
    📍 Use My Current GPS Location
  </button>
  <p id="status" style="color:#94a3b8; margin-top:8px; font-size:13px;"></p>
</div>
<script>
function getLocation() {
  var status = document.getElementById("status");
  status.innerText = "⏳ Requesting GPS permission...";
  status.style.color = "#facc15";
  if (!navigator.geolocation) {
    status.innerText = "❌ Geolocation not supported.";
    status.style.color = "#f87171";
    return;
  }
  navigator.geolocation.getCurrentPosition(
    function(pos) {
      var lat = pos.coords.latitude.toFixed(6);
      var lon = pos.coords.longitude.toFixed(6);
      status.innerText = "✅ Got location: " + lat + ", " + lon + " — reloading...";
      status.style.color = "#4ade80";
      var url = window.parent.location.href.split('?')[0];
      window.parent.location.href = url + "?gps_lat=" + lat + "&gps_lon=" + lon;
    },
    function(err) {
      var msgs = {1:"❌ Permission denied.",2:"❌ Position unavailable.",3:"❌ Timed out."};
      status.innerText = msgs[err.code] || "❌ Unknown error.";
      status.style.color = "#f87171";
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
  );
}
</script>
"""

tab1, tab2, tab3 = st.tabs(["📍 GPS (Auto)", "🏙️ City / Address", "🔢 Manual Coordinates"])

with tab1:
    if "gps_lat" in st.session_state and "gps_lon" in st.session_state:
        lat = st.session_state["gps_lat"]
        lon = st.session_state["gps_lon"]
        location_source = "GPS"
        st.success(f"✅ GPS location captured: **{lat}, {lon}**")
        try:
            geo = Nominatim(user_agent="healthcare_ai_harsh_v2")
            rev = geo.reverse((lat, lon), language="en", timeout=8)
            if rev:
                st.caption(f"📍 {rev.address[:100]}")
        except:
            pass
        if st.button("🔄 Refresh GPS Location"):
            del st.session_state["gps_lat"]
            del st.session_state["gps_lon"]
            st.rerun()
    else:
        st.markdown("Click the button below — your browser will ask for location permission.")
        components.html(GPS_HTML, height=120)

with tab2:
    address_input = st.text_input(
        "Enter area / locality / city",
        placeholder="e.g.  Alambagh Lucknow  |  Sultanpur UP  |  Varanasi",
    )
    if address_input:
        with st.spinner("📡 Geocoding..."):
            try:
                geo = Nominatim(user_agent="healthcare_ai_harsh_v2")
                loc = geo.geocode(address_input + ", India", timeout=10)
                if loc:
                    lat = loc.latitude
                    lon = loc.longitude
                    location_source = "Address"
                    st.success(f"📍 {loc.address[:90]}")
                else:
                    st.error("Not found — try adding city name")
            except Exception as e:
                st.error(f"Error: {e}")

with tab3:
    st.caption("Open Google Maps, long-press your location to copy coordinates.")
    c1, c2 = st.columns(2)
    with c1:
        manual_lat = st.number_input("Latitude", value=0.0, format="%.6f", step=0.0001)
    with c2:
        manual_lon = st.number_input("Longitude", value=0.0, format="%.6f", step=0.0001)
    if manual_lat != 0.0 and manual_lon != 0.0:
        lat = manual_lat
        lon = manual_lon
        location_source = "Manual"
        st.success(f"📍 Using: {lat}, {lon}")

# ── Overpass Query ─────────────────────────────────────────────────
def build_query(lat, lon, radius_m, specialty):
    amenity_map = {
        "All (Doctors & Clinics)": '["amenity"~"hospital|clinic|doctors|pharmacy"]',
        "Hospital":                '["amenity"="hospital"]',
        "Clinic / General Physician": '["amenity"~"clinic|doctors"]',
        "Pharmacy":                '["amenity"="pharmacy"]',
        "Dentist":                 '["amenity"="dentist"]',
        "Physiotherapy":           '["healthcare"="physiotherapist"]',
        "Eye / Ophthalmology":     '["healthcare"~"optometrist|ophthalmology"]',
    }
    f = amenity_map.get(specialty, '["amenity"~"hospital|clinic|doctors"]')
    return f"""
[out:json][timeout:25];
(
  node{f}(around:{radius_m},{lat},{lon});
  way{f}(around:{radius_m},{lat},{lon});
);
out center tags;
"""

def fetch_doctors(lat, lon, radius_km, specialty, max_results):
    query = build_query(lat, lon, radius_km * 1000, specialty)
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    ]
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = None
    for url in endpoints:
        try:
            r = requests.post(url, data=f"data={requests.utils.quote(query)}",
                              headers=headers, timeout=30)
            if r.status_code == 200:
                resp = r
                break
        except:
            continue

    if not resp:
        st.error("❌ All Overpass API endpoints failed. Try again later.")
        return []

    elements = resp.json().get("elements", [])
    results = []
    for el in elements:
        tags = el.get("tags", {})
        elat = el.get("lat") if el["type"] == "node" else el.get("center", {}).get("lat")
        elon = el.get("lon") if el["type"] == "node" else el.get("center", {}).get("lon")
        if not elat or not elon:
            continue
        name = tags.get("name") or tags.get("name:en") or tags.get("amenity", "Unknown Facility")
        dist = geodesic((lat, lon), (elat, elon)).km
        results.append({
            "name": name,
            "lat": elat, "lon": elon,
            "dist_km": round(dist, 2),
            "amenity": tags.get("amenity", tags.get("healthcare", "clinic")),
            "phone": tags.get("phone") or tags.get("contact:phone") or "—",
            "opening_hours": tags.get("opening_hours", "—"),
            "addr": ", ".join(filter(None, [
                tags.get("addr:housenumber", ""),
                tags.get("addr:street", ""),
                tags.get("addr:city", ""),
            ])) or "—",
            "website": tags.get("website") or tags.get("contact:website") or "",
            "speciality": tags.get("healthcare:speciality", ""),
        })
    results.sort(key=lambda x: x["dist_km"])
    return results[:max_results]

# ── Search ─────────────────────────────────────────────────────────
st.markdown("---")

if lat and lon:
    st.info(f"📍 Location set via **{location_source}** → `{round(lat,5)}, {round(lon,5)}`")
    search_btn = st.button("🔍 Find Nearby Doctors & Clinics", type="primary", use_container_width=True)

    cache_key = (round(lat, 4), round(lon, 4), radius_km, specialty)

    if search_btn:
        with st.spinner("🗺️ Searching OpenStreetMap..."):
            results = fetch_doctors(lat, lon, radius_km, specialty, max_results)
        st.session_state["results"] = results
        st.session_state["last_search"] = cache_key
    elif st.session_state.get("last_search") == cache_key:
        results = st.session_state.get("results", [])
    else:
        results = []

    if results:
        st.success(f"✅ Found **{len(results)}** healthcare locations within {radius_km} km")

        m = folium.Map(location=[lat, lon], zoom_start=14, tiles="CartoDB dark_matter")
        folium.Marker([lat, lon], popup="📍 You are here",
                      icon=folium.Icon(color="red", icon="home", prefix="fa"),
                      tooltip="Your Location").add_to(m)
        folium.Circle([lat, lon], radius=radius_km * 1000,
                      color="#3b82f6", fill=True, fill_opacity=0.05).add_to(m)

        color_map = {"hospital": "red", "clinic": "blue", "doctors": "green",
                     "pharmacy": "purple", "dentist": "orange"}

        for i, r in enumerate(results):
            color = color_map.get(r["amenity"], "cadetblue")
            gmaps_url = f"https://www.google.com/maps/dir/?api=1&destination={r['lat']},{r['lon']}"
            popup_html = (f"<b>{r['name']}</b><br>🏥 {r['amenity'].title()}<br>"
                          f"📏 {r['dist_km']} km away<br>📞 {r['phone']}<br>"
                          f"<a href='{gmaps_url}' target='_blank'>🗺️ Get Directions</a>")
            folium.Marker([r["lat"], r["lon"]],
                          popup=folium.Popup(popup_html, max_width=260),
                          icon=folium.Icon(color=color, icon="plus", prefix="fa"),
                          tooltip=f"{i+1}. {r['name']} ({r['dist_km']} km)").add_to(m)

        st_folium(m, width="100%", height=500)

        st.subheader("📋 Results — sorted by distance")
        for i, r in enumerate(results):
            gmaps_dir = f"https://www.google.com/maps/dir/?api=1&destination={r['lat']},{r['lon']}"
            gmaps_search = f"https://www.google.com/maps/search/{urllib.parse.quote(r['name'])}/@{r['lat']},{r['lon']},17z"
            st.markdown(f"""
<div class="doctor-card">
  <b style="font-size:16px">#{i+1} &nbsp; {r['name']}</b> &nbsp;
  <span class="dist-badge">📏 {r['dist_km']} km</span> &nbsp;
  <span style="color:#94a3b8; font-size:13px">🏥 {r['amenity'].title()}</span>
  {"<br><span style='color:#a78bfa;font-size:13px'>🩺 "+r['speciality']+"</span>" if r['speciality'] else ""}
  <br><br>
  {"📞 <b>"+r['phone']+"</b>&nbsp;&nbsp;" if r['phone']!='—' else ""}
  {"🕐 "+r['opening_hours']+"&nbsp;&nbsp;" if r['opening_hours']!='—' else ""}
  {"📍 "+r['addr'] if r['addr']!='—' else ""}
</div>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.link_button("🗺️ Directions", gmaps_dir)
            c2.link_button("🔍 Google Maps", gmaps_search)
            if r["website"]:
                c3.link_button("🌐 Website", r["website"])

        import pandas as pd
        df = pd.DataFrame(results)[["name","amenity","dist_km","phone","opening_hours","addr"]]
        df.columns = ["Name","Type","Distance (km)","Phone","Hours","Address"]
        st.download_button("⬇️ Download CSV", df.to_csv(index=False),
                           "nearby_doctors.csv", "text/csv")

    elif search_btn:
        st.warning("No results found. Try increasing radius or selecting 'All'.")

else:
    st.markdown("""
    <div style="text-align:center; padding:40px; color:#64748b;">
        <h3>👆 Set your location using one of the tabs above</h3>
        <p>GPS tab → click button → allow browser permission<br>
        OR type your area name in City/Address tab</p>
    </div>
    """, unsafe_allow_html=True)