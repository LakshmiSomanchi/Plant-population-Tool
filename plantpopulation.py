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

        mortality = st.slider("Missing plants (number)", min_value=0, max_value=5000, value=0, step=10) 

        seed_type = st.radio(
            "🌱 Select Seed Type",
            ('Organic, Non-GMO, Hybrid', 'OPV (Breeder Seed)')
        )

        submitted = st.form_submit_button("🔍 Calculate")

if submitted and farmer_name and farmer_id:
    if row_spacing <= 0 or plant_spacing <= 0 or land_acres <= 0:
        st.error("⚠️ Row spacing, plant spacing, and farm area must be greater than zero.")
    else:
        st.markdown("---")

        # Constants
        # Note: Using your specified germination rate of 75% (0.75) from the detailed notes
        germination_rate = 0.75 
        
        # Using the specific values from your provided calculations for germination rate per acre
        # Maharashtra: 90x40cm gives ~11,241 spots, then 11,241 / 0.75 = 14,988 seeds. So target is 11,241 plants/acre.
        # Gujarat: 90x60cm gives ~7,494 spots, then 7,494 / 0.75 = 9,992 seeds. So target is 7,494 plants/acre.
        # It seems the 'target plants' in your current output (7,400) is for Gujarat (90x60)
        # and 'Calculated Capacity' (14,988) is for Maharashtra (90x40).
        # To align with your document, let's use the actual calculated 'total_plants' as the base for target
        # rather than fixed germination_rate_per_acre.
        # However, if 'Target Plants' should be a fixed value for the state regardless of spacing,
        # we'd need to explicitly set it. From the screenshot, 'Target Plants' is 7,400.
        # Let's assume the 'Target Plants' metric should reflect the target *population* per acre for the state,
        # irrespective of the specific spacing chosen by the user in the input.
        # If the 'Target Plants' needs to be dynamically derived from the chosen spacing and area, we will adjust.
        # For now, let's stick to the constant values from your previous code which matches the screenshot.
        fixed_target_plants_per_acre = {"Maharashtra": 14000, "Gujarat": 7400} # This seems to be the target *seeds* or *desired population* from prior versions, let's clarify its role.
                                                                                # Based on the screenshot: Target Plants 7,400 matches Gujarat's 90x60 calculation from your document.
                                                                                # Calculated Capacity 14,988 matches Maharashtra's 90x40 calculation from your document.
                                                                                # There might be a slight mismatch in naming or interpretation.
                                                                                # For this fix, let's use the document's logic for *calculated capacity* as the "plant population" base.
        
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
        total_plants = plants_per_m2 * field_area_m2 # This is "Plant Population" from your notes

        # Target plants will be the expected population for the chosen state's typical spacing,
        # or the 'calculated capacity' from the input spacing.
        # Based on your image, 'Target Plants' is 7,400 while 'Calculated Capacity' is 14,988.
        # This implies 'Target Plants' is a fixed goal *per acre* for the state, regardless of specific user spacing.
        # Let's retain the fixed_target_plants_per_acre constant for this.
        target_plants = fixed_target_plants_per_acre[state] * land_acres
        
        if germination_rate <= 0:
            st.error("⚠️ Germination rate cannot be zero or negative for calculations.")
            st.stop()

        # Seeds required for initial sowing (to achieve target_plants given germination_rate)
        required_seeds = target_plants / germination_rate
        required_packets = floor(required_seeds / seeds_per_packet)

        # --- Gap Filling Calculations based on your provided formulas ---
        # Expected plants after initial germination (based on total capacity and germination_rate)
        expected_plants_after_germination = total_plants * germination_rate

        # Initial gaps based on expected loss from total capacity due to germination
        initial_gaps = total_plants - expected_plants_after_germination
        
        # Total gaps to fill includes initial gaps AND the explicitly reported 'mortality' (missing plants)
        # Ensure 'mortality' does not exceed the remaining capacity that can be filled
        total_gaps_to_fill = max(0, initial_gaps + mortality)
        
        # Cap total gaps to the 'total_plants' capacity if it somehow exceeds it
        total_gaps_to_fill = min(total_gaps_to_fill, total_plants) 

        # Seeds needed for gap filling (re-sow based on germination rate)
        # Make sure germination_rate is not zero here
        if germination_rate <= 0:
            gap_seeds = float('inf') # Needs infinite seeds
            gap_packets = float('inf') # Needs infinite packets
        else:
            gap_seeds = ceil(total_gaps_to_fill / germination_rate)
            gap_packets = ceil(gap_seeds / seeds_per_packet)
        # --- End Gap Filling Calculations ---

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
        col10.metric("❓ Gaps (missing plants)", f"{int(total_gaps_to_fill):,}")
        col11.metric("💼 Seeds for Gaps", display_gap_seeds)
        col12.metric("📦 Packets for Gap Filling", display_gap_packets)

        st.caption(f"ℹ️ Based on {packet_info} and accounting for {int(germination_rate*100)}% germination and actual missing plants.")

elif submitted:
    st.error("⚠️ Please enter both Farmer Name and Farmer ID to proceed.")
