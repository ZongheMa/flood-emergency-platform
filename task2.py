import os

import numpy as np
import rasterio
from geopandas import GeoSeries
from rasterio import mask
from shapely.geometry import Point
from shapely.geometry import Polygon


# Define Class for Task 2 and Task 6 (i.e. Highest Point Identification and Extend the Region)
class HighestPoint:
    def __init__(self, user_location):
        # Attribute for receiving the User Location
        self.__user_location = user_location
        self.__buffer = []
        self.__out_transform = []

    # Method for searching the highest point
    def get_highest_point(self):
        # Creating a 5 km buffer from the User Location
        self.__buffer = Polygon(self.__user_location.buffer(5000))
        # Creating a GeoSeries to store the buffer polygon
        g = GeoSeries([self.__buffer])

        # Read and mask the raster DEM file (i.e. SZ.asc)
        with rasterio.open('Material/elevation/SZ.asc') as src:
            # rasterio.mask.mask allows us to mask out the region beyond 5km from the User Location even at the zone
            # within 5km from the raster's edge. (Reference:https://www.youtube.com/watch?v=TbbL2yeRTsk) It makes
            # masking at location within 5km from the raster's edge feasible.  It is regarded as the solution to
            # overcome the limitation stated in Task 6.
            raster, self.__out_transform = rasterio.mask.mask(src, g, all_touched=True, filled=True,
                                                                         invert=False, crop=True)
            out_meta = src.meta

        # Read update the metadata of the masked raster
        out_meta.update({
            'height': raster.shape[1],
            'width': raster.shape[2],
            'transform': self.__out_transform
        })

        # Write the masked raster to a new file (i.e. Masked_SZ.asc)
        with rasterio.open('Material/elevation/Masked_SZ.asc', 'w', **out_meta) as dst:
            dst.write(raster)

        # Open and plot the new raster
        # masked_dataset = rasterio.open(os.path.join('Material', 'elevation', 'Masked_SZ.asc'))
        # rasterio.plot.show(masked_dataset, cmap='terrain')

        # Error handling to stop the program when the elevation of the whole 5k m buffer are smaller than or equal to
        # zero
        if raster.max() <= 0 and raster.min() <= 0:
            print("Error! The whole 5000 m buffer zone are below waterline!!!")
            exit()
        else:
            # search the masked area to find out the highest points
            result = np.where(raster == raster.max())
            high_points = []

            # Extract the highest points' X and Y image coordinates
            highest_points_y = result[1]
            highest_points_x = result[2]

            for i, item in enumerate(highest_points_y):
                # Convert the highest points' X and Y image coordinates to ground coordinates
                tran_xy = (self.__out_transform * (highest_points_x[i], highest_points_y[i]))
                # Add or subtract half size of a pixel (i.e. 2.5m) to find out the center of the highest points
                tran_xy_center = (tran_xy[0] + 2.5, tran_xy[1] - 2.5)
                # Create Shapely Point features for the highest points
                hp_i = Point(tran_xy_center)
                high_points.append(hp_i)

            if len(high_points) == 1:
                print('One highest location found: (Easting ' + str(high_points[0].x) + ', Northing ' + str(
                    high_points[0].y) + ').\n')
            else:
                print(str(len(high_points)) + ' highest locations found:')
                for i in range(len(high_points)):
                    print('\t', i + 1,
                          '(Easting ' + str(high_points[i].x) + ', Northing ' + str(high_points[i].y) + ')\t')
                print()

            # return the Shapely Point features storing the highest points
            return high_points

    # Method to return the transformation parameters of the masked raster
    def get_5k_transform(self):
        return self.__out_transform

    # Method to return the 5km buffer
    def get_buffer(self):
        return self.__buffer
