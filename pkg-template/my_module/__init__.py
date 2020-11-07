import os
import base64
import argparse

import math

try:
    import numpy as np
    import cv2 as cv
except:
    import sys
    sys.path.append('/opt/')
    import numpy as np
    import cv2 as cv


def run(img_path):

    """
        1. Validate & Load inputs
    """

    # check image path
    if(img_path is None or type(img_path) is not str or not os.path.exists(img_path)):
        print("ERROR: Image path is invalid")
        return None

    # Load Image
    img_src = cv.imread(img_path)

    # check if image is valid
    if(img_src is None or type(img_src) is not np.ndarray):
        print("ERROR: Image asset is invalid")
        return None

    # check if image is BGR
    if(len(img_src.shape) != 3):
        print("ERROR: Image asset should be composed of 3 channels")
        return None

    # Grab dimensions
    height = img_src.shape[0]
    width = img_src.shape[1]

    # check that it is not too small
    if(height <= MIN_IMG_HEIGHT or width <= MIN_IMG_WIDTH):
        print("ERROR: Image is too small")
        return None


    """
        2. Process Image
    """
