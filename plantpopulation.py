# dashboard.py
import streamlit as st
from math import floor, ceil

st.set_page_config(page_title="Plant Population Tool", layout="wide")

# Theme detection
is_dark = st.get_option("theme.base") == "dark"
text_color = "#f8f9fa" if is_dark else "#0A0A0A"
bg_color = "#0A9396" if is_dark else "#e0f2f1"

# Styles
st.markdown(f"""
<style>
    html, body, [class*="css"] {{
        background-color: {bg_color};
        font-family: 'Helvetica', sans-serif;
    }}
    .block-container {{
        padding-top: 3rem;
        padding-bottom: 3rem;
    }}
    .stMetricValue {{
        font-size: 1.5rem !important;
        color: {text_color};
    }}
    .stMetricLabel {{
        font-weight: bold;
        color: {text_color};
    }}
    h1, h2, h3, h4, h5 {{
        color: {text_color};
    }}
    .stButton>button {{
        background-color: #0A9396;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.6em 1.5em;
    }}
    .stButton>button:hover {{
        background-color: #007f86;
    }}
</style>
""", unsafe_allow_html=True)

st.title("🌿 Plant Population & Seed Requirement Tool")
st.markdown("""<hr style='margin-top: -15px; margin-bottom: 25px;'>""", unsafe_allow_html=True)

with st.container():
    st.header("📅 Farmer Data Entry")
    st.markdown("Fill in the details below to calculate how many seed packets are required for optimal plant population.")

    with st.form("survey_form"):
        col0, col1, col2 = st.columns(3)
        farmer_name = col0.text_input("👤 Farmer Name")
        farmer_id = col1.text_input("🆔 Farmer ID")
        state = col2.selectbox("🗽 State", ["Maharashtra", "Gujarat"])

        spacing_unit = st.selectbox("📏 Spacing Unit", ["cm", "m"])
        col3, col4, col5 = st.columns(3)
        row_spacing = col3.number_input("↔️ Row Spacing (between rows)", min_value=0.01, step=0.1)
        plant_spacing = col4.number_input("↕️ Plant Spacing (between plants)", min_value=0.01, step=0.1)
        land_acres = col5.number_input("🌾 Farm Area (acres)", min_value=0.01, step=0.1)

        mortality = st.slider("Missing plants", min_value=0.0, max_value=5000.0)
        
        # FIX: Added Seed type selection
        seed_type = st.radio(
            "🌱 Select Seed Type",
            ('Organic, Non-GMO, Hybrid', 'OPV (Breeder Seed)')
        )

        submitted = st.form_submit_button("🔍 Calculate")

if submitted and farmer_name and farmer_id:
    st.markdown("---")

    # Constants
    germination_rate_per_acre = {"Maharashtra": 14000, "Gujarat": 7400}
    confidence_interval = 0.89
    acre_to_m2 = 4046.86

    # FIX: Define seeds per packet based on type
    SEEDS_PER_PACKET_ORGANIC_HYBRID = 4000  # 1 packet seeds of 450 gm contains ~4000 seeds
    SEEDS_PER_PACKET_OPV = 22300          # 1 packet (2.5 kg) for OPV contains ~22300 seeds

    # FIX: Determine seeds_per_packet based on selection
    if seed_type == 'Organic, Non-GMO, Hybrid':
        seeds_per_packet = SEEDS_PER_PACKET_ORGANIC_HYBRID
        packet_info = "1 packet of 450gm (organic, non GMO, Hybrid seeds) containing ~4000 seeds"
    else: # OPV (Breeder Seed)
        seeds_per_packet = SEEDS_PER_PACKET_OPV
        packet_info = "1 packet of 2.5kg (OPV breeder seeds) containing ~22300 seeds"


    # Convert spacing
    if spacing_unit == "cm":
        row_spacing /= 100
        plant_spacing /= 100

    # Calculations
    plant_area_m2 = row_spacing * plant_spacing
    plants_per_m2 = 1 / plant_area_m2
    field_area_m2 = land_acres * acre_to_m2
    total_plants = plants_per_m2 * field_area_m2

    target_plants = germination_rate_per_acre[state] * land_acres
    required_seeds = target_plants / confidence_interval
    required_packets = floor(required_seeds / seeds_per_packet)

    effective_germination = confidence_interval * (1 - mortality / 100)
    expected_plants = total_plants * effective_germination
    gaps = total_plants - expected_plants
    gap_seeds = gaps / effective_germination
    gap_packets = ceil(gap_seeds / seeds_per_packet)

    # Output
    st.subheader("📊 Output Summary")
    col6, col7, col8, col9 = st.columns(4)
    col6.metric("🧬 Calculated Capacity", f"{int(total_plants):,} plants")
    col7.metric("🎯 Target Plants", f"{int(target_plants):,} plants")
    col8.metric("🌱 Required Seeds", f"{int(required_seeds):,} seeds")
    col9.metric("📦 Seed Packets Needed", f"{required_packets} packets")

    st.markdown("""<hr style='margin-top: 25px;'>""", unsafe_allow_html=True)
    st.subheader("📊 Gap Filling Summary")
    col10, col11, col12 = st.columns(3)
    col10.metric("❓ Gaps (missing plants)", f"{int(gaps):,}")
    col11.metric("💼 Seeds for Gaps", f"{int(gap_seeds):,} seeds")
    col12.metric("📦 Packets for Gap Filling", f"{gap_packets} packets")

    # FIX: Updated caption to reflect dynamic seed packet info
    st.caption(f"ℹ️ Based on {packet_info} and accounting for mortality + germination confidence.")

elif submitted:
    st.error("⚠️ Please enter both Farmer Name and Farmer ID to proceed.")
