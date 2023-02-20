import json

import geopandas as gpd
import networkx as nx
import rasterio
from shapely.geometry import LineString


class ShortestPath:

    def __init__(self, road_file, itn, transform, buffer):
        with open(road_file, 'r') as f:
            solent_itn = json.load(f)
        self.__road_links = solent_itn['roadlinks']  # init road links and
        self.__itn = itn  # it finds the nearest nodes
        self.__transform = transform
        self.__buffer = buffer  # 5km buffer around the user

    # Find the shortest path between the location of the user and the highest points(s) using Dijkstra Algorithm,
    # which means finding the path consuming the least time.
    # It applies Naismith’s rule to calculate the walking time.
    def shortest_path(self, elevation_file, user_location, highest_points):
        # find the nearest ITN nodes to the user's location
        print("Finding the nearest ITN nodes to your location...\n")
        nodes_user = self.__itn.nearest_node(user_location)

        # init elevation np array
        elevation_f = rasterio.open(elevation_file)
        elevation = elevation_f.read(1)

        # init a directed road graph and the weight for each road link is the walking time calculated by Naismith’s rule
        graph = nx.DiGraph()  # directed road graph
        for link in self.__road_links:
            road_length = self.__road_links[link]['length']

            # coordinates for the start and end node of the road link
            coord_start = self.__road_links[link]['coords'][0]
            coord_end = self.__road_links[link]['coords'][-1]

            # if the road is not within the buffer and touches the buffer, don't add this road into the graph
            road_line = LineString(self.__road_links[link]['coords'])
            if (not road_line.within(self.__buffer)) and (not road_line.touches(self.__buffer)):
                continue

            # raster location of the coordinates
            raster_start = rasterio.transform.rowcol(self.__transform, coord_start[0], coord_start[1])
            raster_end = rasterio.transform.rowcol(self.__transform, coord_end[0], coord_end[1])

            # elevation of the coordinates
            elevation_start = elevation[raster_start[0]][raster_start[1]]
            elevation_end = elevation[raster_end[0]][raster_end[1]]

            # total walking time = road_length(m) / speed(m/s) + climbing elevation(m) * (60s/10m))
            total_walking_time_normal = road_length / (5000 / 3600)
            total_walking_time_climb = road_length / (5000 / 3600) + abs(elevation_end - elevation_start) * (60 / 10)
            if elevation_start < elevation_end:
                # there is a climbing from start to end
                graph.add_edge(self.__road_links[link]['start'], self.__road_links[link]['end'], fid=link,
                               weight=total_walking_time_climb)
                graph.add_edge(self.__road_links[link]['end'], self.__road_links[link]['start'], fid=link,
                               weight=total_walking_time_normal)
            elif elevation_start > elevation_end:
                # there is a climbing from end to start
                graph.add_edge(self.__road_links[link]['end'], self.__road_links[link]['start'], fid=link,
                               weight=total_walking_time_climb)
                graph.add_edge(self.__road_links[link]['start'], self.__road_links[link]['end'], fid=link,
                               weight=total_walking_time_normal)
            else:
                # add same weight to both direction
                graph.add_edge(self.__road_links[link]['start'], self.__road_links[link]['end'], fid=link,
                               weight=total_walking_time_normal)
                graph.add_edge(self.__road_links[link]['end'], self.__road_links[link]['start'], fid=link,
                               weight=total_walking_time_normal)

        # Find the most feasible path between nodes nearest to the user and nodes to the highest point(s)
        print("Finding shortest path...\n")
        shortest_path = []
        shortest_path_time = float('inf')  # time-consuming for the shortest path
        nodes_user_index = 0  # index of node nearest to the user
        nodes_high_index = 0  # index of node nearest to the highest point
        high_point_index = 0  # index of the highest point
        for h_i, high_point in enumerate(highest_points):
            print("Finding nearest ITN nodes to highest point...\n")
            nodes_high = self.__itn.nearest_node(high_point)
            if len(nodes_high) == 1 and len(nodes_user) == 1:
                # only one node nearest to the user and only one node nearest to the highest point
                try:
                    shortest_path_time_temp = nx.dijkstra_path_length(graph, source=nodes_user[0].object,
                                                                      target=nodes_high[0].object, weight='weight')
                    if shortest_path_time_temp < shortest_path_time:
                        shortest_path_time = shortest_path_time_temp
                        shortest_path = nx.dijkstra_path(graph, source=nodes_user[0].object,
                                                         target=nodes_high[0].object, weight='weight')
                        nodes_user_index = 0
                        nodes_high_index = 0
                        high_point_index = h_i
                except nx.exception.NodeNotFound:
                    print('Road node ', nodes_user[0].object, 'or', nodes_high[0].object,
                          'does not exist in the road graph!\n')
                except nx.exception.NetworkXNoPath:
                    print('No path exist between', nodes_user[0].object, 'and', nodes_high[0].object, '!\n')

            else:
                # more than one node nearest to the user and more than one node nearest to the highest point
                try:
                    for i, start in nodes_user[0:]:
                        for j, end in nodes_high[0:]:
                            shortest_path_time_temp = nx.dijkstra_path_length(graph, source=start.object,
                                                                              target=end.object, weight='weight')
                            if shortest_path_time_temp < shortest_path_time:
                                shortest_path_time = shortest_path_time_temp
                                shortest_path = nx.dijkstra_path(graph, source=start.object, target=end.object,
                                                                 weight='weight')
                                nodes_user_index = i
                                nodes_high_index = j
                                high_point_index = h_i
                except nx.exception.NodeNotFound:
                    print('Road node ', nodes_user[0].object, 'or', nodes_high[0].object,
                          'does not exist in the road graph!\n')
                except nx.exception.NetworkXNoPath:
                    print('No path exist between', nodes_user[0].object, 'and', nodes_high[0].object, '!\n')

        # final nodes in the path
        node_user = nodes_user[nodes_user_index]  # nearest node to the user
        highest_point = highest_points[high_point_index]  # the highest point
        nodes_high = self.__itn.nearest_node(highest_point)
        node_highest = nodes_high[nodes_high_index]  # nearest node to the highest point

        # give msg reminding user that shortest path has been found
        print('Shortest path found! Please have a look at the map.')
        # give msg telling the user how long it will take to get to a safe place
        print('Time consumed by walking to the highest point would be ' + str(round(shortest_path_time/60.0, 2)) + ' mins approximately.\n')

        return node_user, node_highest, highest_point, self.add_geometry(shortest_path, graph)

    # Associate road feature id with geometry
    def add_geometry(self, shortest_path, graph):
        links = []  # this list will be used to populate the feature id (fid) column
        geom = []  # this list will be used to populate the geometry column

        first_node = shortest_path[0]
        for node in shortest_path[1:]:
            link_fid = graph.edges[first_node, node]['fid']
            links.append(link_fid)
            geom.append(LineString(self.__road_links[link_fid]['coords']))
            first_node = node

        shortest_path_gpd = gpd.GeoDataFrame({'fid': links, 'geometry': geom})
        return shortest_path_gpd

# References
# https://networkx.org/documentation/stable/reference/classes/digraph.html
# https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.weighted.dijkstra_path.html
# Week 8 practical
