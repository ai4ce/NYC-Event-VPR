import pandas as pd
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon
import glob

# aggregate all GPS data and plot into one graph

file_path = glob.glob('/home/taiyipan/repository/event_camera_master_project/outbound_data/sensor_data_*/GPS_data_*.csv')
print('GPS file count: {}'.format(len(file_path)))

df = pd.concat(map(pd.read_csv, file_path), ignore_index = True)

print('Total entry count: {}'.format(df.shape[0]))


geometry = [Point(x, y) for x, y in zip(df['Longitude'], df['Latitude'])]
geo_df = gpd.GeoDataFrame(
    df,
    # crs = crs,
    geometry = geometry
)
print(geo_df.head())

map_path = glob.glob('/home/taiyipan/repository/event_camera_master_project/rtk_gps/shape_files/nyc/*.shp')
print(map_path)
map = gpd.read_file(map_path[0])

fig, ax = plt.subplots(figsize = (20, 20))
map.plot(ax = ax, alpha = 0.4, color = 'grey')
geo_df.plot(ax = ax, markersize = 1, marker = '.', color = 'red')
plt.title("NYC GPS data from {}".format(file_path[0]))
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()
