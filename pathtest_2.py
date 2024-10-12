import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import json
import os
import hackharvard as hh 

API_KEY = 'fsq39XrHLq7W0By5/YxGYRDkoLqULJ4O0aUgviDv+7vmwqE='


# Function to get coordinates of a location using Foursquare API (optional, may not be used if direct lat/lon inputs)
def get_coords(location, limit=1):
    url = "https://api.foursquare.com/v3/places/search"
    headers = {
        "Accept": "application/json",
        "Authorization": API_KEY
    }
    params = {
        "query": location,
        "limit": limit
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return None

    if data.get("results"):
        first_result = data["results"][0]
        geocodes = first_result.get("geocodes", {})
        main_geo = geocodes.get("main", {})
        latitude = main_geo.get("latitude")
        longitude = main_geo.get("longitude")

        if latitude and longitude:
            return (latitude, longitude)
        else:
            print("Geocoding failed: Coordinates not found.")
            return None
    else:
        print("No results found.")
        return None


# Function to take latitude and longitude input directly
def get_location():
    try:
        start_lat = float(input("Enter starting latitude: "))
        start_lon = float(input("Enter starting longitude: "))
        end_lat = float(input("Enter destination latitude: "))
        end_lon = float(input("Enter destination longitude: "))
    except ValueError:
        print("Invalid input. Please enter numeric values for latitude and longitude.")
        return None
    
    return start_lat, start_lon, end_lat, end_lon


# Main function to create the path based on latitude and longitude
def create_path():
    # Load the graph for Manhattan walking paths
    try:
        G = ox.graph_from_place('Manhattan, New York, USA', network_type='walk')
    except Exception as e:
        print(f"Error loading graph: {e}")
        return

    # Get start and end coordinates
    location = get_location()
    if not location:
        print("Exiting due to previous errors.")
        return

    start_lat, start_lon, end_lat, end_lon = location
    setLimit = 5

    # Determine direction of movement
    up = False
    right = False
    if (end_lat - start_lat > 0):
        right = True
    if (end_lon - start_lon > 0):
        up = True

    # Fetch places along the route using the hackharvard library
    df = hh.returnList(start_lat, start_lon, end_lat, end_lon, setLimit)

    start_node = ox.distance.nearest_nodes(G, start_lon, start_lat)
    end_node = ox.distance.nearest_nodes(G, end_lon, end_lat)

    curr_lat = G.nodes[start_node]['y']
    curr_lon = G.nodes[start_node]['x']

    nodes = []
    for i in range(len(df)):  
        lat = df.iloc[i]['Latitude']
        lon = df.iloc[i]['Longitude']
        if ((right and lon > curr_lon) or (not right and lon < curr_lon)) and \
           ((up and lat > curr_lat) or (not up and lat < curr_lat)):
            node = ox.distance.nearest_nodes(G, lon, lat)
            nodes.append(node)
            curr_lon = lon
            curr_lat = lat

    # Create the full route
    full_route = []
    full_route_nodes = [start_node] + nodes + [end_node]
    for i in range(len(full_route_nodes) - 1):
        shortest_path_segment = nx.shortest_path(G, full_route_nodes[i], full_route_nodes[i + 1], weight='length')
        full_route.extend(shortest_path_segment[:-1])

    full_route.append(full_route_nodes[-1])

    SPG = G.subgraph(full_route).copy()

    # Convert the subgraph to GeoDataFrames
    try:
        route_nodes, route_edges = ox.graph_to_gdfs(SPG, nodes=True, edges=True)
    except Exception as e:
        print(f"Error converting graph to GeoDataFrames: {e}")
        return

    # Combine all geometries into a single LineString or MultiLineString
    combined = route_edges.unary_union
    print("Combined geometry type:", combined.type)

    # Create GeoJSON Feature
    if combined.type == 'LineString':
        geometry = combined.__geo_interface__
    elif combined.type == 'MultiLineString':
        geometry = combined.__geo_interface__
    else:
        raise ValueError(f"Unsupported geometry type: {combined.type}")

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Scenic Route"
                },
                "geometry": geometry
            }
        ]
    }

    # Save to a GeoJSON file
    try:
        with open('route.geojson', 'w') as f:
            json.dump(geojson, f, indent=4)
        print("route.geojson has been written successfully.")
    except Exception as e:
        print("Error writing route.geojson:", e)

    # Plot the route
    fig, ax = plt.subplots()
    route_edges.plot(ax=ax, linewidth=2, edgecolor='red')
    plt.show()


# Main entry point of the script
if __name__ == "__main__":
    print("=== Path Creator Script Started ===\n") 
    create_path()
    print("\n=== Path Creator Script Completed ===")
