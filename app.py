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

# --- DATA LOADING & GROUPING ---
def load_and_group_data():
    try:
        with open('app_data.json', 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        # Grouping by date
        grouped = {}
        for item in raw_data:
            date_str = item.get('date', 'Unknown Date')
            if date_str not in grouped:
                grouped[date_str] = []
            grouped[date_str].append(item)
            
        # Sort dates (newest first)
        sorted_dates = sorted(grouped.keys(), 
                             key=lambda x: datetime.strptime(x, '%d-%m-%y'), 
                             reverse=True)
        return grouped, sorted_dates
    except FileNotFoundError:
        return {}, []

grouped_data, sorted_days = load_and_group_data()

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

# 1. Topic Filters
pillars = ["All", "AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "China", "Europe", "Strategy", "Finance"]
selected_pillar = st.pills("Filter by Topic:", pillars, selection_mode="single", default="All")

# 2. Search
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.text_input("🔍 Search within summaries...", key="search_query")
with col2:
    st.write("##")
    st.button("Clear Search", on_click=clear_search, use_container_width=True)

st.divider()

# --- RENDERING BY DAY ---
search_term = st.session_state["search_query"].lower()

for day in sorted_days:
    # Filter podcasts for this day based on Pillar and Search
    podcasts_this_day = []
    for ep in grouped_data[day]:
        matches_pillar = (selected_pillar == "All" or 
                          selected_pillar.lower() in [k.lower() for k in ep.get('keys', [])])
        matches_search = (not search_term or search_term in str(ep).lower())
        
        if matches_pillar and matches_search:
            podcasts_this_day.append(ep)
    
    # Only show the day if it contains matching podcasts
    if podcasts_this_day:
        with st.expander(f"📅 {day} ({len(podcasts_this_day)} podcasts)", expanded=(day == sorted_days[0])):
            for ep in podcasts_this_day:
                filename = ep.get('file', 'Untitled')
                # Remove the date prefix from title if present (e.g., "28-01-26 | ")
                clean_title = filename.split('|')[-1].strip() if '|' in filename else filename
                
                st.markdown(f"### {clean_title}")
                st.markdown(f"**Keywords:** :blue[{', '.join(ep.get('keys', []))}]")
                st.write(ep.get('summary'))
                
                # Checkbox
                is_selected = filename in st.session_state['requests']
                if st.checkbox(f"Add to request list", key=f"check_{filename}", value=is_selected):
                    if filename not in st.session_state['requests']:
                        st.session_state['requests'].append(filename)
                        st.rerun()
                else:
                    if filename in st.session_state['requests']:
                        st.session_state['requests'].remove(filename)
                        st.rerun()
                st.divider()