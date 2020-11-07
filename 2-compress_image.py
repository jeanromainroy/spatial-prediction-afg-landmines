import os

# Lib to work with .tif
import imagery_helper

# Find the current working directory
path = os.getcwd()

# Grab path to data folder
if os.path.isdir(os.path.join(path, 'Data')) == False:
    raise Exception('Data directory does not exist, run retrieve script')
data_dir_path = os.path.join(path, 'Data')


# Path to our imagery
src_path = "/home/jean-romain/Geospatial/30cm_imagery/afghanistan.tif"

# path to compressed
out_path = 'compressed.tif'

# load
satdat = imagery_helper.load(src_path)

# display info
imagery_helper.info(satdat)

# compress
imagery_helper.compress(src_path, out_path, compression_type='JPEG')

print(f'Compression done, file can be found {out_path}')
