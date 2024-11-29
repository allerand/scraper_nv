#utils/google_maps.py

from serpapi import GoogleSearch
import requests
import config

def search_google_maps(post_code, coordinates, query, api_key=config.API_KEY, num_results=10):
    ll_format = f"@{coordinates['lat']},{coordinates['lng']},15z"
    params = {
        "engine": "google_maps",
        "q": query,
        "ll": ll_format,
        "type": "search",
        "api_key": api_key,
        "num": num_results
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    local_results = results.get("local_results", [])
    data = []
    for local_result in local_results:
        name = local_result.get('title', 'N/A')
        link = local_result.get('website', 'N/A')
        location = local_result.get('address', 'N/A')
        phone = local_result.get('phone', 'N/A')
        data.append([post_code, location, name, phone, link])
    return data

def get_serpapi_location(query):
    url = "https://serpapi.com/locations.json"
    params = {
        "q": query,
        "limit": 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data:
        location_data = data[0]
        gps_coordinates = location_data.get("gps", [None, None])
        return {
            "lat": gps_coordinates[1],
            "lng": gps_coordinates[0]
        }
    else:
        return None
