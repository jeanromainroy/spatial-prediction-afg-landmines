import os
import numpy as np
from matplotlib import pyplot as plt

# Lib to work with .tif
import imagery_helper

# Lib to work with opencv
import opencv_helper

# mask tool from rasterio
import rasterio
from rasterio.mask import mask

# Lib to import our accidents data
import db_helper

# Find the current working directory
path = os.getcwd()

# Grab path to data folder
if os.path.isdir(os.path.join(path, 'Data')) == False:
    raise Exception('Data directory does not exist, run retrieve script')
data_dir_path = os.path.join(path, 'Data')

# Path to our imagery
src_path = os.path.join(data_dir_path, 'kandahar-compressed.tif')
process_path = os.path.join(data_dir_path, 'kandahar-compressed-with-incidents.tif')
out_path = os.path.join(data_dir_path, 'kandahar-compressed-with-incidents.png')

# load
satdat = imagery_helper.load(src_path)

# read all bands from source dataset into a single ndarray
bands = satdat.read()

def scale(band):
    if(np.max(band) > 255):
        band = np.round((band / 10000.0)*255.0)     # scale to 0 - 255
        band[band > 255] = 255                      # if above set to max
    return band

# scale each band
for i, band in enumerate(bands):
    bands[i] = scale(band).astype(np.uint8)

# set the drawn incident radius
radius = 10

################################################################################
#                                                                              #
#                  Loading a sample the processed incidents                    #
#                                                                              #
################################################################################

# set crs
bbox_crs = '4326'

# Load the data
df = db_helper.get_incidents(OFFSET=0, LIMIT=10000, CRS=bbox_crs)

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

    try:
        # remap (lng,lat) to (x, y)
        xpos, ypos = imagery_helper.convert_lng_lat_to_pixel(satdat, lng, lat)

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
with rasterio.open(process_path, 'w', **kwargs) as dst:
        dst.write(scaled_img)

# load
satdat = imagery_helper.load(process_path)

# display info
imagery_helper.info(satdat)

# scale to uint8
imagery_helper.to_uint8(process_path, process_path, min=0, max=10000)

# compress
imagery_helper.compress(process_path, process_path, compression_type='JPEG')

# convert to png and resize
opencv_helper.convert_tif_to_png(process_path, out_path, resize_ratio=10.0)

print(f'Compression done, file can be found {out_path}')
