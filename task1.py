import geopandas as gpd
from shapely.geometry import Point


# Test whether location that is inputted is in the raster box and within the boundary of the Isle of Wight.
class CoordinateInput:

    def __init__(self, shape_file):
        self.__shape_file = shape_file

    # Ask the user to input the current location
    def user_input(self):
        # First, check if the entered location is within the boundary of the elevation raster
        position = self.prompt()
        isle_of_wight = gpd.read_file(self.__shape_file)
        # Error handling by changing CRS to the British National Grid
        isle_of_wight.to_crs(27700)
        # Error handling by checking if the position is located within the boundary of the Isle of Wight
        while not position.within(isle_of_wight['geometry']).any():
            print('The position is not on the land of Isle of Wight. Please try again.')
            print()
            position = self.prompt()

        # Test output for isle_of_wight
        # for geo in isle_of_wight['geometry']:
        #     print(geo)

        print('\nEntered successfully! Your current position is: (Easting ' + str(position.x) + ', Northing ' + str(
            position.y) + ').\n')
        return position

    # Provide prompts for users to input their current location, which must within the boundary of the elevation raster
    @staticmethod
    def prompt():
        print('Please input your current location.')
        # Ask for easting coordinate
        easting = int(
            input('Please enter the easting coordinate (based on British National Grid between 425000 and 470000): '))
        while easting < 425000 or easting > 470000:
            easting = int(
                input('Sorry! The easting coordinate should be between 425000 and 470000. Please enter again: '))

        # Ask for northing coordinate
        northing = int(
            input('Please enter the northing coordinate (based on British National Grid within 75000 abd 100000): '))
        while northing < 75000 or northing > 100000:
            northing = int(
                input('Sorry! The northing coordinate should be between 75000 and 100000. Please enter again: '))

        position = Point(easting, northing)
        return position
