import os
import numpy as np
from PIL import Image
import json

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

# Grab path to cropped folder
cropped_dir = os.path.join(path, 'Figures', 'cropped')
if os.path.isdir(cropped_dir) == False:
    os.mkdir(cropped_dir)


################################################################################
#                                                                              #
#                             Loading our image                                #
#                                                                              #
################################################################################

# Path to our imagery
src_path = os.path.join(figures_dir_path, 'kandahar-compressed.tif')

# load
satdat = imagery_helper.load(src_path)

# load image PIL
img_src = Image.open(src_path)
img_src = np.array(img_src)

# grab dimensions of image
width = satdat.width
height = satdat.height

# grab approximate pixel dimensions in meters
pixel_results = imagery_helper.pixel_in_m(satdat)

if(pixel_results is None):
    raise Exception('Image is not in ESPG:4326')

xres, yres = pixel_results

# compute approximate size of image in meters
width_m = width*xres
height_m = height*yres

# divide image in little squares
square_length = 300
nbr_x = np.floor(width_m/float(square_length))
nbr_y = np.floor(height_m/float(square_length))
print(f'Nbr of images : {nbr_x*nbr_y}')

# compute deltas
d_x = int(np.floor(width/float(nbr_x)))
d_y = int(np.floor(height/float(nbr_y)))

################################################################################
#                                                                              #
#                  Loading a sample the processed incidents                    #
#                                                                              #
################################################################################

# set crs
crs = '4326'

# Load the data
incidents_df = db_helper.get_incidents(OFFSET=0, LIMIT=10, CRS=crs, CONTAINED=True)

# Keep certain columns
incidents_df = incidents_df.loc[:, ['geometry']]

# init geom_arr
incidents_geom_arr = []

# Go through rows
for index, row in incidents_df.iterrows():

    # get geometry
    geometry = row['geometry']

    # get point from geom
    lng, lat = imagery_helper.point_to_lng_lat(geometry)

    # append
    incidents_geom_arr.append([lng, lat])


def contains_incident(lng_min, lat_min, lng_max, lat_max):

    # Go through rows
    for incident_geom in incidents_geom_arr:

        # grab incident lng, lat
        lng, lat = incident_geom

        if(lng >= lng_min and lng <= lng_max and lat >= lat_min and lat <= lat_max):
            return True

    return False


# init dataframe
imagery_df = []
im_index = 0
incidents_count = 0

# crop image
for x_pos in list(range(0, width, d_x)):
    for y_pos in list(range(0, height, d_y)):

        # outpath
        out_path = os.path.join(cropped_dir, f'{im_index}.png')

        # increment ind
        im_index += 1

        # get pos in pixels
        x_min = x_pos
        x_max = x_pos + d_x
        y_min = y_pos
        y_max = y_pos + d_y

        # get pos in lat, lng
        lng_min, lat_min = imagery_helper.pixel_pos_to_lng_lat(satdat, x_min, y_min)
        lng_max, lat_max = imagery_helper.pixel_pos_to_lng_lat(satdat, x_max, y_max)

        # get true
        true_lng_min = np.min([lng_min, lng_max])
        true_lng_max = np.max([lng_min, lng_max])
        true_lat_min = np.min([lat_min, lat_max])
        true_lat_max = np.max([lat_min, lat_max])

        # check if contains incident
        contains = contains_incident(true_lng_min, true_lat_min, true_lng_max, true_lat_max)
        if(contains):
            incidents_count += 1

        # crop image
        cropped_img = img_src[y_min:y_max, x_min:x_max, :]

        # append to df
        imagery_df.append({
            'filename': os.path.basename(out_path),
            'incident': contains,
            'bbox': {
                'lng_min': lng_min,
                'lat_min': lat_min,
                'lng_max': lng_max,
                'lat_max': lat_max
            }
        })

        # save
        try:
            im = Image.fromarray(cropped_img)
            im.save(out_path)

        except:
            pass

# save df
with open(os.path.join(figures_dir_path, 'training_data.json'), 'w') as outfile:
    json.dump(imagery_df, outfile)


print(f'Number of images with incidents : {incidents_count}')
