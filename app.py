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


def generate_gpt_response(destination):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Please provide the lat long for the center of {destination} in a basic string of lat,long",
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7,
    )

    return response["choices"][0]["message"]["content"].strip()


def generate_gpt_itinerary(tripadvisor_data):
    response = openai.ChatCompletion.create(
        model="gpt-4",
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
        max_tokens=2500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    #print(response["choices"][0]["message"]["content"].strip())
    
    return response["choices"][0]["message"]["content"].strip()



def extract_itinerary_locations(itinerary):
    response = openai.ChatCompletion.create(
        model="gpt-4",
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
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    #print(response["choices"][0]["message"]["content"].strip())
    locations = response["choices"][0]["message"]["content"].strip()
    split_locations = locations.split("\n")
    #print(split_locations)
    return split_locations



def parse_coordinates(coords_string):
    coords = [tuple(map(float, line.split(','))) for line in coords_string.split('\n')]
    return coords  



def get_points_of_interest(api_key, latlong):

    url = f"https://api.content.tripadvisor.com/api/v1/location/nearby_search?radius=2&radiusUnit=km&latLong={latlong}&category=attractions&language=en&key={api_key}"
    print(url)
    headers = {"accept": "application/json"}
    print(headers)
    response = requests.get(url, headers=headers)
    print(response.content)
    data = response.json()
    print(data)
    poi = [item['location_id'] for item in data['data']]
    print('POI:')
    print(poi)
    return poi



def get_accommodations(api_key, latlong):
    url = f"https://api.content.tripadvisor.com/api/v1/location/nearby_search?radius=2&radiusUnit=km&latLong={latlong}&category=restaurants&language=en&key={api_key}"
    #print(url)
    response = requests.get(url)
    data = response.json()
    #print(data)
    accommodations = [item['location_id'] for item in data['data']]
    print('accommodations:')
    print(accommodations)
    return accommodations


def get_restaurants(api_key, latlong):
    url = f"https://api.content.tripadvisor.com/api/v1/location/nearby_search?radius=2&radiusUnit=km&latLong={latlong}&category=hotels&language=en&key={api_key}" 
    #print(url)   
    response = requests.get(url)
    data = response.json()
    #print(data)
    restaurants =  [item['location_id'] for item in data['data']]
    print('Restaurants:')
    print(restaurants)

    return restaurants    


def get_location_details(location_id):
    #time.sleep(2)
    details_url = f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/details?language=en&currency=USD&key={api_key}"
    headers = {"accept": "application/json"}
    details_response = requests.get(details_url, headers=headers)
    #print(details_response)
    details_data = json.loads(details_response.text)
    #print(details_data)
    return details_data



def generate_coordinates(latitude, longitude, distance, bearing):
    earth_radius_km = 6371

    lat1 = math.radians(latitude)
    lon1 = math.radians(longitude)

    angular_distance = distance / earth_radius_km
    bearing = math.radians(bearing)

    lat2 = math.asin(math.sin(lat1) * math.cos(angular_distance) +
                     math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing))

    lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(angular_distance) * math.cos(lat1),
                             math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2))

    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)

    return lat2, lon2


def generate_concentric_circles(city_latitude, city_longitude, num_circles, num_points_per_circle, circle_distance_km):
    coordinates = []

    for i in range(num_circles):
        distance = (i + 1) * circle_distance_km

        for j in range(num_points_per_circle):
            bearing = 360 / num_points_per_circle * j
            lat, lon = generate_coordinates(city_latitude, city_longitude, distance, bearing)
            lat_long_pair = f"{lat},{lon}"
            coordinates.append(lat_long_pair)

    return coordinates




def parse_tripadvisor_data(location_ids, category, api_key):
    parsed_data = []

    for location_id in location_ids:
        location_details = get_location_details(api_key, location_id)

        parsed_data.append({
            "Category": category,
            "Name": location_details["name"],
            "Latitude": location_details["latitude"],
            "Longitude": location_details["longitude"],
            "Address": location_details["address"],
            "Phone": location_details["phone"],
            "Website": location_details["website"],
            "Hours": ", ".join(location_details["hours"]),
            "Rating": location_details["rating"],
            "Num Reviews": location_details["num_reviews"],
            "Cuisines": ", ".join(location_details["cuisines"]),
        })

    return parsed_data


def get_location_details(api_key, location_id):
    url = f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/details?language=en&currency=USD&key={api_key}"
    response = requests.get(url)
    data = response.json()

    name = data.get("name")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    address = data.get("address_obj", {}).get("address_string")
    phone = data.get("phone")
    website = data.get("website")
    rating = data.get("rating")
    num_reviews = data.get("num_reviews")

    hours = data.get("hours", {}).get("weekday_text", [])

    cuisines = []
    if "cuisine" in data:
        for cuisine in data["cuisine"]:
            cuisines.append(cuisine.get("localized_name"))

    return {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "address": address,
        "phone": phone,
        "website": website,
        "hours": hours,
        "rating": rating,
        "num_reviews": num_reviews,
        "cuisines": cuisines
    }





def get_data_for_latlong_pairs(api_key, latlong_pairs):
    all_data = []
    unique_location_ids = set()
    
    progress_bar = st.progress(0)  # Initialize progress bar
    total_pairs = len(latlong_pairs)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        api_key_lat_lng_list = [(api_key, lat_lng) for lat_lng in latlong_pairs]
        results = list(executor.map(lambda args: fetch_tripadvisor_data(*args), api_key_lat_lng_list))

    for idx, (lat_lng, (points_of_interest, restaurants, accommodations)) in enumerate(zip(latlong_pairs, results)):
        #print(lat_lng)

        unique_points_of_interest = [location_id for location_id in points_of_interest if location_id not in unique_location_ids]
        unique_location_ids.update(unique_points_of_interest)
        unique_restaurants = [location_id for location_id in restaurants if location_id not in unique_location_ids]
        unique_location_ids.update(unique_restaurants)
        unique_accommodations = [location_id for location_id in accommodations if location_id not in unique_location_ids]
        unique_location_ids.update(unique_accommodations)

        all_data.extend(parse_tripadvisor_data(unique_points_of_interest, 'Point of Interest', api_key))
        all_data.extend(parse_tripadvisor_data(unique_restaurants, 'Restaurant', api_key))
        all_data.extend(parse_tripadvisor_data(unique_accommodations, 'Accommodation', api_key))
        #print(all_data)
        progress = (idx + 1) / total_pairs  # Calculate progress
        progress_bar.progress(progress)  # Update progress bar

    df = pd.DataFrame(all_data)
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
            text_instructions = html.unescape(step['html_instructions'])
            st.markdown(f"**Step {i + 1}:** {text_instructions}")




def create_map(lat_lng_list):
    df = pd.DataFrame(lat_lng_list, columns=['lat', 'lon'])
    st.map(df)



def fetch_tripadvisor_data(api_key, lat_lng):
    points_of_interest = get_points_of_interest(api_key, lat_lng)
    restaurants = get_restaurants(api_key, lat_lng)
    accommodations = get_accommodations(api_key, lat_lng)

    return points_of_interest, restaurants, accommodations







if st.button("Generate Itinerary"):
    user_preferences = get_user_preferences()
    lat_lng = get_geocoded_location(destination)
    #print(lat_lng)
    city_latitude, city_longitude = lat_lng
    num_circles = 3
    num_points_per_circle = 10
    circle_distance_km = 2

    coordinates = generate_concentric_circles(city_latitude, city_longitude, num_circles, num_points_per_circle, circle_distance_km)
    #print(coordinates)
    tripadivsordf = get_data_for_latlong_pairs(your_tripadvisor_api_key, coordinates)
    tripadivsordf = tripadivsordf.drop_duplicates(subset="Address")

    locations = generate_gpt_itinerary(tripadivsordf[['Name','Address', 'Rating', 'Num Reviews']])
    gpt_itinerary = generate_gpt_itinerary(locations)
    st.markdown(gpt_itinerary)
    locationsresponse = extract_itinerary_locations(gpt_itinerary)

    lat_lng_list = get_geocoded_locations(locationsresponse)

    directions_result = get_directions_result(lat_lng_list)

    st.subheader("Itinerary Directions")
    # Call the display_itinerary_directions function with directions_result
    display_itinerary_directions(directions_result)

    st.subheader("Map")
    # Convert the list of lat/long tuples into a DataFrame
    df = pd.DataFrame(lat_lng_list, columns=['lat', 'lon'])

    # Display the DataFrame as a map
    create_map(lat_lng_list)





  
  
  
  
  
  
  


    
