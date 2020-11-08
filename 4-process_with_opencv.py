import os
import numpy as np
import cv2 as cv

# Lib to work with opencv
import opencv_helper

# Lib to work with .tif
import imagery_helper

# Find the current working directory
path = os.getcwd()

# Grab path to figures folder
if os.path.isdir(os.path.join(path, 'Figures')) == False:
    raise Exception('Figures directory does not exist, run retrieve script')
figures_dir_path = os.path.join(path, 'Figures')

# Path to our imagery
src_path = os.path.join(figures_dir_path, 'kandahar-compressed.tif')

# outpath
out_path = os.path.join(figures_dir_path, 'opencv-processed.tif')

# load image with opencv
img = cv.imread(src_path)

# Grab dimensions of image
height, width, _ = img.shape

# convert to grayscale
img_gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)

# process
img_hist = cv.equalizeHist(img_gray)
edges = cv.Canny(cv.GaussianBlur(img_hist, ksize=(5,5), sigmaX=1, sigmaY=1), 0.1*1024, 0.25*1024)

# resize
resize_ratio = 10.0
resized_img = opencv_helper.resize(edges, int(width/resize_ratio), int(height/resize_ratio))

# show
opencv_helper.show(resized_img)

# write
cv.imwrite(out_path, resized_img)

# check vals
imagery_helper.info(imagery_helper.load(out_path))

# print
print(f'Processing done, file can be found {out_path}')
