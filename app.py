import streamlit as st
import json

# Cambiato il titolo della scheda del browser
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

# --- BARRA LATERALE ---
with st.sidebar:
    st.header("📋 Lista Approfondimenti")
    if st.session_state['richieste']:
        st.write(f"Hai selezionato **{len(st.session_state['richieste'])}** podcast.")
        testo_file = "RICHIESTA DEEP DIVE - CHIARA PODCAST\n-----------------------------------\n\n"
        testo_file += "\n".join([f"- {r}" for r in st.session_state['richieste']])
        
        st.download_button(
            label="📥 Scarica lista (.txt)",
            data=testo_file,
            file_name="richieste_chiara_podcast.txt",
            mime="text/plain"
        )
        if st.button("Svuota lista"):
            st.session_state['richieste'] = []
            st.rerun()
    else:
        st.info("Seleziona i podcast a destra per comporre la tua lista.")

# --- AREA PRINCIPALE ---
st.title("🎙️ Chiara Podcast Intelligence")
st.write("Professional summaries and key insights curated for the team.")

# 1. Filtri Rapidi (Pillars)
pillars = ["AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "China", "Europe", "Strategy", "Finance"]
selected_pillar = st.pills("Filtra per argomento principale:", pillars, selection_mode="single")

# 2. Barra di ricerca libera
search_query = st.text_input("🔍 Cerca nei riassunti...", placeholder="Cerca aziende, nomi o parole chiave...")

st.divider()

# Logica di filtraggio
filtered_data = data
if selected_pillar:
    filtered_data = [d for d in filtered_data if selected_pillar.lower() in [k.lower() for k in d.get('keys', [])]]
if search_query:
    filtered_data = [d for d in filtered_data if search_query.lower() in str(d).lower()]

st.subheader(f"Podcast disponibili: {len(filtered_data)}")

for ep in filtered_data:
    with st.expander(f"📅 {ep.get('date')} | {ep.get('file')}"):
        # Keywords e Riassunto
        st.markdown(f"**Keywords:** :blue[{', '.join(ep.get('keys', []))}]")
        st.write(f"**Riassunto:** {ep.get('summary')}")
        
        # Checkbox carrello
        titolo = ep.get('file')
        is_selected = titolo in st.session_state['richieste']
        if st.checkbox("Aggiungi alla mia lista", value=is_selected, key=titolo):
            if titolo not in st.session_state['richieste']:
                st.session_state['richieste'].append(titolo)
                st.rerun()
        else:
            if titolo in st.session_state['richieste']:
                st.session_state['richieste'].remove(titolo)
                st.rerun()