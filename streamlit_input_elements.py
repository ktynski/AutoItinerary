import streamlit as st

st.title('AutoItinerary')

# User input elements
destination = st.text_input('Enter your destination:')
user_preferences = {'destination': destination}

your_tripadvisor_api_key = st.text_input('Enter your TripAdvisor API key: (This should be kept secret)')

if st.button('Generate Itinerary') and destination and your_tripadvisor_api_key:
    # Call the main function here to generate the itinerary
    # Refactor the main function to take user_preferences and your_tripadvisor_api_key as input
    pass