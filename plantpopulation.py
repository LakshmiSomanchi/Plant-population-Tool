# plantpopulation_final_no_deps.py

import streamlit as st
import pandas as pd
import io
from math import floor, ceil, isfinite

# --- Geolocation Handling (No Dependencies) ---

# 1. Initialize session_state to hold the coordinates. This makes sure they are not lost.
if "latitude" not in st.session_state:
    st.session_state.latitude = None
if "longitude" not in st.session_state:
    st.session_state.longitude = None

# 2. On every page run, check if coordinates have been passed back in the URL.
params = st.query_params
if "lat" in params and "lon" in params:
    # If they exist, save them to the session state.
    st.session_state.latitude = params["lat"]
    st.session_state.longitude = params["lon"]
    # Clear the coordinates from the URL to keep it clean.
    st.query_params.clear()

# 3. This is the JavaScript that will be run in the user's browser.
# It gets the location and triggers a page reload with the coordinates in the URL.
js_code = """
<script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                // Success callback
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const url = new URL(window.location.href);
                    url.searchParams.set('lat', lat);
                    url.searchParams.set('lon', lon);
                    window.location.href = url.href; // Reload the page with new URL
                },
                // Error callback
                function(error) {
                    alert("Error getting location: " + error.message);
                }
            );
        } else {
            alert("Geolocation is not supported by your browser.");
        }
    }
    // Automatically call the function
    getLocation();
</script>
"""

# --- App Styling and Layout ---

st.set_page_config(page_title="Plant Population Tool", layout="wide")

is_dark = st.get_option("theme.base") == "dark"
text_color = "#f8f9fa" if is_dark else "#0A0A0A"
bg_color = "#0A9396" if is_dark else "#e0f2f1"
st.markdown(f"""
<style>
    html, body, [class*="css"] {{ background-color: {bg_color}; font-family: 'Helvetica', sans-serif; }}
    .block-container {{ padding-top: 3rem; padding-bottom: 3rem; }}
    .stMetricValue {{ font-size: 1.5rem !important; color: {text_color}; }}
    .stMetricLabel {{ font-weight: bold; color: {text_color}; }}
    h1, h2, h3, h4, h5 {{ color: {text_color}; }}
    .stButton>button {{ background-color: #0A9396; color: white; font-weight: bold; border-radius: 5px; padding: 0.6em 1.5em; }}
    .stButton>button:hover {{ background-color: #007f86; }}
</style>
""", unsafe_allow_html=True)

st.title("🌿 Plant Population & Seed Requirement Tool")
st.markdown("""<hr style='margin-top: -15px; margin-bottom: 25px;'>""", unsafe_allow_html=True)

with st.container():
    st.header("📅 Farmer Data Entry")
    st.markdown("Click the button to record the current location for this data entry.")

    # 4. The button that triggers the geolocation JavaScript.
    if st.button("📍 Get Current Location"):
        # This injects the JavaScript into the page, which then runs automatically.
        st.components.v1.html(js_code, height=0)

    # 5. Display the captured location from session state.
    if st.session_state.latitude and st.session_state.longitude:
        st.success(f"📍 Location Captured: Latitude {st.session_state.latitude}, Longitude {st.session_state.longitude}")
    else:
        st.info("Click the button above to capture GPS coordinates.")

    with st.form("survey_form"):
        col0, col1, col2 = st.columns(3)
        farmer_name = col0.text_input("👤 Farmer Name")
        farmer_id = col1.text_input("🆔 Farmer ID")
        state = col2.selectbox("🗽 State", ["Maharashtra", "Gujarat"])

        st.subheader("🌱 Farm and Seed Details")
        spacing_unit = st.selectbox("📏 Spacing Unit", ["cm", "m"])
        col3, col4, col5 = st.columns(3)
        row_spacing = col3.number_input("↔️ Row Spacing", min_value=0.01, step=0.1, format="%.2f")
        plant_spacing = col4.number_input("↕️ Plant Spacing", min_value=0.01, step=0.1, format="%.2f")
        land_acres = col5.number_input("🌾 Farm Area (acres)", min_value=0.01, step=0.1, format="%.2f")
        mortality = st.slider("Missing plants (number)", 0, 5000, 0, 10)
        seed_type = st.radio("🌱 Select Seed Type", ('Organic, Non-GMO, Hybrid', 'OPV (Breeder Seed)'))
        submitted = st.form_submit_button("🔍 Calculate")

if submitted and farmer_name and farmer_id:
    if row_spacing <= 0 or plant_spacing <= 0 or land_acres <= 0:
        st.error("⚠️ Row spacing, plant spacing, and farm area must be greater than zero.")
    else:
        st.markdown("---")
        # --- Calculations (Unchanged) ---
        germination_rate = 0.75
        fixed_target_plants_per_acre = {"Maharashtra": 14000, "Gujarat": 7400}
        acre_to_m2 = 4046.86
        seeds_per_packet = 4000 if seed_type == 'Organic, Non-GMO, Hybrid' else 22300
        packet_info = "1 packet of 450gm (~4000 seeds)" if seeds_per_packet == 4000 else "1 packet of 2.5kg (~22300 seeds)"
        if spacing_unit == "cm":
            row_spacing /= 100
            plant_spacing /= 100
        plant_area_m2 = row_spacing * plant_spacing
        plants_per_m2 = 1 / plant_area_m2 if plant_area_m2 > 0 else 0
        total_plants = plants_per_m2 * (land_acres * acre_to_m2)
        target_plants = fixed_target_plants_per_acre[state] * land_acres
        required_seeds = target_plants / germination_rate if germination_rate > 0 else float('inf')
        required_packets = floor(required_seeds / seeds_per_packet)
        initial_gaps = total_plants - (total_plants * germination_rate)
        total_gaps_to_fill = min(total_plants, max(0, initial_gaps + mortality))
        gap_seeds = ceil(total_gaps_to_fill / germination_rate) if germination_rate > 0 else float('inf')
        gap_packets = ceil(gap_seeds / seeds_per_packet) if germination_rate > 0 else float('inf')
        display_gap_seeds = f"{int(gap_seeds):,} seeds" if isfinite(gap_seeds) else "N/A"
        display_gap_packets = f"{int(gap_packets)} packets" if isfinite(gap_packets) else "N/A"

        # --- Output Display (Unchanged) ---
        st.subheader("📊 Output Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🧬 Calculated Capacity", f"{int(total_plants):,} plants")
        c2.metric("🎯 Target Plants", f"{int(target_plants):,} plants")
        c3.metric("🌱 Required Seeds", f"{int(required_seeds):,} seeds")
        c4.metric("📦 Seed Packets Needed", f"{required_packets} packets")
        st.markdown("""<hr style='margin-top: 25px;'>""", unsafe_allow_html=True)
        st.subheader("📊 Gap Filling Summary")
        c10, c11, c12 = st.columns(3)
        c10.metric("❓ Gaps (missing plants)", f"{int(total_gaps_to_fill):,}")
        c11.metric("💼 Seeds for Gaps", display_gap_seeds)
        c12.metric("📦 Packets for Gap Filling", display_gap_packets)
        st.caption(f"ℹ️ Based on {packet_info} & {int(germination_rate*100)}% germination.")

        # --- CSV Download Section (Now includes latitude and longitude) ---
        result_data = {
            "Farmer Name": [farmer_name], "Farmer ID": [farmer_id], "State": [state],
            "Latitude": [st.session_state.latitude], "Longitude": [st.session_state.longitude],
            "Spacing Unit": [spacing_unit],
            "Row Spacing": [row_spacing * (100 if spacing_unit == "m" else 1)],
            "Plant Spacing": [plant_spacing * (100 if spacing_unit == "m" else 1)],
            "Land Acres": [land_acres], "Seed Type": [seed_type],
            "Calculated Capacity": [int(total_plants)], "Target Plants": [int(target_plants)],
            "Required Seeds": [int(required_seeds) if isfinite(required_seeds) else None],
            "Seed Packets Needed": [int(required_packets) if isfinite(required_packets) else None],
            "Gaps (Missing Plants)": [int(total_gaps_to_fill)],
            "Seeds for Gaps": [int(gap_seeds) if isfinite(gap_seeds) else None],
            "Packets for Gap Filling": [int(gap_packets) if isfinite(gap_packets) else None],
        }
        df = pd.DataFrame(result_data)
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv_bytes,
            file_name=f"{farmer_name}_plant_population_results.csv",
            mime="text/csv",
        )

elif submitted:
    st.error("⚠️ Please enter both Farmer Name and Farmer ID to proceed.")
