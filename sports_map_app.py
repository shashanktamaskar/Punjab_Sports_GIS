import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Load data
file_path = "Information regarding nursery location.xlsx"
xls = pd.ExcelFile(file_path)
df = xls.parse('Sheet1')

# Rename columns for clarity
df.columns = ['Sr. No.', 'Dist. Wise Sr. No', 'District', 'Constituency', 'Nursery', 'Ownership', 'Area', 'Game', 'Coordinates', 'Latitude', 'Longitude', 'Unnamed', 'Remarks']
df = df[['District', 'Constituency', 'Nursery', 'Ownership', 'Area', 'Game', 'Latitude', 'Longitude']].dropna()

# Ensure Latitude and Longitude are numeric
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

# Drop rows where conversion failed
df = df.dropna(subset=['Latitude', 'Longitude'])

def create_map(df):
    # Create folium map with Google Hybrid View
    m = folium.Map(
        location=[df['Latitude'].mean(), df['Longitude'].mean()], 
        zoom_start=10
    )

    # Add Google Hybrid View as a tile layer
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google Hybrid",
        name="Google Hybrid",
        overlay=False,
        control=True
    ).add_to(m)

    # Clustered markers
    marker_cluster = MarkerCluster().add_to(m)

    # Define sports icons
    sport_icons = {
        'Basketball': 'basketball-ball',
        'Volleyball': 'volleyball-ball',
        'Football': 'futbol',
        'Cricket': 'baseball-ball',
        'Hockey': 'hockey-puck',
    }

    for _, row in df.iterrows():
        icon = folium.Icon(icon=sport_icons.get(row['Game'], 'info-sign'), prefix='fa', color='blue')
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<b>{row['Nursery']}</b><br>{row['Game']}<br>{row['Ownership']}<br>Area: {row['Area']}",
            icon=icon
        ).add_to(marker_cluster)

    return m



# Streamlit App
st.title("Constituency-wise Sports Facilities Map")
st.sidebar.header("Filters")

# Dropdowns for filtering
selected_district = st.sidebar.selectbox("Select District", ['All'] + list(df['District'].unique()))
#selected_constituency = st.sidebar.selectbox("Select Constituency", ['All'] + list(df['Constituency'].unique()))
selected_sport = st.sidebar.selectbox("Select Sport", ['All'] + list(df['Game'].unique()))

# Apply Filters
filtered_df = df.copy()
if selected_district != 'All':
    filtered_df = filtered_df[filtered_df['District'] == selected_district]
#if selected_constituency != 'All':
#    filtered_df = filtered_df[filtered_df['Constituency'] == selected_constituency]
if selected_sport != 'All':
    filtered_df = filtered_df[filtered_df['Game'] == selected_sport]

# Display Map
if not filtered_df.empty:
    folium_static(create_map(filtered_df))
else:
    st.write("No data available for the selected filters.")
