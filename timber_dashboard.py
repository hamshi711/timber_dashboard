
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
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

    # Convert 'Date' column to datetime
    data['Date'] = pd.to_datetime(data['Date'])

    # Filter Data
    filtered_data = data[
        (data['Region'].isin(selected_region)) &
        (data['Date'] == pd.to_datetime(selected_date))
    ]

    # Show filtered data table
    st.subheader("📋 Log Records")
    st.dataframe(filtered_data)

    # Bar chart
    st.subheader("🌳 Log Volume by Species")
    fig1 = px.bar(filtered_data, x='Species', y='Volume_m3', color='Species', title='Volume by Log Species')
    st.plotly_chart(fig1)

    # Route map using pydeck
    st.subheader("🚛 Truck Routes: From Camp to Destination")

    # Separate camps and destinations (example assumption: logs that went to mill are not at camp)
    route_data = data.copy()
    route_data['At_Camp'] = route_data['Destination'].str.lower().str.contains('camp')

    moved_logs = route_data[~route_data['At_Camp']]
    route_pairs = []

    for _, row in moved_logs.iterrows():
        # Simulate camp coordinates based on known region (for demo purpose)
        if "kapit" in row['Region'].lower():
            start_lat, start_lon = 2.016, 113.02
        elif "sibu" in row['Region'].lower():
            start_lat, start_lon = 2.215, 112.95
        elif "bintulu" in row['Region'].lower():
            start_lat, start_lon = 3.016, 113.88
        elif "kuching" in row['Region'].lower():
            start_lat, start_lon = 1.556, 110.35
        else:
            start_lat, start_lon = row['Latitude'], row['Longitude']  # fallback

        route_pairs.append({
            "from_lat": start_lat,
            "from_lon": start_lon,
            "to_lat": row['Latitude'],
            "to_lon": row['Longitude']
        })

    route_df = pd.DataFrame(route_pairs)

    if not route_df.empty:
        layer = pdk.Layer(
            "ArcLayer",
            data=route_df,
            get_source_position='[from_lon, from_lat]',
            get_target_position='[to_lon, to_lat]',
            get_width=4,
            get_tilt=15,
            get_source_color=[0, 128, 255],
            get_target_color=[255, 0, 0],
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            latitude=route_df["from_lat"].mean(),
            longitude=route_df["from_lon"].mean(),
            zoom=6,
            pitch=45,
        )

        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    # KPI Summary
    st.metric("📦 Total Volume (m³)", f"{filtered_data['Volume_m3'].sum():.2f}")
    st.metric("📄 Total Logs Tracked", len(filtered_data))

    # Log Balance at Camp
    st.subheader("📍 Log Balance at Logging Camp")
    data['At_Camp'] = data['Destination'].str.lower().str.contains('camp')
    camp_balance = data.groupby(['Region', 'At_Camp'])['Log_ID'].count().unstack(fill_value=0)
    camp_balance['Logs_Remaining_At_Camp'] = camp_balance.get(True, 0)
    st.dataframe(camp_balance[['Logs_Remaining_At_Camp']])

    # Grouping by License and Truck
    st.subheader("🚚 Grouped by License No and Truck ID")
    group_summary = data.groupby(['License_No', 'Truck_ID'])['Log_ID'].count().reset_index(name='Logs_Count')
    st.dataframe(group_summary)

    # Aging of logs at camp
    st.subheader("⏳ Log Aging at Camp")
    camp_logs = data[data['At_Camp']].copy()
    camp_logs['Days_At_Camp'] = (pd.to_datetime(datetime.today()) - camp_logs['Date']).dt.days
    st.dataframe(camp_logs[['Log_ID', 'Region', 'Species', 'Date', 'Days_At_Camp']])

    # Alert for logs > 7 days at camp
    overdue_logs = camp_logs[camp_logs['Days_At_Camp'] > 7]
    if not overdue_logs.empty:
        st.warning("⚠️ Overdue Logs: The following logs have stayed at camp for more than 7 days!")
        st.dataframe(overdue_logs[['Log_ID', 'Region', 'Species', 'Date', 'Days_At_Camp']])
    else:
        st.success("✅ No overdue logs at camp.")
else:
    st.warning("Please upload a CSV file to get started.")
