
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.title("🌲 Timber Log Tracking Dashboard")
st.markdown("Upload your CSV file to visualize and monitor logging operations.")

# Upload CSV File
st.sidebar.header("📁 Upload Your Timber CSV")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

    # Sidebar Filters
    st.sidebar.header("🔍 Filter Logs")
    selected_region = st.sidebar.multiselect("Select Region", data['Region'].unique(), default=data['Region'].unique())
    selected_date = st.sidebar.date_input("Select Date", datetime.today())

    # Filter Data
    filtered_data = data[
        (data['Region'].isin(selected_region)) &
        (pd.to_datetime(data['Date']) == pd.to_datetime(selected_date))
    ]

    # Show filtered data table
    st.subheader("📋 Log Records")
    st.dataframe(filtered_data)

    # Bar chart
    st.subheader("🌳 Log Volume by Species")
    fig1 = px.bar(filtered_data, x='Species', y='Volume_m3', color='Species', title='Volume by Log Species')
    st.plotly_chart(fig1)

    # Map
    st.subheader("🗺️ Logging Activity Map")
    st.map(filtered_data.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}))

    # KPI Summary
    st.metric("📦 Total Volume (m³)", f"{filtered_data['Volume_m3'].sum():.2f}")
    st.metric("📄 Total Logs Tracked", len(filtered_data))

    # Log Balance at Camp
    st.subheader("📍 Log Balance at Logging Camp")
    data['At_Camp'] = data['Destination'].str.lower().str.contains('camp')
    camp_balance = data.groupby(['Region', 'At_Camp'])['Log_ID'].count().unstack(fill_value=0)
    camp_balance['Logs_Remaining_At_Camp'] = camp_balance.get(True, 0)
    st.dataframe(camp_balance[['Logs_Remaining_At_Camp']])
else:
    st.warning("Please upload a CSV file to get started.")
