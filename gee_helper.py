import os
from datetime import datetime, timedelta
import time

from io import BytesIO
import requests
import zipfile

import ee

# image
from PIL import Image
import numpy as np

# Pretty print
import pprint
pp = pprint.PrettyPrinter(depth=4)

# init earth engine
ee.Initialize()

# Find the current working directory
path = os.getcwd()

# Grab path to data folder
if os.path.isdir(os.path.join(path, 'Data')) == False:
    raise Exception('Data directory does not exist, run retrieve script')
data_dir_path = os.path.join(path, 'Data')


def humansize(nbytes):
    """
        Function to get sizes in Human readable format
    """

    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def get_imagery(
        BBOX_CORNERS,
        FILTER_DATE='2017-03-01',
        FILTER_DATE_RADIUS_DAYS=30,
        IMAGE_COLLECTION='COPERNICUS/S2_SR',
        INTEREST_BANDS=['B4', 'B3', 'B2'],
        MAX_CLOUD_COVER=20,
        MAX_VISUALIZE_INTENSITY=5000,
        EXPORT_TO_DRIVE=False
    ):

    # check inputs
    if(len(INTEREST_BANDS) > 3):
        raise Exception('No more than 3 bands')

    # Production of rectangle limiting ROI
    ROI_GEOMETRY_RECT = ee.Geometry.Rectangle(coords=BBOX_CORNERS, proj='EPSG:4326')

    # Print roi area in square kilometers.
    ROIarea = ROI_GEOMETRY_RECT.area().divide(1000 * 1000).getInfo()
    print(f'ROI area : {ROIarea} km^2')

    # convert input to datetime window
    dateformat = '%Y-%m-%d'
    datetime_obj = datetime.strptime(FILTER_DATE, dateformat)

    # make sure date year is > 2017 (Sentinel lower bound)
    adjust_year = datetime_obj.year
    if(adjust_year < 2017):
        adjust_year = 2017
        datetime_obj = datetime_obj.replace(year=adjust_year)

    # set time window
    datemin = datetime_obj - timedelta(days=FILTER_DATE_RADIUS_DAYS)
    datemax = datetime_obj + timedelta(days=FILTER_DATE_RADIUS_DAYS)
    datemin_str = datemin.strftime(dateformat)
    datemax_str = datemax.strftime(dateformat)

    #Public Image Collections
    results = ee.ImageCollection(IMAGE_COLLECTION).filterDate(datemin_str, datemax_str).filterBounds(ROI_GEOMETRY_RECT).filterMetadata('CLOUDY_PIXEL_PERCENTAGE','less_than', MAX_CLOUD_COVER)

    # Get collection size
    assets_count = results.size().getInfo()
    assets_size = humansize(results.reduceColumns(ee.Reducer.sum(), ['system:asset_size']).getInfo()['sum'])
    print(f'Total number of assets with filters: {assets_count}\n')
    print(f'Total size of collection : {assets_size}')

    # check if we found assets
    if(assets_count == 0):
        return None

    # Create a list with all the images
    collectionList = results.toList(results.size())
    collectionSize = collectionList.size().getInfo()

    # Parse
    for i in range(0, collectionSize):

        # get data
        infoDict = collectionList.get(i).getInfo()

        # print index
        print(f"--- Index: {i} ---")
        print(f"\nid:\t\t\t\t{infoDict['id']}")

        # print info
        pp.pprint(infoDict)

        print('\n\n\n\n')

        # STOP AFTER FIRST
        break

    # Selected image index
    desiredIndex = 0

    # Get an image
    sample_image = ee.Image(collectionList.get(desiredIndex)).select(INTEREST_BANDS)

    # visualize
    img_visualized = sample_image.visualize(
        min=0,
        max=MAX_VISUALIZE_INTENSITY
    )

    # clip
    clipped_img = img_visualized.clipToBoundsAndScale(
        geometry=ROI_GEOMETRY_RECT
    )

    # if export to drive
    if EXPORT_TO_DRIVE:

        # start export task
        task = ee.batch.Export.image.toDrive(**{
            'image': clipped_img,
            'folder':'gis',
            'scale': 10
        })
        task.start()

        # check on task
        while task.active():
            print('Polling for task (id: {}).'.format(task.id))
            time.sleep(5)

        return None

    # get url
    asset_url = clipped_img.getDownloadURL()

    return asset_url


def download_asset(url, asset_id):

    # get request
    r = requests.get(url, allow_redirects=True)

    # check file type
    filetype = r.headers.get('content-type')

    # if zip
    if('zip' in filetype):

        # Create a folder that contains all data files
        dir_path = os.path.join(data_dir_path, asset_id)
        if os.path.isdir(dir_path) == False:
            os.mkdir(dir_path)

        # read bytes
        filebytes = BytesIO(r.content)

        # unzip
        filenames = []
        with zipfile.ZipFile(filebytes, 'r') as zip_ref:

            # set files
            filenames = zip_ref.namelist()

            # extract
            zip_ref.extractall(dir_path)

        # compose
        if(len(filenames) > 1):

            # init bands
            bands = []

            for filename in filenames:

                # load grayscale band
                band_img = Image.open(os.path.join(dir_path, filename))

                # convert to numpy array
                band = np.asarray(band_img)

                # append
                bands.append(band)

            # stack bands
            canvas = np.dstack(bands)

            # save image
            img = Image.fromarray(canvas)
            img.save(os.path.join(dir_path, 'composed.png'))

    else:

        if('png' in filetype):
            asset_id = asset_id + '.png'
        elif('tif' in filetype):
            asset_id = asset_id + '.tif'
        else:
            print(filetype)

        # write to file
        outpath = os.path.join(data_dir_path, asset_id)
        open(outpath, 'wb').write(r.content)

    print(f'Download done {url}')
