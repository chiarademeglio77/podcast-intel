import streamlit as st
import json

st.set_page_config(page_title="Grover Podcast Intel", layout="wide")

# Inizializziamo il "carrello" delle richieste
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
        
        # Prepariamo il contenuto del file TXT
        testo_file = "RICHIESTA DEEP DIVE - PODCAST INTEL\n"
        testo_file += "-----------------------------------\n\n"
        testo_file += "\n".join([f"- {r}" for r in st.session_state['richieste']])
        
        # PULSANTE DI DOWNLOAD
        st.download_button(
            label="📥 Scarica lista (.txt)",
            data=testo_file,
            file_name="richieste_podcast.txt",
            mime="text/plain",
            help="Scarica il file e invialo ad Andromeda su Teams o via Email"
        )
        
        if st.button("Svuota lista"):
            st.session_state['richieste'] = []
            st.rerun()
    else:
        st.info("Seleziona i podcast dall'elenco a destra per comporre la tua lista.")

# --- AREA PRINCIPALE ---
st.title("🎙️ Grover Podcast Intelligence")
st.write("Seleziona i temi che vuoi approfondire e scarica la lista finale dalla barra laterale.")

for ep in data:
    # Mostriamo titolo e data
    with st.expander(f"📅 {ep.get('date')} | {ep.get('file')}"):
        st.write(f"**Riassunto:** {ep.get('summary')}")
        
        # Logica della checkbox per aggiungere/rimuovere
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