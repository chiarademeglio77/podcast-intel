import streamlit as st
import json
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Chiara Podcast Intel", layout="wide")

# --- CSS TO REDUCE TOP SPACE & STYLE ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
        }
        .series-label {
            font-size: 14px;
            color: #666;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: -15px; 
        }
    </style>
""", unsafe_allow_html=True)

# INITIALIZE SESSION STATE
if 'requests' not in st.session_state:
    st.session_state['requests'] = []
if 'search_query' not in st.session_state:
    st.session_state['search_query'] = ""
if 'selected_series' not in st.session_state:
    st.session_state['selected_series'] = []

# --- CALLBACKS ---
def clear_all_filters():
    st.session_state["search_query"] = ""
    st.session_state["selected_series"] = [] # Resetta anche la selezione Podcast

def clear_requests():
    st.session_state['requests'] = []
    for key in st.session_state.keys():
        if key.startswith("check_"):
            st.session_state[key] = False

# --- DATA LOADING & PARSING ---
def load_and_group_data():
    try:
        with open('app_data.json', 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        grouped = {}
        all_series = {} # Dizionario per contare le serie
        
        for item in raw_data:
            # 1. Pulisce la data
            raw_date = item.get('date', 'Unknown').strip()
            
            # 2. Estrae il nome della Serie dal file (Prima dell'underscore)
            filename = item.get('file', '')
            clean_name = filename.replace(".txt", "").replace(raw_date, "").strip(" _|-")
            
            if "_" in clean_name:
                series_name = clean_name.split("_")[0].strip()
            else:
                series_name = "Other/Single Episodes"
                
            # Conta le serie
            all_series[series_name] = all_series.get(series_name, 0) + 1
            # Aggiunge nome serie al dato per filtraggio facile dopo
            item['series_name'] = series_name

            # Raggruppa per data
            if raw_date not in grouped:
                grouped[raw_date] = []
            grouped[raw_date].append(item)
            
        def parse_date(d):
            try:
                return datetime.strptime(d, '%d-%m-%y')
            except ValueError:
                return datetime.min 
                
        sorted_dates = sorted(grouped.keys(), key=parse_date, reverse=True)
        return raw_data, grouped, sorted_dates, all_series
        
    except FileNotFoundError:
        return [], {}, [], {}

all_data, grouped_data, sorted_days, series_counts = load_and_group_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("📋 Deep Dive Requests")
    
    # 1. SEZIONE FILTRO PODCAST (Nuova)
    st.subheader("🎙️ Filter by Podcast Series")
    
    # Crea le opzioni con il conteggio: "Business Wars (5)"
    series_options = [f"{k} ({v})" for k, v in series_counts.items()]
    series_options.sort() # Ordine alfabetico
    
    # Multiselect widget collegato allo stato
    selected_series_raw = st.multiselect(
        "Select series:",
        options=series_options,
        key="selected_series",
        placeholder="Choose a podcast..."
    )
    
    st.divider()
    
    # 2. SEZIONE CARRELLO
    if st.session_state['requests']:
        st.write(f"Selected: **{len(st.session_state['requests'])}**")
        file_content = "DEEP DIVE REQUESTS\n" + "\n".join([f"- {r}" for r in st.session_state['requests']])
        st.download_button("📥 Download list (.txt)", file_content, "requests.txt")
        st.button("Clear all selections", on_click=clear_requests, type="primary")
    else:
        st.info("Select items to build your list.")

# --- MAIN AREA ---
st.title("🎙️ Chiara Podcast Intelligence")

# --- PILLARS & COUNTS ---
base_pillars = ["AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "China", "Europe", "Strategy", "Finance"]
pillars_with_counts = ["All"]

for p in base_pillars:
    count = 0
    for d in all_data:
        if p.lower() in [k.lower() for k in d.get('keys', [])]:
            count += 1
    pillars_with_counts.append(f"{p} ({count})")

selected_pill_text = st.pills("Topic:", pillars_with_counts, selection_mode="single", default="All")
selected_pillar = selected_pill_text.split(" (")[0] if selected_pill_text and selected_pill_text != "All" else "All"

# --- SEARCH & CLEAR ---
col1, col2 = st.columns([0.85, 0.15], vertical_alignment="bottom")
with col1:
    st.text_input("🔍 Search...", key="search_query")
with col2:
    # Il bottone Clear ora pulisce ANCHE il filtro Podcast laterale
    st.button("Clear", on_click=clear_all_filters, use_container_width=True)

st.divider()

# --- RENDERING ---
search_term = st.session_state["search_query"].lower()
count_shown = 0

# Logica per pulire le opzioni selezionate nel multiselect (rimuovere il numero tra parentesi)
# Es: "Business Wars (3)" -> "Business Wars"
active_series_filters = [s.rpartition(' (')[0] for s in st.session_state["selected_series"]]

for day in sorted_days:
    podcasts_this_day = []
    for ep in grouped_data[day]:
        
        # 1. Filtro Topic
        matches_pillar = (selected_pillar == "All" or selected_pillar.lower() in [k.lower() for k in ep.get('keys', [])])
        
        # 2. Filtro Search
        matches_search = (not search_term or search_term in str(ep).lower())
        
        # 3. NUOVO Filtro Serie Podcast
        # Se non ho selezionato nulla (lista vuota), mostra tutto. Altrimenti controlla se la serie combacia.
        matches_series = (not active_series_filters) or (ep.get('series_name') in active_series_filters)
        
        if matches_pillar and matches_search and matches_series:
            podcasts_this_day.append(ep)
    
    if podcasts_this_day:
        count_shown += len(podcasts_this_day)
        with st.expander(f"📅 {day} ({len(podcasts_this_day)} items)", expanded=(day == sorted_days[0])):
            for ep in podcasts_this_day:
                filename = ep.get('file', 'Untitled')
                
                # Formattazione Titolo
                clean_name = filename.replace(".txt", "").replace(day, "").strip(" _|-")
                if "_" in clean_name:
                    parts = clean_name.split("_", 1)
                    st.markdown(f'<p class="series-label">🎙️ {parts[0].strip()}</p>', unsafe_allow_html=True)
                    st.markdown(f"#### {parts[1].strip()}")
                else:
                    st.markdown(f"#### {clean_name}")

                st.markdown(f"**Keywords:** :blue[{', '.join(ep.get('keys', []))}]")
                st.caption(ep.get('summary'))
                
                # Checkbox
                cb_key = f"check_{filename}"
                is_selected = filename in st.session_state['requests']
                
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