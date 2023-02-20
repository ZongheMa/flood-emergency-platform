from rtree import index
from shapely.geometry import Point
import json


class ITN:

    def __init__(self, itn_path, buffer):
        self.__buffer = buffer  # 5km buffer around the user location
        self.__idx = self.r_tree(itn_path)  # r-tree storing road nodes

    # Init road nodes and store them in an r-tree
    def r_tree(self, itn_path):
        with open(itn_path, 'r') as f:
            ITN = json.load(f)
        idx = index.Index()
        road_nodes_idx = ITN['roadnodes']
        road_nodes = []
        id_node = 0
        for node in road_nodes_idx:
            point = Point(road_nodes_idx[node]['coords'])
            if point.within(self.__buffer) or point.touches(self.__buffer):
                # Test for output
                # print(road_nodes_idx[node]['coords'])
                road_nodes.append(road_nodes_idx[node]['coords'])
                idx.insert(id_node, (point.x, point.y), obj=node)
                id_node += 1
        return idx

    # Find the nearest nodes for a given location
    def nearest_node(self, location):
        # Error handling by using a list for potential multiple nearest nodes.
        nodes = list(self.__idx.nearest((location.x, location.y), 1, objects=True))
        # Error handling by checking if there is node found
        if len(nodes) == 0:
            print('Sorry, no ITN node found within 5km!')
            exit()
        # Test the return of this function
        # print("Nodes: ")
        # for node in nodes:
        #     print(node.id)
        #     print(node.object)

        return nodes


