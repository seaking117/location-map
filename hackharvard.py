import requests
import pandas as pd
import json

scenic_category_ids = [
    '16000',  # Landmarks and outdoors
    '10027',   #Museums
]

API_KEY = 'fsq39XrHLq7W0By5/YxGYRDkoLqULJ4O0aUgviDv+7vmwqE='


def calculate_bounding_box(lat1, lon1, lat2, lon2):
    ne_lat = max(lat1, lat2)
    ne_lon = max(lon1, lon2)
    sw_lat = min(lat1, lat2)
    sw_lon = min(lon1, lon2)
    return ne_lat, ne_lon, sw_lat, sw_lon


keywords = [
    'landmark',
    'monument',
    'tourist attraction',
    'scenic',
    'sightseeing',
    'historic site',
    'point of interest',
    'museum',
    'park',
    'garden',
    'art gallery',
    'heritage site',
    'waterfront',
    'trail'
]

def get_scenic_places(ne_lat, ne_lon, sw_lat, sw_lon, query='', limit=50):
    url = 'https://api.foursquare.com/v3/places/search'
    headers = {
        'Accept': 'application/json',
        'Authorization': API_KEY,
    }
    params = {
        'query': query,
        'ne': f'{ne_lat},{ne_lon}',
        'sw': f'{sw_lat},{sw_lon}',
        #'categories': ','.join(categories) if categories else None,
        'limit': limit,  # Maximum is 50 per request
        "open_now": True,
        'sort': 'DISTANCE' #distance is measured in meters
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return data



def assign_scenic_scores(df):
    def score_by_keyword(keyword):
        high_value_keywords = ['landmark', 'monument', 'scenic', 'park', 'garden','tourist attraction', 'waterfront']
        mid_value_keywords = ['sightseeing','historic site', 'museum']
        if keyword in high_value_keywords:
            return 2  # Higher score
        elif keyword in mid_value_keywords:
            return 1  # Normal score
        else:
            return 0.5 #low score

    df['Scenic Score'] = df['Keyword'].apply(score_by_keyword)
    return df



#museum of the city of ny to the battery
start_lat= 40.7925
start_lon = -73.9519
end_lat= 40.7029
end_lon = -74.0154

ne_lat, ne_lon, sw_lat, sw_lon = calculate_bounding_box(start_lat, start_lon, end_lat, end_lon)

# Initialize an empty list to hold all places
all_places = []

# Loop over each keyword
for keyword in keywords:
    print(f"Searching for keyword: {keyword}")
    scenic_places = get_scenic_places(
        ne_lat=ne_lat,
        ne_lon=ne_lon,
        sw_lat=sw_lat,
        sw_lon=sw_lon,
        query = keyword,
        limit=50
    )
    
    if scenic_places:
        results = scenic_places.get('results', [])
        print(f"Number of places found for '{keyword}': {len(results)}\n")
        
        for place in results:
            place_info = {
                'Name': place.get('name'),
                'Latitude': place['geocodes']['main']['latitude'],
                'Longitude': place['geocodes']['main']['longitude'],
                # 'Category': ', '.join([category['name'] for category in place.get('categories', [])]),
                # 'Category ID': ', '.join([str(category['id']) for category in place.get('categories', [])]),
                # 'Address': place.get('location', {}).get('formatted_address', 'Address not available'),
                'Distance': place.get('distance'),
                'Keyword': keyword,  # Keep track of which keyword returned this place
                'fsq_id': place.get('fsq_id'),  # Unique identifier for deduplication
            }
            all_places.append(place_info)
    else:
        print(f"No data received for keyword: {keyword}")

# Remove duplicates based on 'fsq_id'
unique_places = {place['fsq_id']: place for place in all_places}
places_list = list(unique_places.values())

print(f"Total unique places found: {len(places_list)}\n")

# Convert to DataFrame
df = pd.DataFrame(places_list)

# Optionally, reset the index
df.reset_index(drop=True, inplace=True)

# Display the DataFrame
assign_scenic_scores(df)
print(df)









