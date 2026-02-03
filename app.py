import streamlit as st
import pandas as pd
import os
from bms import scrape_bookmyshow, update_event_sheet

st.set_page_config(page_title="Pixie: Event Discovery", layout="wide")

# --- UI Header ---
st.title("🎟️ Pixie: Event Discovery & Tracking")
st.markdown("Automated tool to discover upcoming events for photobooth installations.")

# --- Sidebar: Scraping Controls ---
st.sidebar.header("Control Panel")
target_city = st.sidebar.text_input("Enter City to Scrape", value="Jaipur")

if st.sidebar.button("Run Scraper Now"):
    with st.spinner(f"Searching for new events in {target_city}..."):
        new_data = scrape_bookmyshow(target_city)
        if not new_data.empty:
            update_event_sheet(new_data)
            st.sidebar.success(f"Updated! Found {len(new_data)} events.")
        else:
            st.sidebar.warning("No new events found.")

# --- Main Dashboard: Data Display ---
st.subheader("Current Event Database")
filename = "event_tracker.xlsx"

if os.path.exists(filename):
    df = pd.read_excel(filename)
    
    # Requirement: Filtering/Searching
    col1, col2 = st.columns(2)
    with col1:
        status_choice = st.multiselect("Filter by Status", options=df['status'].unique(), default=df['status'].unique())
    with col2:
        category_search = st.text_input("Search Category (e.g., Music, Comedy)")

    # Apply Filters
    mask = df['status'].isin(status_choice)
    if category_search:
        mask &= df['event_name'].str.contains(category_search, case=False, na=False)
    
    filtered_df = df[mask]

    # Requirement: Stores and displays data
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # Requirement: Download Option
    with open(filename, "rb") as file:
        st.download_button(
            label="📥 Export Tracker to Excel",
            data=file,
            file_name="event_tracker.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("No data found. Enter a city and click 'Run Scraper Now' to begin.")
