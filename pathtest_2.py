import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import os

print("Script started.")

G = ox.graph_from_place('Manhattan, New York, USA', network_type='walk')

start_lat, start_lon = 40.785091, -73.968285
end_lat, end_lon = 40.758896, -73.985130

start_node = ox.distance.nearest_nodes(G, start_lon, start_lat)
end_node = ox.distance.nearest_nodes(G, end_lon, end_lat)

shortest_path = nx.shortest_path(G, start_node, end_node, weight='length')

SPG = G.subgraph(shortest_path).copy()

route_nodes, route_edges = ox.graph_to_gdfs(SPG, nodes=True, edges=True)

print("Number of route edges:", len(route_edges))
if len(route_edges) == 0:
    print("route_edges is empty.")

print("Initial CRS of route_edges:", route_edges.crs)

if route_edges.crs is None:
    route_edges.crs = G.graph['crs']
    print("Assigned CRS to route_edges:", route_edges.crs)

route_edges = route_edges.to_crs(epsg=4326)
print("Reprojected to WGS84.")

combined = route_edges.unary_union
print("Combined geometry type:", combined.type)

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

try:
    with open('route.geojson', 'w') as f:
        json.dump(geojson, f, indent=4)
    print("route.geojson has been written successfully.")
except Exception as e:
    print("Error writing route.geojson:", e)

try:
    with open('test.txt', 'w') as f:
        f.write("Test file.")
    print("test.txt has been written successfully.")
except Exception as e:
    print("Error writing test.txt:", e)

print("Current working directory:", os.getcwd())

fig, ax = plt.subplots()
route_edges.plot(ax=ax, linewidth=2, edgecolor='red')
plt.show()

print("Script completed.")
