# dashboard.py
import streamlit as st
from math import floor

st.set_page_config(page_title="Plant Population Tool", layout="wide")
st.title("🌿 Plant Population & Seed Requirement Tool")
st.markdown("---")

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stMetric { text-align: center; }
</style>
""", unsafe_allow_html=True)

with st.container():
    st.header("📥 Farmer Survey Entry")
    col0, col1, col2 = st.columns(3)
    farmer_name = col0.text_input("Farmer Name")
    farmer_id = col1.text_input("Farmer ID")
    state = col2.selectbox("State", ["Maharashtra", "Gujarat"])

    spacing_unit = st.selectbox("Spacing Unit", ["cm", "m"])
    col3, col4, col5 = st.columns(3)
    row_spacing = col3.number_input("Row Spacing (between rows)", min_value=0.01, step=0.1)
    plant_spacing = col4.number_input("Plant Spacing (between plants)", min_value=0.01, step=0.1)
    land_acres = col5.number_input("Farm Area (acres)", min_value=0.01, step=0.1)

    calculate = st.button("🔍 Calculate")

if calculate and farmer_name and farmer_id:
    st.markdown("---")

    # Constants
    germination_rate_per_acre = {"Maharashtra": 14000, "Gujarat": 7400}  # plants/acre
    confidence_interval = 0.90
    seeds_per_packet = 7500
    acre_to_m2 = 4046.86

    # Convert spacing to meters if needed
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
    col6, col7, col8, col9 = st.columns(4)
    col6.metric("Calculated Capacity", f"{int(calculated_plants):,} plants")
    col7.metric("Target Plants", f"{int(target_plants):,} plants")
    col8.metric("Required Seeds (90% confidence)", f"{int(required_seeds):,} seeds")
    col9.metric("Seed Packets Needed", f"{required_packets} packets")

    st.caption("⚙️ Based on 7500 seeds per 450g packet and 90% germination confidence. Packets are rounded down to the nearest full packet.")

elif calculate:
    st.error("⚠️ Please enter both Farmer Name and Farmer ID to proceed.")
