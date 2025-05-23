# dashboard.py
import streamlit as st
import pandas as pd
from math import ceil

st.set_page_config(page_title="Seed Packet Calculator", layout="centered")
st.title("🌾 Plant Population & Seed Packet Tool")
st.markdown("---")

st.subheader("🌱 Input Parameters")

location = st.selectbox("State/Location", ["Maharashtra", "Gujarat"])
spacing_unit = st.selectbox("Spacing Unit", ["cm", "m"])
row_spacing = st.number_input("Row spacing (between rows)", min_value=0.0, step=0.1)
plant_spacing = st.number_input("Plant spacing (between plants)", min_value=0.0, step=0.1)
land_acres = st.number_input("Farm Area (acres)", min_value=0.0, step=0.1)

st.markdown("---")
st.subheader("📊 Output Calculations")

# Predefined values
germination_rates = {"Maharashtra": 14000, "Gujarat": 7400}  # plants per acre
seeds_per_packet = 7000
confidence_interval = 0.85

# Convert spacing to meters if needed
if spacing_unit == "cm":
    row_spacing /= 100
    plant_spacing /= 100

# Area per plant and total plants
area_per_plant_m2 = row_spacing * plant_spacing
plants_per_m2 = 1 / area_per_plant_m2 if area_per_plant_m2 > 0 else 0
acre_to_m2 = 4046.86

# Total plants based on spacing and land
total_m2 = land_acres * acre_to_m2
estimated_plants = total_m2 * plants_per_m2

# Adjusted for germination confidence
germination_target = germination_rates[location] * land_acres
required_seeds = germination_target / confidence_interval
required_packets = ceil(required_seeds / seeds_per_packet)

# Display
st.metric("Target Germination", f"{germination_target:.0f} plants")
st.metric("Estimated Plant Capacity", f"{estimated_plants:.0f} plants")
st.metric("Seed Packets Required", f"{required_packets} packets")

st.markdown("---")
st.caption("Based on standard seed packets of 7000 seeds and 85% germination confidence.")
