# My Module

Takes an image and outputs 0/1


## Runtime

 - Python 3.6

 - OpenCV 4.2.0

 - NumPy


## Installation

To install this python package simply run this command,

    python3 setup.py install


## Usage

In a python script,

    # Import lib
    import my_module

    # run
    results = my_module.run(image_path)


## Deploying to AWS Lambda

Here are the instructions to deploy this package to Amazon Lambda.

### Setting up the lambda function runtime

 - Runtime : Python 3.6

 - Timeout : 5 min

 - Memory : 3008 MB

 - Handler : lambda_function.lambda_handler

 - Layer : opencv 4.2.0 with numpy

*to build a lambda layer containing opencv and numpy (https://github.com/tiivik/LambdaZipper)*


### Environment Variables

 - IMG_MAX_LENGTH :     2048

 - S3_ID :	            AK...

 - S3_SECRET :	        nQ...

 - SHARDED_PATH :       2-sharded/


### The code

Organize the files like this,

    meza-sharder/
        lambda_function.py
        app/
            __init__.py
            other.py
