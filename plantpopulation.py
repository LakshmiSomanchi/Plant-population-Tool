# dashboard.py
import streamlit as st
from math import floor

st.set_page_config(page_title="Plant Population Tool", layout="wide")

# Page styling
st.markdown("""
<style>
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        font-family: 'Segoe UI', sans-serif;
    }
    .stMetricValue {
        font-size: 1.5rem !important;
        color: #0A9396;
    }
    .stMetricLabel {
        font-weight: bold;
    }
    h1, h2, h3, h4 {
        color: #005f73;
    }
    .stButton>button {
        background-color: #0A9396;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.6em 1.5em;
    }
    .stButton>button:hover {
        background-color: #007f86;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌿 Plant Population & Seed Requirement Tool")
st.markdown("""<hr style='margin-top: -15px; margin-bottom: 25px;'>""", unsafe_allow_html=True)

with st.container():
    st.header("📥 Farmer Survey Entry")
    st.markdown("Fill in the details below to calculate how many seed packets are required for optimal plant population.")

    with st.form("survey_form"):
        col0, col1, col2 = st.columns(3)
        farmer_name = col0.text_input("👤 Farmer Name")
        farmer_id = col1.text_input("🆔 Farmer ID")
        state = col2.selectbox("🗺️ State", ["Maharashtra", "Gujarat"])

        spacing_unit = st.selectbox("📏 Spacing Unit", ["cm", "m"])
        col3, col4, col5 = st.columns(3)
        row_spacing = col3.number_input("↔️ Row Spacing (between rows)", min_value=0.01, step=0.1)
        plant_spacing = col4.number_input("↕️ Plant Spacing (between plants)", min_value=0.01, step=0.1)
        land_acres = col5.number_input("🌾 Farm Area (acres)", min_value=0.01, step=0.1)

        submitted = st.form_submit_button("🔍 Calculate")

if submitted and farmer_name and farmer_id:
    st.markdown("---")

    germination_rate_per_acre = {"Maharashtra": 14000, "Gujarat": 7400}
    confidence_interval = 0.90
    seeds_per_packet = 7500
    acre_to_m2 = 4046.86

    if spacing_unit == "cm":
        row_spacing /= 100
        plant_spacing /= 100

    plant_area_m2 = row_spacing * plant_spacing
    plants_per_m2 = 1 / plant_area_m2
    field_area_m2 = land_acres * acre_to_m2
    calculated_plants = plants_per_m2 * field_area_m2

    target_plants = germination_rate_per_acre[state] * land_acres
    required_seeds = target_plants / confidence_interval
    required_packets = floor(required_seeds / seeds_per_packet)

    st.subheader("📊 Output Summary")
    st.markdown("""<div style='margin-bottom: 20px;'>Calculated results for seed packet distribution:</div>""", unsafe_allow_html=True)
    col6, col7, col8, col9 = st.columns(4)
    col6.metric("🧮 Calculated Capacity", f"{int(calculated_plants):,} plants")
    col7.metric("🎯 Target Plants", f"{int(target_plants):,} plants")
    col8.metric("🌱 Required Seeds", f"{int(required_seeds):,} seeds")
    col9.metric("📦 Seed Packets Needed", f"{required_packets} packets")

    st.markdown("""<hr style='margin-top: 25px;'>""", unsafe_allow_html=True)
    st.caption("ℹ️ Based on 7500 seeds per 450g packet and 90% germination confidence. Packets are rounded down to the nearest full packet.")

elif submitted:
    st.error("⚠️ Please enter both Farmer Name and Farmer ID to proceed.")
