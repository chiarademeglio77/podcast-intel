import streamlit as st
import json
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Podcast Intel", layout="wide")

# --- CSS TO REDUCE TOP SPACE ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
        }
        /* Style for the Series Name (Small Label) */
        .series-label {
            font-size: 14px;
            color: #666;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: -15px; /* Pulls the title closer */
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

# --- COUNTS ---
base_pillars = ["AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "China", "Europe", "Strategy", "Finance"]
pillars_with_counts = ["All"]

for p in base_pillars:
    count = 0
    for d in all_data:
        if p.lower() in [k.lower() for k in d.get('keys', [])]:
            count += 1
    pillars_with_counts.append(f"{p} ({count})")

# Pillars Display
selected_pill_text = st.pills("Topic:", pillars_with_counts, selection_mode="single", default="All")
if selected_pill_text and selected_pill_text != "All":
    selected_pillar = selected_pill_text.split(" (")[0]
else:
    selected_pillar = "All"

# --- SEARCH ---
col1, col2 = st.columns([0.85, 0.15], vertical_alignment="bottom")
with col1:
    st.text_input("🔍 Search...", key="search_query")
with col2:
    st.button("Clear", on_click=clear_search, use_container_width=True)

st.divider()

# --- RENDERING LOOP ---
search_term = st.session_state["search_query"].lower()
count_shown = 0

for day in sorted_days:
    podcasts_this_day = []
    for ep in grouped_data[day]:
        matches_pillar = (selected_pillar == "All" or 
                          selected_pillar.lower() in [k.lower() for k in ep.get('keys', [])])
        matches_search = (not search_term or search_term in str(ep).lower())
        
        if matches_pillar and matches_search:
            podcasts_this_day.append(ep)
    
    if podcasts_this_day:
        count_shown += len(podcasts_this_day)
        with st.expander(f"📅 {day} ({len(podcasts_this_day)} items)", expanded=(day == sorted_days[0])):
            for ep in podcasts_this_day:
                filename = ep.get('file', 'Untitled')
                
                # --- LOGICA DI FORMATTAZIONE TITOLO ---
                # 1. Rimuovi .txt e la data iniziale
                clean_name = filename.replace(".txt", "")
                clean_name = clean_name.replace(day, "").strip(" _|-")
                
                # 2. Dividi Serie e Titolo usando l'underscore
                if "_" in clean_name:
                    parts = clean_name.split("_", 1) # Divide solo al primo _
                    series_name = parts[0].strip()
                    episode_title = parts[1].strip()
                    
                    # Stampa Serie (piccolo)
                    st.markdown(f'<p class="series-label">🎙️ {series_name}</p>', unsafe_allow_html=True)
                    # Stampa Titolo (grande)
                    st.markdown(f"#### {episode_title}")
                else:
                    # Se non c'è underscore, stampa tutto come titolo
                    st.markdown(f"#### {clean_name}")
                
                # --------------------------------------

                st.markdown(f"**Keywords:** :blue[{', '.join(ep.get('keys', []))}]")
                st.caption(ep.get('summary'))
                
                # Checkbox
                is_selected = filename in st.session_state['requests']
                cb_key = f"check_{filename}"
                
                if st.checkbox("Add to request list", key=cb_key, value=is_selected):
                    if filename not in st.session_state['requests']:
                        st.session_state['requests'].append(filename)
                        st.rerun()
                else:
                    if filename in st.session_state['requests']:
                        st.session_state['requests'].remove(filename)
                        st.rerun()
                st.divider()

if count_shown == 0:
    st.warning("No podcasts found matching your filters.")