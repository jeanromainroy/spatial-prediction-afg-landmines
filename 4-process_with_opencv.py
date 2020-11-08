import os
import numpy as np
import cv2 as cv

# Lib to work with .tif
import imagery_helper


# Find the current working directory
path = os.getcwd()

# Grab path to data folder
if os.path.isdir(os.path.join(path, 'Data')) == False:
    raise Exception('Data directory does not exist, run retrieve script')
data_dir_path = os.path.join(path, 'Data')


def show(img, title='img'):
    """
        Displays image through opencv gui
    """

    cv.imshow(title, img)
    key = cv.waitKey(0)
    cv.destroyAllWindows()
    if(key == 27):
        assert False


def resize(img, target_width, target_height, INTERPOLATION_METHOD=None):
    """
        Resizes an image to the target width and height
    """

    # Grab dimensions of image
    height = img.shape[0]
    width = img.shape[1]

    # deep copy
    img_resized = img.copy()

    if(INTERPOLATION_METHOD is None):
        if(width > target_width or height > target_height):
            # shrink
            img_resized = cv.resize(img_resized, (target_width, target_height), interpolation=cv.INTER_AREA)

        else:
            # enlarge
            img_resized = cv.resize(img_resized, (target_width, target_height), interpolation=cv.INTER_CUBIC)

    else:
        img_resized = cv.resize(img_resized, (target_width, target_height), interpolation=INTERPOLATION_METHOD)

    return img_resized


# Path to our imagery
src_path = os.path.join(data_dir_path, 'kandahar-compressed.tif')

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
resized_img = resize(edges, int(width/resize_ratio), int(height/resize_ratio))

# show
show(resized_img)

# outpath
out_path = os.path.join(data_dir_path, 'opencv_processed.tif')

# write
cv.imwrite(out_path, resized_img)

# check vals
imagery_helper.info(imagery_helper.load(out_path))
