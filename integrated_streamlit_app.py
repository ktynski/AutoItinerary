import streamlit as st
import os
from run import get_location_details, generate_coordinates, generate_concentric_circles, parse_tripadvisor_data, get_data_for_latlong_pairs, generate_gpt_itinerary, extract_itinerary_locations

st.title('AutoItinerary')

# User input elements
destination = st.text_input('Enter your destination:')
user_preferences = {'destination': destination}

your_tripadvisor_api_key = os.environ['your_tripadvisor_api_key']


def main(user_preferences, your_tripadvisor_api_key):
    # Refactor the AutoItinerary code to work with the Streamlit UI elements just created.
    # Ensure that user_preferences and your_tripadvisor_api_key variables are passed as arguments to the main function.
    # TODO: Reuse AutoItinerary functions here and display result using Streamlit elements.
    pass

if st.button('Generate Itinerary') and destination and your_tripadvisor_api_key:
    main(user_preferences, your_tripadvisor_api_key)
