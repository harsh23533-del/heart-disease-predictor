import streamlit as st
import streamlit.components.v1 as components
import requests
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import urllib.parse

st.set_page_config(page_title="Doctor Finder", page_icon="🏥", layout="wide")

st.markdown("""
<style>
.doctor-card {
    background: #1a1a2e;
    border: 1px solid #16213e;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
}
.dist-badge { background: #1e3a5f; color: #60a5fa; padding: 2px 10px; border-radius: 20px; font-size: 12px; }
.addr-box { background: #0f172a; border-left: 3px solid #3b82f6; padding: 8px 12px; border-radius: 6px; margin-top: 8px; font-size: 13px; color: #94a3b8; }
.my-location-box {
    background: #0f2027;
    border: 2px solid #22c55e;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏥 Doctor Finder — Live Nearby Search")
st.caption("Real GPS location + exact addresses + Google Maps navigation")

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

# ── Read GPS from URL params → session_state ──────────────────────
params = st.query_params
if params.get("gps_lat") and params.get("gps_lon"):
    try:
        st.session_state["gps_lat"] = float(params["gps_lat"])
        st.session_state["gps_lon"] = float(params["gps_lon"])
        st.query_params.clear()
    except:
        pass

lat, lon = None, None
location_source = ""
current_address = ""

# ── GPS HTML Component ─────────────────────────────────────────────
GPS_HTML = """
<div style="font-family:sans-serif;">
  <button onclick="getLocation()" style="
      background:linear-gradient(135deg,#1d4ed8,#2563eb);
      color:white; border:none; padding:12px 24px;
      border-radius:10px; font-size:15px; font-weight:600;
      cursor:pointer; width:100%; box-shadow:0 4px 15px rgba(37,99,235,0.4);">
    📍 Use My Current GPS Location
  </button>
  <p id="status" style="color:#94a3b8; margin-top:10px; font-size:13px; text-align:center;"></p>
</div>
<script>
function getLocation() {
  var status = document.getElementById("status");
  status.innerText = "⏳ Requesting GPS permission...";
  status.style.color = "#facc15";
  if (!navigator.geolocation) {
    status.innerText = "❌ Geolocation not supported by your browser.";
    status.style.color = "#f87171"; return;
  }
  navigator.geolocation.getCurrentPosition(
    function(pos) {
      var lat = pos.coords.latitude.toFixed(6);
      var lon = pos.coords.longitude.toFixed(6);
      status.innerText = "✅ Location found! Loading...";
      status.style.color = "#4ade80";
      var base = window.parent.location.href.split('?')[0];
      window.parent.location.href = base + "?gps_lat=" + lat + "&gps_lon=" + lon;
    },
    function(err) {
      var msgs = {1:"❌ Permission denied — allow location in browser settings.",
                  2:"❌ Position unavailable. Try manual entry.",
                  3:"❌ Timed out. Try again."};
      status.innerText = msgs[err.code] || "❌ Error.";
      status.style.color = "#f87171";
    },
    { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
  );
}
</script>
"""

# ── Photon Reverse Geocode (faster, no rate limit) ────────────────
@st.cache_data(ttl=3600)
def get_exact_address(lat, lon):
    """Photon geocoder — fast, free, no API key, no rate limit"""
    try:
        r = requests.get(
            f"https://photon.komoot.io/reverse?lat={lat}&lon={lon}&limit=1",
            timeout=6
        )
        if r.status_code == 200:
            props = r.json()["features"][0]["properties"]
            parts = []
            for k in ["housenumber", "street", "suburb", "city", "state", "country"]:
                v = props.get(k, "")
                if v:
                    parts.append(str(v))
            if parts:
                return ", ".join(parts)
    except:
        pass
    # Fallback to Nominatim if Photon fails
    try:
        from geopy.geocoders import Nominatim
        geo = Nominatim(user_agent="healthcare_ai_harsh_v4")
        rev = geo.reverse((lat, lon), language="en", timeout=8, zoom=18)
        if rev:
            return rev.address
    except:
        pass
    return f"{lat}, {lon}"

# ── Photon Forward Geocode ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def geocode_address(address_input):
    """Forward geocode using Photon — fast & free"""
    try:
        r = requests.get(
            f"https://photon.komoot.io/api/?q={urllib.parse.quote(address_input + ' India')}&limit=1",
            timeout=6
        )
        if r.status_code == 200:
            features = r.json().get("features", [])
            if features:
                props = features[0]["properties"]
                coords = features[0]["geometry"]["coordinates"]
                lon, lat = coords[0], coords[1]
                parts = []
                for k in ["name", "street", "city", "state", "country"]:
                    v = props.get(k, "")
                    if v:
                        parts.append(str(v))
                address = ", ".join(parts) if parts else f"{lat}, {lon}"
                return lat, lon, address
    except:
        pass
    # Fallback to Nominatim
    try:
        from geopy.geocoders import Nominatim
        geo = Nominatim(user_agent="healthcare_ai_harsh_v4")
        loc = geo.geocode(address_input + ", India", timeout=8)
        if loc:
            return loc.latitude, loc.longitude, loc.address
    except:
        pass
    return None, None, None

# ── OSM tags only — no reverse geocode per doctor ─────────────────
def get_place_address(tags):
    """Build address from OSM tags only — no API call"""
    parts = []
    for k in ["addr:housenumber", "addr:street", "addr:subdistrict", "addr:city", "addr:state"]:
        v = tags.get(k, "")
        if v:
            parts.append(v)
    if parts:
        return ", ".join(parts)
    return "Address not available"

# ── Location Tabs ──────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📍 GPS (Auto)", "🏙️ City / Address", "🔢 Manual Coordinates"])

with tab1:
    if "gps_lat" in st.session_state and "gps_lon" in st.session_state:
        lat = st.session_state["gps_lat"]
        lon = st.session_state["gps_lon"]
        location_source = "GPS"
        current_address = get_exact_address(lat, lon)
        st.markdown(f"""
        <div class="my-location-box">
            <b style="color:#22c55e">✅ Your Current Location (GPS)</b><br>
            <span style="color:#f8fafc; font-size:15px">📍 {current_address}</span><br>
            <span style="color:#64748b; font-size:12px">Coordinates: {lat}, {lon}</span>
        </div>
        """, unsafe_allow_html=True)
        gmaps_me = f"https://www.google.com/maps?q={lat},{lon}"
        st.link_button("🗺️ View My Location on Google Maps", gmaps_me)
        if st.button("🔄 Refresh / Change Location"):
            del st.session_state["gps_lat"]
            del st.session_state["gps_lon"]
            st.rerun()
    else:
        st.markdown("Allow location permission — browser will ask once you click:")
        components.html(GPS_HTML, height=110)
        st.info("💡 After clicking, browser will ask for location permission. Allow it and page will auto-reload.")

with tab2:
    address_input = st.text_input("Enter area / locality / city",
        placeholder="e.g. Alambagh Lucknow | Sultanpur UP | Varanasi")
    if address_input:
        with st.spinner("📡 Finding location..."):
            lat, lon, found_address = geocode_address(address_input)
            if lat and lon:
                location_source = "Address"
                current_address = found_address
                st.markdown(f"""
                <div class="my-location-box">
                    <b style="color:#22c55e">✅ Location Found</b><br>
                    <span style="color:#f8fafc">📍 {found_address[:120]}</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.error("Not found — try adding city name e.g. 'Alambagh, Lucknow'")

with tab3:
    st.caption("Open Google Maps → long-press your location → copy coordinates")
    c1, c2 = st.columns(2)
    with c1:
        manual_lat = st.number_input("Latitude", value=0.0, format="%.6f", step=0.0001)
    with c2:
        manual_lon = st.number_input("Longitude", value=0.0, format="%.6f", step=0.0001)
    if manual_lat != 0.0 and manual_lon != 0.0:
        lat = manual_lat
        lon = manual_lon
        location_source = "Manual"
        current_address = get_exact_address(lat, lon)
        st.success(f"📍 {current_address[:100]}")

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

@st.cache_data(ttl=600)
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
        # OSM tags only — no reverse geocode per doctor
        exact_addr = get_place_address(tags)
        results.append({
            "name": name,
            "lat": elat, "lon": elon,
            "dist_km": round(dist, 2),
            "amenity": tags.get("amenity", tags.get("healthcare", "clinic")),
            "phone": tags.get("phone") or tags.get("contact:phone") or "—",
            "opening_hours": tags.get("opening_hours", "—"),
            "address": exact_addr,
            "website": tags.get("website") or tags.get("contact:website") or "",
            "speciality": tags.get("healthcare:speciality", ""),
        })
    results.sort(key=lambda x: x["dist_km"])
    return results[:max_results]

# ── Search ─────────────────────────────────────────────────────────
st.markdown("---")

if lat and lon:
    st.info(f"📍 **{location_source}** → {current_address[:80]}...")
    search_btn = st.button("🔍 Find Nearby Doctors & Clinics", type="primary", use_container_width=True)

    cache_key = (round(lat, 3), round(lon, 3), radius_km, specialty)

    if search_btn:
        with st.spinner("🗺️ Searching nearby doctors..."):
            results = fetch_doctors(round(lat, 3), round(lon, 3), radius_km, specialty, max_results)
        st.session_state["results"] = results
        st.session_state["last_search"] = cache_key
    elif st.session_state.get("last_search") == cache_key:
        results = st.session_state.get("results", [])
    else:
        results = []

    if results:
        st.success(f"✅ Found **{len(results)}** healthcare locations within {radius_km} km")

        # ── Map ──────────────────────────────────────────────────
        m = folium.Map(location=[lat, lon], zoom_start=14, tiles="CartoDB dark_matter")

        folium.Marker(
            [lat, lon],
            popup=folium.Popup(f"<b>📍 You are here</b><br>{current_address[:80]}", max_width=250),
            icon=folium.Icon(color="red", icon="home", prefix="fa"),
            tooltip="📍 Your Location"
        ).add_to(m)

        folium.Circle([lat, lon], radius=radius_km * 1000,
                      color="#3b82f6", fill=True, fill_opacity=0.05).add_to(m)

        color_map = {"hospital": "red", "clinic": "blue", "doctors": "green",
                     "pharmacy": "purple", "dentist": "orange"}

        for i, r in enumerate(results):
            color = color_map.get(r["amenity"], "cadetblue")
            gmaps_nav = (f"https://www.google.com/maps/dir/?api=1"
                         f"&origin={lat},{lon}"
                         f"&destination={r['lat']},{r['lon']}"
                         f"&travelmode=driving")
            popup_html = (
                f"<b style='font-size:14px'>{r['name']}</b><br>"
                f"🏥 {r['amenity'].title()}<br>"
                f"📏 {r['dist_km']} km away<br>"
                f"📍 {r['address'][:80]}<br>"
                f"📞 {r['phone']}<br><br>"
                f"<a href='{gmaps_nav}' target='_blank' style='background:#2563eb;color:white;"
                f"padding:5px 10px;border-radius:5px;text-decoration:none;font-weight:bold'>"
                f"🗺️ Get Directions</a>"
            )
            folium.Marker(
                [r["lat"], r["lon"]],
                popup=folium.Popup(popup_html, max_width=280),
                icon=folium.Icon(color=color, icon="plus", prefix="fa"),
                tooltip=f"{i+1}. {r['name']} ({r['dist_km']} km)"
            ).add_to(m)

        st_folium(m, width="100%", height=520)

        # ── Result Cards ─────────────────────────────────────────
        st.subheader("📋 Nearby Doctors — sorted by distance")

        for i, r in enumerate(results):
            gmaps_nav = (f"https://www.google.com/maps/dir/?api=1"
                         f"&origin={lat},{lon}"
                         f"&destination={r['lat']},{r['lon']}"
                         f"&travelmode=driving")
            gmaps_place = (f"https://www.google.com/maps/search/"
                           f"{urllib.parse.quote(r['name'])}"
                           f"/@{r['lat']},{r['lon']},17z")
            gmaps_street = f"https://www.google.com/maps?q={r['lat']},{r['lon']}"

            st.markdown(f"""
<div class="doctor-card">
  <b style="font-size:17px">#{i+1} &nbsp; {r['name']}</b> &nbsp;
  <span class="dist-badge">📏 {r['dist_km']} km</span> &nbsp;
  <span style="color:#94a3b8; font-size:13px">🏥 {r['amenity'].title()}</span>
  {"<br><span style='color:#a78bfa;font-size:13px'>🩺 "+r['speciality']+"</span>" if r['speciality'] else ""}
  <div class="addr-box">
    📍 {r['address']}
  </div>
  <br>
  {"📞 <b style='color:#4ade80'>"+r['phone']+"</b>&nbsp;&nbsp;" if r['phone']!='—' else ""}
  {"🕐 <span style='color:#fbbf24'>"+r['opening_hours']+"</span>" if r['opening_hours']!='—' else ""}
</div>""", unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.link_button("🚗 Directions", gmaps_nav, use_container_width=True)
            c2.link_button("📍 View on Maps", gmaps_street, use_container_width=True)
            c3.link_button("🔍 Search Place", gmaps_place, use_container_width=True)
            if r["website"]:
                c4.link_button("🌐 Website", r["website"], use_container_width=True)
            st.markdown("")

        # ── CSV Export ───────────────────────────────────────────
        import pandas as pd
        df = pd.DataFrame(results)[["name","amenity","dist_km","phone","opening_hours","address"]]
        df.columns = ["Name","Type","Distance (km)","Phone","Hours","Address"]
        st.download_button("⬇️ Download CSV", df.to_csv(index=False),
                           "nearby_doctors.csv", "text/csv")

    elif search_btn:
        st.warning("⚠️ No results found. Try increasing search radius or select 'All'.")

else:
    st.markdown("""
    <div style="text-align:center; padding:50px; color:#64748b;">
        <h2>👆 Set your location above to begin</h2>
        <p style="font-size:16px">GPS tab → Click button → Allow browser permission<br>
        OR type your area name in City/Address tab</p>
    </div>
    """, unsafe_allow_html=True)