# Add path to opencv
import sys
sys.path.append('/opt/')

# other libs
import json
import os
import shutil
import tempfile
import boto3

import numpy as np
import cv2 as cv


from app.__init__ import run as my_module

# Load env variables
S3_ID = os.environ['S3_ID']
S3_SECRET = os.environ['S3_SECRET']
SHARDED_PATH = os.environ['SHARDED_PATH']


def clear_tmp():
    """
        Clears the temp folder
    """

    folder = '/tmp'
    for filename in os.listdir(folder):

        if('.pt' in filename):
            continue

        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))



def get_image(bucket, image_key):
    """
        Get the image from the S3 bucket
    """

    # request object from S3
    response = bucket.Object(key=image_key).get()

    # grab image
    imgBytes = response['Body'].read()

    # Init temp file
    tmp = tempfile.NamedTemporaryFile()

    # save file to temp folder
    with open(tmp.name, 'wb') as fh:
        fh.write(imgBytes)

    # load image file with opencv
    img = cv.imread(tmp.name)

    # if could not load
    if(img is None or type(img) is not np.ndarray):
        img = None

    return img, tmp.name


def upload_image(bucket, file_path, file_name):
    """
        Upload the image to the S3 bucket
    """
    bucket.upload_file(file_path, file_name)


def lambda_handler(event, context):

    # grab inputs from body
    if('bucket_name' not in event or 'image_id' not in event):
        return {
            'statusCode': 400,
            'body': json.dumps('Missing inputs')
        }

    bucket_name = event['bucket_name']
    image_id = event['image_id']

    # validate
    if(bucket_name is None or type(bucket_name) is not str or len(bucket_name) == 0):
        return {
            'statusCode': 400,
            'body': json.dumps('Bucket name invalid')
        }

    if(image_id is None or type(image_id) is not str or len(image_id) == 0):
        return {
            'statusCode': 400,
            'body': json.dumps('image id invalid')
        }


    # init bucket
    s3 = boto3.resource(
        service_name='s3',
        aws_access_key_id=S3_ID,
        aws_secret_access_key=S3_SECRET
    )
    bucket = s3.Bucket(bucket_name)


    # get image
    try:
        img, img_path = get_image(bucket, f'{SHARDED_PATH}{image_id}/src.jpg')
    except:
        return {
            'statusCode': 500,
            'body': json.dumps('Error occurred when trying to load the image')
        }

    # if could not load
    if(img is None):
        return {
            'statusCode': 500,
            'body': json.dumps('Could not load image')
        }


    # ------------------------------------------------------------------------------------------------
    # --------------------------------- Start Doing Stuff --------------------------------------------
    # ------------------------------------------------------------------------------------------------


    # clear tmp folder
    clear_tmp()

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
