import streamlit as st
import json

# Page configuration
st.set_page_config(page_title="Chiara Podcast Intel", layout="wide")

# 1. Initialize session state
if 'requests' not in st.session_state:
    st.session_state['requests'] = []

if 'search_query' not in st.session_state:
    st.session_state['search_query'] = ""

# --- CALLBACK FUNCTIONS ---

def clear_search():
    st.session_state["search_query"] = ""

def clear_requests():
    # 1. Empty the master list
    st.session_state['requests'] = []
    # 2. Find and reset all checkbox widget keys in memory
    for key in st.session_state.keys():
        if key.startswith("check_"):
            st.session_state[key] = False

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
        
        # Hard Reset Button
        st.button("Clear all selections", on_click=clear_requests, type="primary")
    else:
        st.info("Select podcasts from the list to build your request.")

# --- MAIN AREA ---
st.title("🎙️ Chiara Podcast Intelligence")
st.write("Professional summaries and key insights from curated transcripts.")

# 1. Topic Filters
pillars = ["All", "AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "China", "Europe", "Strategy", "Finance"]
selected_pillar = st.pills("Main Topic:", pillars, selection_mode="single", default="All")

# 2. Search Bar
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.text_input("🔍 Search within text...", placeholder="Search for companies, names, or themes...", key="search_query")
with col2:
    st.write("##")
    st.button("Clear Search", on_click=clear_search, use_container_width=True)

st.divider()

# FILTERING LOGIC
filtered_data = data
if selected_pillar and selected_pillar != "All":
    filtered_data = [d for d in filtered_data if selected_pillar.lower() in [k.lower() for k in d.get('keys', [])]]

current_search = st.session_state["search_query"]
if current_search:
    filtered_data = [d for d in filtered_data if current_search.lower() in str(d).lower()]

st.subheader(f"Podcasts Displayed: {len(filtered_data)}")

# DISPLAY RESULTS
for ep in filtered_data:
    filename = ep.get('file')
    # Generate a unique key for the checkbox
    cb_key = f"check_{filename}"
    
    with st.expander(f"📅 {ep.get('date')} | {filename}"):
        st.markdown(f"**Keywords found:** :blue[{', '.join(ep.get('keys', []))}]")
        st.write(f"**Summary:** {ep.get('summary')}")
        
        # Checkbox logic: If the checkbox is clicked, update the list
        if st.checkbox("Add to my deep dive request list", key=cb_key):
            if filename not in st.session_state['requests']:
                st.session_state['requests'].append(filename)
        else:
            if filename in st.session_state['requests']:
                st.session_state['requests'].remove(filename)

# A single rerun at the end ensures the sidebar updates immediately without lag
if st.session_state.get('last_requests_len') != len(st.session_state['requests']):
    st.session_state['last_requests_len'] = len(st.session_state['requests'])
    st.rerun()