# dashboard.py
import streamlit as st
from math import floor, ceil, isfinite

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
        row_spacing = col3.number_input("↔️ Row Spacing (between rows)", min_value=0.01, step=0.1, format="%.2f")
        plant_spacing = col4.number_input("↕️ Plant Spacing (between plants)", min_value=0.01, step=0.1, format="%.2f")
        land_acres = col5.number_input("🌾 Farm Area (acres)", min_value=0.01, step=0.1, format="%.2f")

        # FIX: Reverted mortality slider range and label
        mortality = st.slider("Missing plants (number)", min_value=0, max_value=5000, value=0, step=10) # Changed max to 5000 and type to int

        seed_type = st.radio(
            "🌱 Select Seed Type",
            ('Organic, Non-GMO, Hybrid', 'OPV (Breeder Seed)')
        )

        submitted = st.form_submit_button("🔍 Calculate")

if submitted and farmer_name and farmer_id:
    # Input validation for spacing and land area to prevent ZeroDivisionError or infinite values
    if row_spacing <= 0 or plant_spacing <= 0 or land_acres <= 0:
        st.error("⚠️ Row spacing, plant spacing, and farm area must be greater than zero.")
    else:
        st.markdown("---")

        # Constants
        germination_rate_per_acre = {"Maharashtra": 14000, "Gujarat": 7400}
        confidence_interval = 0.89 # This can be thought of as germination success rate
        acre_to_m2 = 4046.86

        SEEDS_PER_PACKET_ORGANIC_HYBRID = 4000
        SEEDS_PER_PACKET_OPV = 22300

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
        
        if confidence_interval == 0:
            st.error("⚠️ Confidence interval cannot be zero for calculations.")
            st.stop()

        required_seeds = target_plants / confidence_interval
        required_packets = floor(required_seeds / seeds_per_packet)

        # FIX START: Adjusted how mortality (missing plants) affects expected_plants
        # Expected plants from initial sowing, considering germination success (confidence_interval)
        expected_plants_before_mortality = total_plants * confidence_interval
        
        # Now, subtract the explicit 'missing plants' from this expected number
        # Ensure expected plants don't go below zero
        expected_plants = max(0, expected_plants_before_mortality - mortality)

        # If effective germination rate for gap filling is needed, it's just the confidence_interval
        # because the 'mortality' is already accounted for as a fixed number of missing plants.
        effective_germination_for_gap_fill = confidence_interval 
        
        # Corrected gaps calculation: Shortfall to reach target, considering what survived (expected_plants)
        gaps = max(0, target_plants - expected_plants)
        # Ensure gaps don't exceed the total possible plants in the field.
        gaps = min(gaps, total_plants) 

        # Handle case where effective_germination_for_gap_fill might be zero or near-zero
        if effective_germination_for_gap_fill <= 0:
            st.warning("⚠️ Effective germination rate for gap filling is zero or negative. Gap filling seeds cannot be calculated accurately.")
            gap_seeds = float('inf') # Needs infinite seeds
            gap_packets = float('inf') # Needs infinite packets
        else:
            gap_seeds = ceil(gaps / effective_germination_for_gap_fill)
            gap_packets = ceil(gap_seeds / seeds_per_packet)
        # FIX END

        display_gap_seeds = f"{int(gap_seeds):,} seeds" if isfinite(gap_seeds) else "N/A (Infinite)"
        display_gap_packets = f"{gap_packets} packets" if isfinite(gap_packets) else "N/A (Infinite)"


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
        col11.metric("💼 Seeds for Gaps", display_gap_seeds)
        col12.metric("📦 Packets for Gap Filling", display_gap_packets)

        st.caption(f"ℹ️ Based on {packet_info} and accounting for germination confidence and actual missing plants.")

elif submitted:
    st.error("⚠️ Please enter both Farmer Name and Farmer ID to proceed.")
