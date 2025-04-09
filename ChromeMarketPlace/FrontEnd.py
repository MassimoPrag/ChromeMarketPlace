import streamlit as st
import pandas as pd
from SCRAPERS.makeOneCsv import makeOneDF
import base64
import os
from streamlit_chat import message


# Optional email drop
st.sidebar.header("Optional Email Drop")
email = st.sidebar.text_input("Enter your email (optional)")
if st.sidebar.button("Submit Email"):
    if email:
        with open("emails.txt", "a") as f:
            f.write(email + "\n")
        st.sidebar.success("Email submitted successfully!")

st.title("Chrome Hearts Ledger")
st.write("This is a ledger of all Chrome Hearts items scraped from various websites.")
st.write("Search for any and all items in the search bar below and get exactly where they are available.")

# Load the dataframe once and store it in session state
if 'df' not in st.session_state:
    st.session_state.df = makeOneDF()

df = st.session_state.df

# Load forum messages from file
if 'messages' not in st.session_state:
    if os.path.exists("forum_messages.txt"):
        with open("forum_messages.txt", "r") as f:
            st.session_state.messages = f.read().splitlines()
    else:
        st.session_state.messages = []

# Load submitted websites from file
if 'websites' not in st.session_state:
    if os.path.exists("submitted_websites.txt"):
        with open("submitted_websites.txt", "r") as f:
            st.session_state.websites = f.read().splitlines()
    else:
        st.session_state.websites = []

# Initialize session state for chat
if 'past' not in st.session_state:
    st.session_state.past = []

# Create tabs
tab1, tab2, tab3 = st.tabs(["Ledger", "Forum", "Submit Website"])

with tab1:
    search_term = st.text_input("Search for items")

    if search_term:
        filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
    else:
        filtered_df = df

     # Convert the 'Link' column to clickable links
    def make_clickable(link):
        return f'<a href="{link}" target="_blank">{link}</a>'

    filtered_df['Link'] = filtered_df['Link'].apply(make_clickable)

    # Display the dataframe with clickable links
    st.markdown(filtered_df.to_html(escape=False, index=False), unsafe_allow_html=True)

with tab2:
    st.header("Forum")
    
    def on_input_change():
        user_input = st.session_state.user_input
        st.session_state.past.append(user_input)
        st.session_state.messages.append(user_input)
        with open("forum_messages.txt", "a") as f:
            f.write(user_input + "\n")

    st.session_state.setdefault(
        'past', 
        ['plan text with line break',
        'play the song "Dancing Vegetables"', 
        'show me image of cat', 
        'and video of it',
        'show me some markdown sample',
        'table in markdown']
    )

    chat_placeholder = st.empty()

    with chat_placeholder.container():    
        for i in range(len(st.session_state['past'])):                
            message(st.session_state['past'][i], is_user=True, key=f"{i}_user")

    with st.container():
        st.text_input("Send Message:", on_change=on_input_change, key="user_input")     

with tab3:
    st.header("Submit Website for Scraping")
    
    # Input for website URL
    website_url = st.text_input("Website URL")
    additional_info = st.text_area("Additional Information (optional)")

    if st.button("Submit Website"):
        if website_url:
            # Save the submitted website URL and additional information
            with open("submitted_websites.txt", "a") as f:
                f.write(f"Website URL: {website_url}\n")
                if additional_info:
                    f.write(f"Additional Information: {additional_info}\n")
                f.write("\n")
            st.session_state.websites.append(website_url)
            st.success("Website submitted successfully!")
        else:
            st.error("Please enter a website URL.")

    # Display submitted websites
    st.subheader("Submitted Websites")
    if st.session_state.websites:
        for website in st.session_state.websites:
            st.write(website)
    else:
        st.write("No websites submitted yet.")
