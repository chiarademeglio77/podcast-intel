import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_title="Chiara Podcast Intel", layout="wide")

# 1. Inizializzazione Memoria
if 'requests' not in st.session_state:
    st.session_state['requests'] = []
if 'search_query' not in st.session_state:
    st.session_state['search_query'] = ""

# --- FUNZIONI DI PULIZIA (CALLBACKS) ---
def clear_search():
    st.session_state["search_query"] = ""

def clear_requests():
    st.session_state['requests'] = []
    # Reset forzato di tutte le checkbox
    for key in st.session_state.keys():
        if key.startswith("check_"):
            st.session_state[key] = False

# --- CARICAMENTO DATI (CON FIX PER L'ERRORE) ---
def load_and_group_data():
    try:
        with open('app_data.json', 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        grouped = {}
        for item in raw_data:
            # FIX: .strip() rimuove gli spazi invisibili che causavano l'errore
            raw_date = item.get('date', 'Unknown')
            date_str = raw_date.strip() 
            
            if date_str not in grouped:
                grouped[date_str] = []
            grouped[date_str].append(item)
            
        # Funzione sicura per ordinare le date
        def parse_date(d):
            try:
                return datetime.strptime(d, '%d-%m-%y')
            except ValueError:
                return datetime.min # Se la data è sbagliata, va in fondo
                
        sorted_dates = sorted(grouped.keys(), key=parse_date, reverse=True)
        return grouped, sorted_dates
    except FileNotFoundError:
        return {}, []

grouped_data, sorted_days = load_and_group_data()

# --- SIDEBAR (CARRELLO) ---
with st.sidebar:
    st.header("📋 Deep Dive Requests")
    if st.session_state['requests']:
        st.write(f"Selected: **{len(st.session_state['requests'])}**")
        file_content = "DEEP DIVE REQUESTS\n" + "\n".join([f"- {r}" for r in st.session_state['requests']])
        st.download_button("📥 Download list (.txt)", file_content, "requests.txt")
        st.button("Clear all selections", on_click=clear_requests, type="primary")
    else:
        st.info("Select items to build your list.")

# --- AREA PRINCIPALE ---
st.title("🎙️ Chiara Podcast Intelligence")

# 1. Filtri
pillars = ["All", "AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "China", "Europe", "Strategy", "Finance"]
selected_pillar = st.pills("Topic:", pillars, selection_mode="single", default="All")

# 2. Ricerca
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.text_input("🔍 Search...", key="search_query")
with col2:
    st.write("##")
    st.button("Clear", on_click=clear_search, use_container_width=True)

st.divider()

# --- VISUALIZZAZIONE PER GIORNO ---
search_term = st.session_state["search_query"].lower()
count_shown = 0

for day in sorted_days:
    # Filtra i podcast di questo giorno
    podcasts_this_day = []
    for ep in grouped_data[day]:
        # Filtro Argomento
        matches_pillar = (selected_pillar == "All" or 
                          selected_pillar.lower() in [k.lower() for k in ep.get('keys', [])])
        # Filtro Ricerca Testo
        matches_search = (not search_term or search_term in str(ep).lower())
        
        if matches_pillar and matches_search:
            podcasts_this_day.append(ep)
    
    # Se ci sono podcast per questo giorno, mostra il gruppo
    if podcasts_this_day:
        count_shown += len(podcasts_this_day)
        # Il primo giorno è aperto di default, gli altri chiusi
        with st.expander(f"📅 {day} ({len(podcasts_this_day)} items)", expanded=(day == sorted_days[0])):
            for ep in podcasts_this_day:
                filename = ep.get('file', 'Untitled')
                
                # PULIZIA TITOLO: Rimuove la data (es. "28-01-26") dal nome del file
                clean_title = filename.replace(day, "").strip(" _|-")
                
                # Layout del singolo podcast
                st.markdown(f"### {clean_title}")
                st.markdown(f"**Keywords:** :blue[{', '.join(ep.get('keys', []))}]")
                st.caption(ep.get('summary'))
                
                # Checkbox selezione
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