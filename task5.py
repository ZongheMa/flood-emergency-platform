import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from pyproj import CRS
from rasterio import plot as raster_plot
from rasterio.mask import mask
from shapely.geometry import Point, Polygon

CRS_BNG = CRS('epsg:27700')

# Materials
isle_of_wight = gpd.read_file('Material/shape/isle_of_wight.shp')
road_links = gpd.read_file('Material/roads/links.shp')
road_nodes = gpd.read_file('Material/roads/nodes.shp')
background = rasterio.open('Material/background/raster-50k_2724246.tif')
elevation = rasterio.open('Material/elevation/SZ.asc')


class Plotting:

    def __init__(self, user_location, highest_point, shortest_path_gpd):
        self.user_location = user_location
        self.highest_point = highest_point
        self.shortest_path_gpd = shortest_path_gpd

    def plot_map(self):
        bounds = background.bounds
        palette = []
        for key, val in background.colormap(1).items():
            palette.append(val)
        palette = np.array(palette)

        # Drawing map background
        background_image = palette[background.read(1)]
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.imshow(background_image, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top], zorder=0)
        ax.set_title('The shortest path between the user and the highest point within 5km radius', fontsize=15)
        ax.set_xlabel('Easting', fontsize=10)
        ax.set_ylabel('Northing', fontsize=10)

        # Start Point or User Input
        start_x = self.user_location.x
        start_y = self.user_location.y

        # Plot a background map 20km x 20km of the surrounding area
        km = 20
        xmin = np.max([start_x - km * 500, bounds.left])
        xmax = np.min([start_x + km * 500, bounds.right])
        ymin = np.max([start_y - km * 500, bounds.bottom])
        ymax = np.min([start_y + km * 500, bounds.top])
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)

        isle_of_wight.to_crs(CRS_BNG).plot(ax=ax, color='none')
        road_nodes.to_crs(CRS_BNG).plot(ax=ax, markersize=3, color='grey')
        road_links.to_crs(CRS_BNG).plot(ax=ax, linewidth=1, cmap='RdYlGn', column='descript_1')

        # Start, End Node and Path
        plt.plot(start_x, start_y, 'ro', markersize=15, label='user point')
        plt.plot(self.highest_point.x, self.highest_point.y, 'go', markersize=15, label='highest point')
        self.shortest_path_gpd.plot(ax=ax, edgecolor='orange', linewidth=5, label='shortest path', zorder=2)

        # 5000m buffer elevation raster
        m = 5000
        start = (start_x, start_y)
        start_point = Point(start)
        boundary = start_point.buffer(m)
        polygon = Polygon([(elevation.bounds.left, elevation.bounds.bottom),
                           (elevation.bounds.right, elevation.bounds.bottom),
                           (elevation.bounds.right, elevation.bounds.top),
                           (elevation.bounds.left, elevation.bounds.top)])
        elev_masked, out_tf = mask(elevation, shapes=[boundary.intersection(polygon)], filled=False, crop=True)
        raster_plot.show(source=elev_masked, ax=ax, zorder=1,
                         transform=out_tf, alpha=0.5, cmap=plt.get_cmap('terrain'))

        # Adding North Arrow
        x, y, arrow_length = 0.9, 0.2, 0.1
        ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
                    arrowprops=dict(facecolor='black', width=5, headwidth=15),
                    ha='center', va='center', fontsize=20,
                    xycoords=ax.transAxes)

        # Adding scale bar
        ax.add_artist(AnchoredSizeBar(ax.transData, size=1000,
                                      label='1 km', loc=4, frameon=False, pad=0.6,
                                      size_vertical=0.7, color='black'))

        # Adding Color Bar
        dtm_array = elevation.read(1)
        dtm = ax.imshow(dtm_array, cmap='terrain')
        plt.text(1.15, 0.9, 'Elevation (m)', transform=ax.transAxes, fontsize=10)
        plt.colorbar(dtm, ax=ax, orientation='vertical', anchor=(0.0, 0.5), shrink=0.8)

        plt.legend()
        plt.show()

# References
# https://matplotlib.org/3.1.0/api/_as_gen/mpl_toolkits.axes_grid1.anchored_artists.html
# https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.imshow.html#matplotlib.pyplot.imshow
# https://snyk.io/advisor/python/rasterio/functions/rasterio.mask.mask
