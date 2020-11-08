import os
import numpy as np
import cv2 as cv

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


def convert_tif_to_png(src_path, out_path, resize_ratio=None):
    """
        Takes as input a .tif image and saves it as .png, option to resize
    """

    # load image with opencv
    img = cv.imread(src_path)

    # Grab dimensions of image
    height, width, _ = img.shape

    # resize
    if(resize_ratio is not None):
        img = resize(img, int(width/float(resize_ratio)), int(height/float(resize_ratio)))

    # write
    cv.imwrite(out_path, img)
