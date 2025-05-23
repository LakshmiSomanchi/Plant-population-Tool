# dashboard.py
import streamlit as st
from math import ceil

st.set_page_config(page_title="Plant Population & Seed Requirement", layout="centered")
st.title("🌿 Plant Population & Seed Requirement Calculator")
st.markdown("---")

st.subheader("📥 Input Parameters")

state = st.selectbox("State", ["Maharashtra", "Gujarat"])
spacing_unit = st.selectbox("Spacing Unit", ["cm", "m"])
row_spacing = st.number_input("Row Spacing (between rows)", min_value=0.01, step=0.1)
plant_spacing = st.number_input("Plant Spacing (between plants)", min_value=0.01, step=0.1)
land_acres = st.number_input("Farm Area (acres)", min_value=0.01, step=0.1)

calculate = st.button("🔍 Calculate")

if calculate:
    st.markdown("---")

    # Constants
    germination_rate_per_acre = {"Maharashtra": 14000, "Gujarat": 7400}  # plants/acre
    confidence_interval = 0.90
    seeds_per_packet = 7000
    acre_to_m2 = 4046.86

    # Convert spacing to meters if needed
    if spacing_unit == "cm":
        row_spacing /= 100
        plant_spacing /= 100

    # Calculate total plants by land area and spacing
    plant_area_m2 = row_spacing * plant_spacing
    plants_per_m2 = 1 / plant_area_m2
    field_area_m2 = land_acres * acre_to_m2
    calculated_plants = plants_per_m2 * field_area_m2

    # Required seeds considering germination rate
    target_plants = germination_rate_per_acre[state] * land_acres
    required_seeds = target_plants / confidence_interval
    required_packets = ceil(required_seeds / seeds_per_packet)

    st.subheader("📊 Output")
    st.metric("Calculated Plant Capacity (based on spacing)", f"{int(calculated_plants):,} plants")
    st.metric("Target Plants (per germination rate)", f"{int(target_plants):,} plants")
    st.metric("Required Seeds (with 90% confidence)", f"{int(required_seeds):,} seeds")
    st.metric("Seed Packets Needed", f"{required_packets} packets")

    st.caption("⚙️ Based on 7000 seeds per 450g packet and 85% germination confidence.")
