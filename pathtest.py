import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt

G = ox.graph_from_place('Manhattan, New York, USA', network_type='walk')

start_lat, start_lon = 40.785091, -73.968285
end_lat, end_lon = 40.758896, -73.985130

start_node = ox.distance.nearest_nodes(G, start_lon, start_lat)
end_node = ox.distance.nearest_nodes(G, end_lon, end_lat)

shortest_path = nx.shortest_path(G, start_node, end_node, weight='length')

SPG = nx.MultiDiGraph()
shortEdges = []

for node in shortest_path:
    SPG.add_node(node, **G.nodes[node])

for i in range(len(shortest_path) - 1):
    u, v = shortest_path[i], shortest_path[i+1]
    if G.has_edge(u, v):
        edge_data = G.get_edge_data(u, v)
        for key, attr_dict in edge_data.items():
            SPG.add_edge(u, v, key=key, **attr_dict)


SPG.graph['crs'] = G.graph['crs']
shortest_path_length = nx.shortest_path_length(G, start_node, end_node, weight='None')

route_nodes, route_edges = ox.graph_to_gdfs(SPG, nodes=True, edges=True)
nyc_nodes, nyc_edges = ox.graph_to_gdfs(G, nodes = True, edges = True, node_geometry=True, fill_edge_geometry=True)
#print(shortest_path_length)
fig, ax = plt.subplots() 

route_edges.plot(ax=ax,linewidth = 0.5, edgecolor = 'red')

nyc_nodes.plot(ax=ax, color='blue', markersize=5)
route_nodes.plot(ax=ax, color = 'red', markersize=5)

# Display the plot
plt.show()


