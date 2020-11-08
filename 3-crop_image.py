import os
import numpy as np

# Lib to work with .tif
import imagery_helper

# mask tool from rasterio
import rasterio

# Lib to import our accidents data
import db_helper

# Find the current working directory
path = os.getcwd()

# Grab path to figures folder
if os.path.isdir(os.path.join(path, 'Figures')) == False:
    raise Exception('Figures directory does not exist, run retrieve script')
figures_dir_path = os.path.join(path, 'Figures')

# Path to our imagery
src_path = os.path.join(figures_dir_path, 'kandahar-compressed.tif')

# load
satdat = imagery_helper.load(src_path)


################################################################################
#                                                                              #
#                  Loading a sample the processed incidents                    #
#                                                                              #
################################################################################

# set crs
crs = '4326'

# Load the data
df = db_helper.get_incidents(OFFSET=0, LIMIT=10000, CRS=crs)

# Keep certain columns
df = df.loc[:, ['geometry']]


################################################################################
#                                                                              #
#                     Go through incidents and draw image                      #
#                                                                              #
################################################################################

# count number of incidents inside
count = 0

# Go through rows
for index, row in df.iterrows():

    # get geometry
    geometry = row['geometry']

    # convert point to lat lng
    lng, lat = imagery_helper.point_to_lng_lat(geometry)

    # grab geometry
    aoi = [feature['geometry'] for feature in geojson['features']]



    try:
        xpos, ypos = convert_latlng_to_pixel(lat, lng)

        # set radius
        y_min = ypos - radius
        y_max = ypos + radius
        x_min = xpos - radius
        x_max = xpos + radius

        if(y_min < 0):
            y_min = 0
        if(x_min < 0):
            x_min = 0

        # set to white
        for i in range(y_min, y_max):
            for j in range(x_min, x_max):
                for k, band in enumerate(bands):
                    bands[k][i][j] = 255

        # increment count
        count += 1

    except:
        pass


print(f'Nbr of incidents : {count}')

# stack
scaled_img = np.dstack(bands).astype(np.uint8)

# Use imshow to load the blue band.
fig = plt.imshow(scaled_img)

# Display the results.
plt.show()

# get count
count = len(bands)

# move axis with entries to beginning
scaled_img = np.moveaxis(scaled_img,-1,0)

# get the metadata of original GeoTIFF:
meta = satdat.meta

# get the dtype
m_dtype = scaled_img.dtype

# set the source metadata as kwargs we'll use to write the new data:
kwargs = meta

# update the 'dtype' value to match our NDVI array's dtype:
kwargs.update(dtype=m_dtype)

# update the 'count' value since our output will no longer be a 4-band image:
kwargs.update(count=count)

# Finally, use rasterio to write new raster file 'data/ndvi.tif':
with rasterio.open(out_path, 'w', **kwargs) as dst:
        dst.write(scaled_img)

