# dashboard.py
import streamlit as st
import pandas as pd
from datetime import date
import os
import plotly.express as px

st.set_page_config(page_title="Plant Population Dashboard", layout="wide")
st.title("🌱 Plant Population Tool")
st.markdown("---")

excel_file = "plant_population_data.xlsx"

if os.path.exists(excel_file):
    saved_data = pd.read_excel(excel_file)
else:
    saved_data = pd.DataFrame()

st.subheader("Field Input Parameters")

with st.form("plant_population_form"):
    cols1 = st.columns(6)
    farmer_name = cols1[0].text_input("Farmer Name")
    field_id = cols1[1].text_input("Field ID")
    area_acre = cols1[2].number_input("Area (acre)", min_value=0.0, step=0.01)
    area_m = cols1[3].number_input("Area (m)", min_value=0.0, step=0.1)
    spacing_cm = cols1[4].text_input("Row × Plant Spacing (cm)")
    spacing_m = cols1[5].text_input("Row × Plant Spacing (m)")

    cols2 = st.columns(5)
    sowing_date = cols2[0].date_input("Sowing Date", value=date.today())
    expected_plants = cols2[1].number_input("Expected Plants", min_value=0)
    plants_emerged = cols2[2].number_input("Plants Emerged", min_value=0)
    actual_stand = cols2[3].number_input("Actual Stand (%)", min_value=0.0, max_value=100.0, step=0.1)
    missing_plants = cols2[4].number_input("Missing Plants", min_value=0)

    cols3 = st.columns(5)
    gaps_filled = cols3[0].number_input("Gaps filled", min_value=0)
    total_gaps = cols3[1].number_input("Total Gaps", min_value=0)
    gap_percent = cols3[2].number_input("Gap %", min_value=0.0, max_value=100.0, step=0.1)
    gap_filling_date = cols3[3].date_input("Gap Filling Date", value=date.today())
    success_rate = cols3[4].number_input("Success Rate (%)", min_value=0.0, max_value=100.0, step=0.1)

    cols4 = st.columns(2)
    labour_hours = cols4[0].number_input("Labour Hours", min_value=0.0, step=0.1)
    labour_efficiency = cols4[1].number_input("Labour Efficiency (gaps/hr)", min_value=0.0, step=0.1)

    submitted = st.form_submit_button("Submit")

if submitted:
    new_entry = pd.DataFrame([{
        "Farmer Name": farmer_name,
        "Field ID": field_id,
        "Area (acre)": area_acre,
        "Area (m)": area_m,
        "Row × Plant Spacing (cm)": spacing_cm,
        "Row × Plant Spacing (m)": spacing_m,
        "Sowing Date": sowing_date,
        "Expected Plants": expected_plants,
        "Plants Emerged": plants_emerged,
        "Actual Stand (%)": actual_stand,
        "Missing Plants": missing_plants,
        "Gaps filled": gaps_filled,
        "Total Gaps": total_gaps,
        "Gap %": gap_percent,
        "Gap Filling Date": gap_filling_date,
        "Success Rate (%)": success_rate,
        "Labour Hours": labour_hours,
        "Labour Efficiency (gaps/hr)": labour_efficiency
    }])

    saved_data = pd.concat([saved_data, new_entry], ignore_index=True)
    saved_data.to_excel(excel_file, index=False)
    st.success("Data submitted and saved to Excel.")

st.markdown("---")
st.subheader("📊 Collected Submissions")

if not saved_data.empty:
    with st.expander("🔍 Filter Data"):
        farmers = saved_data["Farmer Name"].unique().tolist()
        selected_farmers = st.multiselect("Farmer Name", options=farmers, default=farmers)

        fields = saved_data["Field ID"].unique().tolist()
        selected_fields = st.multiselect("Field ID", options=fields, default=fields)

        filtered_data = saved_data[
            saved_data["Farmer Name"].isin(selected_farmers) &
            saved_data["Field ID"].isin(selected_fields)
        ]

    st.dataframe(filtered_data, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Summary Analysis")

    avg_gap_percent = filtered_data["Gap %"].mean()
    avg_success_rate = filtered_data["Success Rate (%)"].mean()
    avg_efficiency = filtered_data["Labour Efficiency (gaps/hr)"].mean()
    total_expected = filtered_data["Expected Plants"].sum()
    total_emerged = filtered_data["Plants Emerged"].sum()
    total_missing = filtered_data["Missing Plants"].sum()
    total_filled = filtered_data["Gaps filled"].sum()

    st.metric("Average Gap %", f"{avg_gap_percent:.2f}%")
    st.metric("Average Success Rate", f"{avg_success_rate:.2f}%")
    st.metric("Average Labour Efficiency", f"{avg_efficiency:.2f} gaps/hr")
    st.metric("Total Expected Plants", total_expected)
    st.metric("Total Emerged Plants", total_emerged)
    st.metric("Total Missing Plants", total_missing)
    st.metric("Total Gaps Filled", total_filled)

    st.markdown("---")
    st.subheader("📊 Charts")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig1 = px.bar(filtered_data, x="Farmer Name", y="Gap %", color="Field ID", title="Gap % by Farmer")
        st.plotly_chart(fig1, use_container_width=True)

    with chart_col2:
        fig2 = px.line(filtered_data.sort_values("Sowing Date"), x="Sowing Date", y="Success Rate (%)", color="Farmer Name", title="Success Rate Over Time")
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.scatter(filtered_data, x="Expected Plants", y="Plants Emerged", color="Farmer Name", size="Labour Efficiency (gaps/hr)", title="Expected vs Emerged Plants")
    st.plotly_chart(fig3, use_container_width=True)
