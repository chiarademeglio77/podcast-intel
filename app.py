import streamlit as st
import json

st.set_page_config(page_title="Chiara Podcast Intel", layout="wide")

# Initialize session state for requests and search
if 'requests' not in st.session_state:
    st.session_state['requests'] = []
if 'search_text' not in st.session_state:
    st.session_state['search_text'] = ""

def load_data():
    try:
        with open('app_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

data = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("📋 Deep Dive Requests")
    
    if st.session_state['requests']:
        st.write(f"Selected: **{len(st.session_state['requests'])}** podcasts")
        file_content = "DEEP DIVE REQUESTS - CHIARA PODCAST INTEL\n-------------------------------------------\n\n"
        file_content += "\n".join([f"- {r}" for r in st.session_state['requests']])
        
        st.download_button(
            label="📥 Download list (.txt)",
            data=file_content,
            file_name="podcast_requests.txt",
            mime="text/plain"
        )
        
        if st.button("Clear all selections"):
            st.session_state['requests'] = []
            st.rerun()
    else:
        st.info("Select podcasts from the list to build your request.")

# --- MAIN AREA ---
st.title("🎙️ Chiara Podcast Intelligence")
st.write("Professional summaries and key insights from curated transcripts.")

# 1. Topic Filters (Pillars)
pillars = ["All", "AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "China", "Europe", "Strategy", "Finance"]
selected_pillar = st.pills("Main Topic:", pillars, selection_mode="single", default="All")

# 2. Search Bar with Clear Button
col1, col2 = st.columns([0.85, 0.15])
with col1:
    search_query = st.text_input(
        "🔍 Search within text...", 
        placeholder="Search for companies, names, or themes...",
        value=st.session_state['search_text'],
        key="search_input"
    )
    # Update state whenever user types
    st.session_state['search_text'] = search_query

with col2:
    st.write(" ") # Padding for alignment
    st.write(" ") # Padding for alignment
    if st.button("Clear Search", use_container_width=True):
        st.session_state['search_text'] = ""
        st.rerun()

st.divider()

# FILTERING LOGIC
filtered_data = data

# Filter by Pillar
if selected_pillar and selected_pillar != "All":
    filtered_data = [d for d in filtered_data if selected_pillar.lower() in [k.lower() for k in d.get('keys', [])]]

# Filter by Search Query
if st.session_state['search_text']:
    s = st.session_state['search_text'].lower()
    filtered_data = [
        d for d in filtered_data 
        if s in str(d).lower()
    ]

st.subheader(f"Podcasts Displayed: {len(filtered_data)}")

for ep in filtered_data:
    with st.expander(f"📅 {ep.get('date')} | {ep.get('file')}"):
        # Show ALL keywords found in the JSON
        st.markdown(f"**Keywords found:** :blue[{', '.join(ep.get('keys', []))}]")
        st.write(f"**Summary:** {ep.get('summary')}")
        
        filename = ep.get('file')
        is_selected = filename in st.session_state['requests']
        
        if st.checkbox("Add to my deep dive request list", value=is_selected, key=filename):
            if filename not in st.session_state['requests']:
                st.session_state['requests'].append(filename)
                st.rerun()
        else:
            if filename in st.session_state['requests']:
                st.session_state['requests'].remove(filename)
                st.rerun()