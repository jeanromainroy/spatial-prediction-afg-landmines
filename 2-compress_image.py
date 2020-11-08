import os
import numpy as np

# Lib to work with .tif
import imagery_helper

# Find the current working directory
path = os.getcwd()

# Grab path to figures folder
if os.path.isdir(os.path.join(path, 'Figures')) == False:
    raise Exception('Figures directory does not exist, run retrieve script')
figures_dir_path = os.path.join(path, 'Figures')

# Path to our imagery
src_path = os.path.join(figures_dir_path, "test-img-full-resolution.tif")

# path to output image
out_path_1 = os.path.join(figures_dir_path, 'test-img-processed.tif')
out_path_2 = os.path.join(figures_dir_path, 'test-img-compressed.tif')

# load
satdat = imagery_helper.load(src_path)

# display info
imagery_helper.info(satdat)

# scale to uint8
imagery_helper.to_uint8(src_path, out_path_1, min=0, max=10000)

# compress
imagery_helper.compress(out_path_1, out_path_2, compression_type='JPEG')

print(f'Compression done, file can be found {out_path_2}')
