import streamlit as st
import json

# Set the page title and look
st.set_page_config(page_title="Chiara Podcast Intel", layout="wide")

# Initialize the "request list" in the session state
if 'requests' not in st.session_state:
    st.session_state['requests'] = []

def load_data():
    try:
        with open('app_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

data = load_data()

# --- SIDEBAR (THE REQUEST CART) ---
with st.sidebar:
    st.header("📋 Deep Dive Requests")
    
    if st.session_state['requests']:
        st.write(f"Selected: **{len(st.session_state['requests'])}** podcasts")
        
        # Prepare the TXT file content
        file_content = "DEEP DIVE REQUESTS - CHIARA PODCAST INTEL\n"
        file_content += "-------------------------------------------\n\n"
        file_content += "\n".join([f"- {r}" for r in st.session_state['requests']])
        
        # Download button
        st.download_button(
            label="📥 Download list (.txt)",
            data=file_content,
            file_name="podcast_requests.txt",
            mime="text/plain",
            help="Download this file and send it to Chiara via Teams or Email"
        )
        
        if st.button("Clear all selections"):
            st.session_state['requests'] = []
            st.rerun()
    else:
        st.info("Select podcasts from the list on the right to build your request.")

# --- MAIN AREA ---
st.title("🎙️ Chiara Podcast Intelligence")
st.write("Professional summaries and key insights from curated transcripts.")

# 1. Topic Filters (Pillars)
pillars = ["All", "AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "China", "Europe", "Strategy", "Finance"]
selected_pillar = st.pills("Main Topic:", pillars, selection_mode="single", default="All")

# 2. Search Bar
search_query = st.text_input("🔍 Search within text...", placeholder="Search for companies, names, or themes...")

st.divider()

# FILTERING LOGIC
filtered_data = data

# Filter by Pillar (unless "All" is selected)
if selected_pillar and selected_pillar != "All":
    filtered_data = [d for d in filtered_data if selected_pillar.lower() in [k.lower() for k in d.get('keys', [])]]

# Filter by Search Query
if search_query:
    filtered_data = [
        d for d in filtered_data 
        if search_query.lower() in str(d).lower()
    ]

st.subheader(f"Podcasts Displayed: {len(filtered_data)}")

for ep in filtered_data:
    # Use the filename and date as the header
    with st.expander(f"📅 {ep.get('date')} | {ep.get('file')}"):
        
        # Show all keywords
        st.markdown(f"**Keywords found:** :blue[{', '.join(ep.get('keys', []))}]")
        
        # Show the summary text
        st.write(f"**Summary:** {ep.get('summary')}")
        
        # Selection checkbox for the request list
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