from task1 import CoordinateInput
from task2 import HighestPoint
from task3 import ITN
from task4 import ShortestPath
from task5 import Plotting

shape_file = 'Material/shape/isle_of_wight.shp'
road_file = 'Material/itn/solent_itn.json'
elevation_file = 'Material/elevation/SZ.asc'
masked_elevation = 'Material/elevation/Masked_SZ.asc'


def main():
    # (Task 1) User Input
    user_location = CoordinateInput(shape_file).user_input()

    # (Task 2 & Task 6) Highest Point Identification & Extend the Region
    print("Finding highest location within 5 kilometres...\n")
    hp = HighestPoint(user_location)
    highest_points = hp.get_highest_point()  # the highest point
    transform = hp.get_5k_transform()  # transformation parameters of the masked raster
    buffer = hp.get_buffer()  # 5 km buffer around the user location

    # (Task 3) Nearest ITN
    itn = ITN(road_file, buffer)

    # (Task 4) Shortest Path
    shortest_path = ShortestPath(road_file, itn, transform, buffer)
    # final nodes in the path and the path between the nearest node to the user and node to the highest point
    node_user, node_highest, highest_point, shortest_path_gpd = shortest_path.shortest_path(elevation_file,
                                                                                            user_location,
                                                                                            highest_points)

    # (Task 5) Map Plotting
    plotter = Plotting(user_location, highest_point, shortest_path_gpd)
    plotter.plot_map()


if __name__ == '__main__':
    main()
