import pandas as pd
import googlemaps
import gmaps
import streamlit as st
import time
import math
import openai
import datetime
import requests
import json
import pandas as pd
import googlemaps
import gmaps
import os
from dotenv import load_dotenv
import numpy as np
import html2text
import concurrent.futures
import html
from transformers import GPT2Tokenizer



# Load environment variables from .env file
load_dotenv()
print("wtf")
st.title("Trip Planner")

destination = st.text_input("Enter your destination:")

def get_current_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        ip = response.json()["ip"]
        return ip
    except:
        st.warning("Unable to fetch current IP address.")
        return None

current_ip = get_current_ip()
if current_ip:
    st.write(f"Current IP address: {current_ip}")

gmaps_client = googlemaps.Client(key=os.environ['gmaps_api_key'])
gmaps_api_key = os.environ['gmaps_api_key']
# Create a client for the googlemaps library
gmaps_client = googlemaps.Client(key=gmaps_api_key)
# Configure the gmaps library with the API key
gmaps.configure(api_key=gmaps_api_key)
openai.api_key = os.environ['openai_api_key']
your_tripadvisor_api_key = os.environ['your_tripadvisor_api_key']
eventbrite_api_key = os.environ['eventbrite_api_key']


def get_user_preferences():
    destination = "Ithaca ny"
    start_date = "2023-11-24"
    end_date = "2023-11-24"
    interests = "Hiking"
    budget = "5000"
    transportation_mode = "driving"

    preferences = {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "interests": [interest.strip() for interest in interests.split(",")],
        "budget": budget,
        "transportation_mode": transportation_mode,
    }

    return preferences



def generate_gpt_itinerary(tripadvisor_data):
    res_box = st.empty()
    delay_time = 0.01 # faster
    max_response_length = 8000
    answer = ''
    full_answer = '' # Variable to store the entire content
    start_time = time.time()
            
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                    {
                        "role": "system",
                        "content": """ Based on a dataset relevant travel guide data provided at the end please plan an itinerary that follows this format to create a 3 day itinerary using beatiful markdown with clear hierarchy and easy to read with flourishes. Simulate a world renowned travel guide author and  an expert on the given location.
                        Please follow the template generally, but feel free to improve on it as long as it is consistent throughout in terms of formatting and thoroughness. Be as detailed as possible to make it as useful and engaging and convincing as possible that the itinerary will create a memorable and enjoyable experience: \n
                        Each day should have plans for breakfast, lunch, dinner, do not ask the user to choose for any of the days or activities, you need to suggest all.
                        
                        Intro: Provide an enticing title for the itinerary that includes the location
                        Day: {day_number} (should have a theme):

                        Morning:
                        - Visit {point_of_interest_1_name} at {point_of_interest_1_address}
                          {point_of_interest_1_website} (Rating: {point_of_interest_1_rating}, {point_of_interest_1_num_reviews} reviews)

                        - Grab breakfast at {restaurant_1_name} at {restaurant_1_address}
                          {restaurant_1_website} (Rating: {restaurant_1_rating}, {restaurant_1_num_reviews} reviews)
                          Cuisines: {restaurant_1_cuisines}
                          Hours: {restaurant_1_hours}
                          
                          Tips: {tips for this segment} should be in blockquote markdown

                        Afternoon:
                        - Visit {point_of_interest_2_name} at {point_of_interest_2_address}
                          {point_of_interest_2_website} (Rating: {point_of_interest_2_rating}, {point_of_interest_2_num_reviews} reviews)

                        - Have lunch at {restaurant_2_name} at {restaurant_2_address}
                          {restaurant_2_website} (Rating: {restaurant_2_rating}, {restaurant_2_num_reviews} reviews)
                          Cuisines: {restaurant_2_cuisines}
                          Hours: {restaurant_2_hours}
                          
                          Tips: {tips for this segment} should be in blockquote markdown
                          
                        Evening:
                        - Visit {point_of_interest_3_name} at {point_of_interest_3_address}
                          {point_of_interest_3_website} (Rating: {point_of_interest_3_rating}, {point_of_interest_3_num_reviews} reviews)

                        - Enjoy dinner at {restaurant_3_name} at {restaurant_3_address}
                          {restaurant_3_website} (Rating: {restaurant_3_rating}, {restaurant_3_num_reviews} reviews)
                          Cuisines: {restaurant_3_cuisines}
                          Hours: {restaurant_3_hours}
                          
                          Tips: {tips for this segment} should be in blockquote markdown

                        Then go on to the next 2 days of the itinerary and finish with a useful conclusion.
                          """
                    },
                    {
                        "role": "user",
                        "content": f"Use streamlit's markdown format ex: st.markdown(generated content) in order to properly format it. Use readability and design best practices, but make it fun and eye catching. Include links to websites and/or phone numbers. Use various styling options to create an attractive and visually appealing text output. Consider using headings, bold, italics, lists, blockquotes, code snippets, tables, links, and any other relevant Markdown elements to showcase a wide range of styling possibilities. Data to use to build itinerary: \n ### \n {tripadvisor_data} \n ### Itinerary: \n "
                    }
                ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7,
        stream = True
    )
    for event in response:
        # RETRIEVE THE TEXT FROM THE RESPONSE
        event_time = time.time() - start_time  # CALCULATE TIME DELAY BY THE EVENT
        event_text = event['choices'][0]['delta'] # EVENT DELTA RESPONSE
        answer = event_text.get('content', '') # RETRIEVE CONTENT
        
        # Concatenate the new content to the existing content
        full_answer += answer
        
        # Update the markdown display with the entire content
        res_box.markdown(full_answer, unsafe_allow_html=True)
        
        time.sleep(delay_time)
    
    
    
    return full_answer



def extract_itinerary_locations(itinerary):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                    {
                        "role": "system",
                        "content": """ Every day should be fully planned, and not left up to the user. Based on the following itinerary, please extract an unnumbered list of names + locations (each as a string) in the order in which they are found in the itinerary: \n

                          """
                    },
                    {
                    "role": "user",
                    "content": f''' Itinerary to use to extract the list in order in which they appear in the itinerary each one on a new line. Here is an example of a correctly formatted output:
                                        ###
                                        "Establishment/Place/location, City, State",
                                        "Establishment/Place/location, City, State",
                                        "Establishment/Place/location, City, State",
                                        "Establishment/Place/location, City, State",
                                        "Establishment/Place/location, City, State",
                                        "Establishment/Place/location, City, State",
                                        "Establishment/Place/location, City, State",
                                        "Establishment/Place/location, City, State",
                                        "Establishment/Place/location, City, State",
                                        "Establishment/Place/location, City, State",
                                         etc. etc. etc. for the rest of the locations from the itinerary.
                                        ###

                                        Now please construct a similarly formatted list of locations in the order you see them
                                        ### {itinerary} ### Locations List: \n'''
                }
                ],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    #print(response["choices"][0]["message"]["content"].strip())
    locations = response["choices"][0]["message"]["content"].strip()
    split_locations = locations.split("\n")
    #print(split_locations)
    return split_locations



def get_places_df(location, radius, place_type, api_key):
    """
    Get a DataFrame of places from a location using the Google Maps Places API.

    Args:
        location (tuple): A tuple containing the latitude and longitude of the location.
        radius (int): The radius (in meters) within which to search for places.
        place_type (str): The type of place to search for (e.g. 'restaurant', 'hotel', etc.).
        api_key (str, optional): Your Google Maps API key. Defaults to API_KEY.

    Returns:
        pd.DataFrame: A DataFrame containing information about the nearby places.
    """

    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    place_data = []
    next_page_token = None

    while True:
        params = {
            "location": f"{location[0]},{location[1]}",
            "radius": radius,
            "type": place_type,
            "key": api_key
        }

        if next_page_token:
            params["pagetoken"] = next_page_token

        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] == "OK":
            places = data["results"]

            for place in places:
                place_data.append({
                    "name": place["name"],
                    "place_type": place_type,
                    "address": place["vicinity"],
                    "latitude": place["geometry"]["location"]["lat"],
                    "longitude": place["geometry"]["location"]["lng"],
                    "place_id": place["place_id"],
                    "rating": place.get("rating", None),
                    "user_ratings_total": place.get("user_ratings_total", None),
                })

            # Check if there is a next page token
            next_page_token = data.get("next_page_token", None)

            if not next_page_token:
                break

            # Wait for the token to become valid
            time.sleep(1)

        else:
            print(f"Error: {data['status']}")
            break

    places_df = pd.DataFrame(place_data)
    return places_df



def get_places_df_multiple_types(location, radius, place_types, api_key):
    """
    Get a DataFrame of places from a location with multiple place types using the Google Maps Places API.

    Args:
        location (tuple): A tuple containing the latitude and longitude of the location.
        radius (int): The radius (in meters) within which to search for places.
        place_types (list): A list of place types to search for (e.g. ['restaurant', 'hotel', 'park']).
        api_key (str, optional): Your Google Maps API key. Defaults to API_KEY.

    Returns:
        pd.DataFrame: A DataFrame containing information about the nearby places.
    """

    all_places_df = pd.DataFrame()

    for place_type in place_types:
        places_df = get_places_df(location, radius, place_type, api_key)
        all_places_df = pd.concat([all_places_df, places_df], ignore_index=True)

    return all_places_df





def add_photo_references(df, api_key):
    """
    Add photo references to the DataFrame using the Google Maps Places API.

    Args:
        df (pd.DataFrame): A DataFrame containing places information.
        api_key (str): Your Google Maps API key.

    Returns:
        pd.DataFrame: A DataFrame containing places information with an additional column for photo references.
    """

def get_place_photo_references(place_id):
    place_details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "photo",
        "fields": "website",
        "fields": "current_opening_hours",
        "key": api_key
    }

    response = requests.get(place_details_url, params=params)
    data = response.json()
    print(data)

    if data["status"] == "OK":
        place_details = data["result"]

        if "photos" in place_details:
            return [photo["photo_reference"] for photo in place_details["photos"]]

        return []

    df["photo_references"] = df["place_id"].apply(get_place_photo_references)
    return df



  



def get_geocoded_location(destination):
    geocoded_location = gmaps_client.geocode(destination)
    latitude = geocoded_location[0]['geometry']['location']['lat']
    longitude = geocoded_location[0]['geometry']['location']['lng']
    lat_lng = (latitude, longitude)
    return lat_lng

def get_geocoded_locations(locations):
    geocoded_locations = [gmaps_client.geocode(location) for location in locations]
    print(geocoded_locations)
    lat_lng_list = []
    for geocoded_location in geocoded_locations:
        latitude = geocoded_location[0]['geometry']['location']['lat']
        longitude = geocoded_location[0]['geometry']['location']['lng']
        lat_lng = (latitude, longitude)
        lat_lng_list.append(lat_lng)
    return lat_lng_list

def get_directions_result(lat_lng_list):
    directions_result = gmaps_client.directions(
        origin=lat_lng_list[0],
        destination=lat_lng_list[-1],
        waypoints=lat_lng_list[1:-1],
        mode='driving'
    )
    return directions_result


def display_itinerary_directions(directions_result):
    legs = directions_result[0]['legs']
    for idx, leg in enumerate(legs):
        st.markdown(f"**Leg {idx + 1}**")
        steps = leg['steps']
        for i, step in enumerate(steps):
            text_instructions = step['html_instructions']
            st.markdown(f"**Step {i + 1}:** {text_instructions}")





def create_map(lat_lng_list):
    df = pd.DataFrame(lat_lng_list, columns=['lat', 'lon'])
    st.map(df)



def truncate_string_to_max_tokens(input_string, max_tokens=1700):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokens = tokenizer.tokenize(input_string)
    
    # Truncate the tokens to a maximum of 2000 tokens
    truncated_string = tokens[:max_tokens]
    
    # Convert the truncated tokens back to a string
    truncated_string = tokenizer.convert_tokens_to_string(truncated_string)
    
    return truncated_string    



    
def main():
    if st.button("Generate Itinerary"):

        progress_bar = st.progress(0)
        progress_weight = {
            "starter": 0.3,
            "generate_gpt_itinerary":0.7,
       
        }

        user_preferences = get_user_preferences()
        lat_lng = get_geocoded_location(destination)
        #print(lat_lng)
        location = (lat_lng)  # Googleplex
        radius = 6000  # 2 km
        place_types = ["restaurant", "lodging", "park", "store", "cafe", "museum", "shopping mall", "stadium", "tourist_attraction", "university", "spa", "campground", "bar"]

        all_places_df = get_places_df_multiple_types(location, radius, place_types, 'AIzaSyD9fMra9YQU28FawZynXgfl7RCVc9UbRxU')
        progress_bar.progress(progress_weight["starter"])
        #all_places_df_with_photos = add_photo_references(all_places_df, API_KEY)
        #print(coordinates)
        
        # Update progress after getting data for latlong pairs
        df_string = all_places_df.to_string()
        truncated_location_string = truncate_string_to_max_tokens(df_string, max_tokens=1700)
        gpt_itinerary = generate_gpt_itinerary(truncated_location_string)
        progress_bar.progress(progress_weight["generate_gpt_itinerary"] + progress_weight["starter"])
        
        #st.markdown(gpt_itinerary)
        locationsresponse = extract_itinerary_locations(gpt_itinerary)

        # Update progress after getting geocoded locations
        #lat_lng_list = get_geocoded_locations(locationsresponse)
        #progress_bar.progress(progress_weight["get_geocoded_locations"] + progress_weight["generate_gpt_itinerary"] + progress_weight["starter"])

        # ... other code here ...

        # Update progress after getting directions result
        #directions_result = get_directions_result(lat_lng_list)
        #progress_bar.progress(progress_weight["get_directions_result"] + progress_weight["get_geocoded_locations"] + progress_weight["generate_gpt_itinerary"] + progress_weight["starter"])

        # ... other code here ...

        # Update progress after displaying itinerary directions
        #st.subheader("Itinerary Directions")
        #display_itinerary_directions(directions_result)
        #progress_bar.progress(progress_weight["display_itinerary_directions"] + progress_weight["get_directions_result"] + progress_weight["get_geocoded_locations"] + progress_weight["generate_gpt_itinerary"] + progress_weight["starter"])

        # ... other code here ...

        # Update progress after creating the map
        #st.subheader("Map")
        #df = pd.DataFrame(lat_lng_list, columns=['lat', 'lon'])
        #create_map(lat_lng_list)
        #progress_bar.progress(1.0)  # Complete progress bar

if __name__ == "__main__":
    main()




  
  
  
  
  
  
  


    
