import streamlit as st
import json

# Set the page title and look
st.set_page_config(page_title="Grover Podcast Intel", layout="wide")

# Function to load the data created by your sync script
def load_data():
    try:
        with open('app_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

data = load_data()

st.title("🎙️ Grover Podcast Intelligence")
st.write("Professional summaries and key insights from the latest transcripts.")

# 1. Search Bar
search_query = st.text_input("🔍 Search within summaries...", placeholder="Type a company, topic, or keyword...")

# 2. Filter by Pillar (The list we discussed)
pillars = ["AI", "Cybersecurity", "Management", "Consulting", "Global Trade", "US", "China", "Europe", "Politics", "General Tech", "Finance", "Strategy", "Health", "Career", "Coaching", "History", "[Other]"]
selected_pillar = st.pills("Filter by Topic Pillar", pillars, selection_mode="single")

# 3. Logic to filter results
filtered_data = data

if selected_pillar:
    filtered_data = [d for d in filtered_data if selected_pillar in d.get('keys', [])]

if search_query:
    filtered_data = [
        d for d in filtered_data 
        if search_query.lower() in d.get('summary', "").lower() 
        or search_query.lower() in d.get('file', "").lower()
    ]

# 4. Displaying the Results
st.divider()
st.subheader(f"Showing {len(filtered_data)} Podcasts")

for ep in filtered_data:
    # Creating an expandable box for each podcast
    with st.expander(f"📅 {ep.get('date', 'N/A')} | {ep.get('file', 'Unknown File')}"):
        st.markdown(f"**Keywords:** {', '.join(ep.get('keys', []))}")
        st.info(ep.get('summary', "No summary available."))
        
        # This button allows colleagues to "tick" for more info
        if st.button("Request Deep Dive", key=ep.get('file')):
            st.success("Your request has been logged. It will be processed in the next daily sync.")