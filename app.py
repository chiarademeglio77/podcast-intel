import streamlit as st
import json
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Podcast Intel", layout="wide")

# --- 1. CSS HACK TO REDUCE TOP EMPTY SPACE ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            margin-top: 0rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# INITIALIZE SESSION STATE
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
def load_and_group_data():
    try:
        with open('app_data.json', 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        grouped = {}
        for item in raw_data:
            # Cleanup date string
            raw_date = item.get('date', 'Unknown').strip()
            if raw_date not in grouped:
                grouped[raw_date] = []
            grouped[raw_date].append(item)
            
        def parse_date(d):
            try:
                return datetime.strptime(d, '%d-%m-%y')
            except ValueError:
                return datetime.min 
                
        sorted_dates = sorted(grouped.keys(), key=parse_date, reverse=True)
        return raw_data, grouped, sorted_dates
    except FileNotFoundError:
        return [], {}, []

all_data, grouped_data, sorted_days = load_and_group_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("📋 Deep Dive Requests")
    if st.session_state['requests']:
        st.write(f"Selected: **{len(st.session_state['requests'])}**")
        file_content = "DEEP DIVE REQUESTS\n" + "\n".join([f"- {r}" for r in st.session_state['requests']])
        st.download_button("📥 Download list (.txt)", file_content, "requests.txt")
        st.button("Clear all selections", on_click=clear_requests, type="primary")
    else:
        st.info("Select items to build your list.")

# --- MAIN AREA ---
st.title("🎙️ Chiara Podcast Intelligence")

# --- 2. CALCULATE COUNTS FOR PILLARS ---
base_pillars = ["AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "China", "Europe", "Strategy", "Finance"]
pillars_with_counts = ["All"]

for p in base_pillars:
    # Count how many podcasts have this key
    count = 0
    for d in all_data:
        if p.lower() in [k.lower() for k in d.get('keys', [])]:
            count += 1
    # Create label like "China (3)"
    pillars_with_counts.append(f"{p} ({count})")

# Display Pillars
selected_pill_text = st.pills("Topic:", pillars_with_counts, selection_mode="single", default="All")

# Clean the selection back to just the word (e.g. "China (3)" -> "China")
if selected_pill_text and selected_pill_text != "All":
    selected_pillar = selected_pill_text.split(" (")[0]
else:
    selected_pillar = "All"

# --- 3. ALIGNED SEARCH BAR & BUTTON ---
# vertical_alignment="bottom" aligns the button to the input box perfectly
col1, col2 = st.columns([0.85, 0.15], vertical_alignment="bottom")

with col1:
    st.text_input("🔍 Search...", key="search_query")
with col2:
    st.button("Clear", on_click=clear_search, use_container_width