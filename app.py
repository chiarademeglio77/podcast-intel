import streamlit as st
import json

st.set_page_config(page_title="Chiara Podcast Intel", layout="wide")

if 'richieste' not in st.session_state:
    st.session_state['richieste'] = []

def load_data():
    try:
        with open('app_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

data = load_data()

# --- BARRA LATERALE (CARRELLO) ---
with st.sidebar:
    st.header("📋 Lista Approfondimenti")
    if st.session_state['richieste']:
        st.write(f"Selezionati: **{len(st.session_state['richieste'])}**")
        testo_file = "RICHIESTA DEEP DIVE - CHIARA PODCAST\n\n" + "\n".join([f"- {r}" for r in st.session_state['richieste']])
        st.download_button("📥 Scarica lista (.txt)", testo_file, "richieste_chiara.txt")
        if st.button("Svuota lista"):
            st.session_state['richieste'] = []
            st.rerun()
    else:
        st.info("Seleziona i podcast a destra.")

# --- AREA PRINCIPALE ---
st.title("🎙️ Chiara Podcast Intelligence")

# 1. Filtri (Aggiunto "Tutti" per tornare indietro facilmente)
pillars = ["Tutti", "AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "China", "Europe", "Strategy", "Finance"]
selected_pillar = st.pills("Argomento principale:", pillars, selection_mode="single", default="Tutti")

# 2. Ricerca libera
search_query = st.text_input("🔍 Cerca nei testi...", placeholder="Cerca aziende, nomi o temi...")

st.divider()

# LOGICA DI FILTRAGGIO
filtered_data = data

# Applica Pillar (se non è "Tutti")
if selected_pillar and selected_pillar != "Tutti":
    filtered_data = [d for d in filtered_data if selected_pillar.lower() in [k.lower() for k in d.get('keys', [])]]

# Applica Ricerca
if search_query:
    filtered_data = [d for d in filtered_data if search_query.lower() in str(d).lower()]

st.subheader(f"Podcast visualizzati: {len(filtered_data)}")

for ep in filtered_data:
    with st.expander(f"📅 {ep.get('date')} | {ep.get('file')}"):
        # Mostra TUTTE le keywords presenti nel JSON
        st.markdown(f"**Keywords trovate:** :blue[{', '.join(ep.get('keys', []))}]")
        st.write(f"**Riassunto:** {ep.get('summary')}")
        
        titolo = ep.get('file')
        if st.checkbox("Aggiungi alla lista", value=(titolo in st.session_state['richieste']), key=titolo):
            if titolo not in st.session_state['richieste']:
                st.session_state['richieste'].append(titolo)
                st.rerun()
        else:
            if titolo in st.session_state['richieste']:
                st.session_state['richieste'].remove(titolo)
                st.rerun()