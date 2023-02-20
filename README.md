# flood-emergency-planning

## Contributors
- Hurmain Ariffin (task 5)
- Yuet Wai Cheuk (task 2 & 6)
- Haris Riefchi Wicaksono (task 1)
- Zonghe Ma (task 3)
- Joy Zhao (task 4)

## Introduction
Extreme flooding is expected on the Isle of Wight and the authority in charge of planning the emergency response is advising everyone to proceed by foot to the nearest high ground.

To support this process, the emergency response authority wants you to develop a software to quickly advise people of the quickest route that they should take to walk to the highest point of land within a 5km radius.

## Instructions
To complete this assignment, you need to build a Python application. Your task is to create a Python program named ‘main.py’ that does what explained in the following subsections. To do this, you are allowed to use only the packages presented in the module.

The first 5 tasks will award you a total of 70 marks. The 6th task (10 marks) is designed to test your ability to carry out your own research in order to solve it. Finally, the 7th tasks is a creativity task that can award you 20 additional marks for the development of additional unspecified features.

## Task 1: User Input
This program asks the user to input their current location. It first asks for the easting coordinate then the northing coordinate. This easting cooodinate must within [430000, 465000] and the northing coordinate must within [80000, 95000]. If enteres coodinates are not within the range or on the main land of Isle of Wight, it will constantly ask the user to modify the answers.

### About

#### Files

| File name     | Description  |
|---------------|------------------------------|
| task1.py      | This file contains the  `CoordinateInput` *Class* and *functions* asking user for the currrent position                        |
| Material/shape/isle_of_wight.shp           | This shape file is used to make sure the user is on the land |

#### Parameters

>**CoordinateInput** (shape_file)

>**user_input** ()

| Parameters Type | Name         | Explanation                                                                | Data Type |
|-----------------|--------------|----------------------------------------------------------------------------|-----------|
| Input value     | shape_file     | The shape file of the Isle of Wight |String                         |
| Return value    | position | User's location                               | Point     |

#### Error Handling
1. Changing the CRS to the British National Grid.

2. Checking if the position is located within the boundary of the Isle of Wight.

#### Creativities

1. Use `while` loops to constantly interact with the user.
1. Make sure the user is within the boundary of the Isle of Wight.


## Task 2: Highest Point Identification
Identify the highest point within a 5km radius from the user location.

To successfully complete this task you could (1) use the window function in rasterio to limit the size of your elevation array. If you do not use this window you may experience memory issues; or, (2) use a rasterised 5km buffer to clip an elevation array. Other solutions are also accepted. Moreover, if you are not capable to solve this task you can select a random point within 5km of the user.

## Task 3: Nearest Integrated Transport Network

Identify the nearest Integrated Transport Network (ITN) node to the user and the nearest ITN node to the highest point identified in the previous step. To successfully complete this task you could use r-trees.

### About

#### Files

| File name | Description                                                  | Notes                              |
| :-------- | ------------------------------------------------------------ | ---------------------------------- |
| task3.py  | This file contains the *Class* and *definition* of the nearest ITN algorithm |                                    |
| main.py   | This is the main execute file of task 3                      |                                    |
| itn       | This is the file folder for testing including *'solent_itn.json'* which is used in this local execution but not being uploaded | You can find this in Materials/itn |

#### Parameters
>**ITN** (itn_path)

>**nearest_node**(location)

| Parameters Type | Name     | Explanation                                  | Data Type       |
| --------------- | -------- | -------------------------------------------- | --------------- |
| Input value     | itn_path | Path to the Json file with ITN data          | String          |
| Input value     | location | A location                                   | Point           |
| Return value    | nodes    | The nearest ITN points to the input location | list (of Point) |
#### Error Handling
1. Using a list to return the ouput for potential multiple nearest nodes.

## Task 4: Shortest Path
Class `ShortestPath` is for this task. It can find the shortest path from the user to the highest point by applying Naismith’s rule. Naismith's rule suggests that a healthy person able to walk at a speed of 5 kilometres per hour will gain one minute for every 10 metres climbed (i.e. ascending rather than descending). 

### About

#### Class

> *Class* **ShortestPath** (*road_file, itn, transform, buffer*)

| Parameters | Explanation                                                                | Data Type |
|----------------|----------------------------------------------------------------------------|-----------|
| road_file | Path to the road links file |String                         |
| itn | An object of ITN which can find nearest nodes | ITN |
| transform | Transformation parameters of the elevation raster | numpy.Array |
| buffer | 5km buffer around the user's location | Polygon |

#### Method

> 1. *Method* **shortest_path**(*elevation_file, user_location, highest_points*)

It finds the shortest path between the location of the user and the highest points(s) using Dijkstra Algorithm, which means finding the way consuming the least time. The walking time is calculated by applying Naismith’s rule.

|Parameter Type | Parameter | Explanation  | Data Type |
|---------------|-----------|--------------|-----------|
|Input| elevation_file | Path to the elevation file |String  |
|Input| user_location | The location of the user | Point |
|Input| highest_points | Highest points within 5km (there may be more than one point) | list (of Point) |
|Output| node_user | The nearest node to the user | Point |
|Output| node_highest | The nearest node to the highest point | Point |
|Output| highest_point | The highest point (destination) | Point |
|Output| shortest_path_gpd | The shortest path | GeoDataFrame |


> 2. *Method* **add_geometry**(*shortest_path, graph*)

It associates road feature id with geometry. This will be useful in the plotting.

|Parameter Type | Parameter | Explanation  | Data Type |
|---------------|-----------|--------------|-----------|
|Input| shortest_path | Path to the elevation file |list  |
|Input| graph | Directed graph containing all rode nodes and road links within 5km buffer around th | DiGraph |
|Output| shortest_path_gpd | The shortest path | GeoDataFrame |

#### Error Handling

1. Print error massage if a source node or a target node is not found in the road node graph.

2. Print error massage if the target node is not reachable from the source node in the road node graph.

#### Creativities

1. There might be more than one node nearest to the user, more than one highest point, and more than one node nearest to the highest point(s). This program calculates the walking time for all possible paths and compares them to confirm the final node nearest to the user, the only highest point and the nearest node to the highest point. 

## Task 5: Map Plotting
Plot a background map 20km x 20km of the surrounding area. You are free to use either a 1:50k Ordnance Survey raster (with internal color-map). Overlay a transparent elevation raster with a suitable color-map. Add the user’s starting point with a suitable marker, the highest point within a 5km buffer with a suitable marker, and the shortest route calculated with a suitable line. Also, you should add to your map, a color-bar showing the elevation range, a north arrow, a scale bar, and a legend.

## Task 6: Extend the Region
The position of the user is restricted to a region in where the user must be more than 5km from the edge of the elevation raster. Write additional code to overcome this limitation.
