import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Sample data
data = pd.DataFrame({
    'Log_ID': ['LOG001', 'LOG002', 'LOG003', 'LOG004'],
    'Species': ['Meranti', 'Keruing', 'Merbau', 'Tapang'],
    'Volume_m3': [3.5, 5.2, 2.9, 4.1],
    'Region': ['Kapit', 'Bintulu', 'Sibu', 'Kuching'],
    'License_No': ['LIC123', 'LIC456', 'LIC123', 'LIC789'],
    'Truck_ID': ['TRK001', 'TRK002', 'TRK001', 'TRK003'],
    'Date': [datetime(2025, 7, 27), datetime(2025, 7, 27), datetime(2025, 7, 28), datetime(2025, 7, 28)],
    'Destination': ['Mill A', 'Mill B', 'Mill A', 'Mill C'],
    'Latitude': [2.016, 3.016, 2.215, 1.556],
    'Longitude': [113.02, 113.88, 112.95, 110.35]
})

# Sidebar Filters
st.sidebar.header("Filter Logs")
selected_region = st.sidebar.multiselect("Select Region", data['Region'].unique(), default=data['Region'].unique())
selected_date = st.sidebar.date_input("Select Date", datetime.today())

# Filter Data
filtered_data = data[
    (data['Region'].isin(selected_region)) &
    (data['Date'] == pd.to_datetime(selected_date))
]

st.title("🌲 Timber Log Tracking Dashboard")
st.markdown("Monitor and trace logging operations and timber flow in real time.")

# Show filtered data table
st.subheader("Log Records")
st.dataframe(filtered_data)

# Volume by Species
st.subheader("Log Volume by Species")
fig1 = px.bar(filtered_data, x='Species', y='Volume_m3', color='Species', title='Volume by Log Species')
st.plotly_chart(fig1)

# Map
st.subheader("Logging Activity Map")
st.map(filtered_data.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}))

# KPI Summary
total_volume = filtered_data['Volume_m3'].sum()
total_logs = len(filtered_data)
st.metric("Total Volume (m³)", f"{total_volume:.2f}")
st.metric("Total Logs Tracked", total_logs)
