import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_title="Chiara Podcast Intel", layout="wide")

# 1. Initialize session state
if 'requests' not in st.session_state:
    st.session_state['requests'] = []
if 'search_query' not in st.session_state:
    st.session_state['search_query'] = ""

# --- CALLBACKS ---
def clear_search():
    st.session_state["search_query"] = ""

def clear_requests():
    st.session_state['requests'] = []
    for key in st.session_state.keys():
        if key.startswith("check_"):
            st.session_state[key] = False

# --- DATA LOADING ---
def load_data():
    try:
        with open('app_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Standardize dates for sorting/filtering
            for item in data:
                try:
                    item['dt_obj'] = datetime.strptime(item.get('date', '01-01-20'), '%d-%m-%y').date()
                except:
                    item['dt_obj'] = datetime.today().date()
            return data
    except FileNotFoundError:
        return []

data = load_data()

# Get date range from data
if data:
    all_dates = [d['dt_obj'] for d in data]
    min_date = min(all_dates)
    max_date = max(all_dates)
else:
    min_date = max_date = datetime.today().date()

# --- SIDEBAR ---
with st.sidebar:
    st.header("📋 Deep Dive Requests")
    
    # NEW: Date Range Filter
    st.subheader("📅 Filter by Date")
    selected_dates = st.date_input(
        "Select date range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filter podcasts based on their report date"
    )

    st.divider()
    
    if st.session_state['requests']:
        st.write(f"Selected: **{len(st.session_state['requests'])}**")
        file_content = "DEEP DIVE REQUESTS\n" + "\n".join([f"- {r}" for r in st.session_state['requests']])
        st.download_button("📥 Download list (.txt)", file_content, "requests.txt")
        st.button("Clear all selections", on_click=clear_requests, type="primary")
    else:
        st.info("Select items from the main list.")

# --- MAIN AREA ---
st.title("🎙️ Chiara Podcast Intelligence")

# 1. Topic Filters
pillars = ["All", "AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "China", "Europe", "Strategy", "Finance"]
selected_pillar = st.pills("Main Topic:", pillars, selection_mode="single", default="All")

# 2. Search
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.text_input("🔍 Search within text...", key="search_query")
with col2:
    st.write("##")
    st.button("Clear Search", on_click=clear_search, use_container_width=True)

# --- FILTERING LOGIC ---
filtered_data = data

# Filter by Date Range
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_data = [d for d in filtered_data if start_date <= d['dt_obj'] <= end_date]

# Filter by Pillar
if selected_pillar and selected_pillar != "All":
    filtered_data = [d for d in filtered_data if selected_pillar.lower() in [k.lower() for k in d.get('keys', [])]]

# Filter by Search
curr_search = st.session_state["search_query"]
if curr_search:
    filtered_data = [d for d in filtered_data if curr_search.lower() in str(d).lower()]

st.subheader(f"Podcasts Displayed: {len(filtered_data)}")

for ep in filtered_data:
    filename = ep.get('file')
    with st.expander(f"📅 {ep.get('date')} | {filename}"):
        st.markdown(f"**Keywords:** :blue[{', '.join(ep.get('keys', []))}]")
        st.write(f"**Summary:** {ep.get('summary')}")
        
        if st.checkbox("Add to request list", key=f"check_{filename}", value=(filename in st.session_state['requests'])):
            if filename not in st.session_state['requests']:
                st.session_state['requests'].append(filename)
                st.rerun()
        else:
            if filename in st.session_state['requests']:
                st.session_state['requests'].remove(filename)
                st.rerun()