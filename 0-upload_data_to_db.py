# Import libraries
import os
import datetime
import json

import pandas as pd
import numpy as np
import geopandas as gpd

from shapely.geometry import Point, Polygon

from sqlalchemy import create_engine, types
from sqlalchemy.dialects import postgresql as postgresTypes
from geoalchemy2.types import Geometry as geoTypes

# Lib to work with .tif
import imagery_helper

# Set up database connection engine
from config import username, password, hostname, port, db_name
engine = create_engine(
    f'postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{db_name}',
    connect_args={'options': '-csearch_path={}'.format('public')}
)

# Find the current working directory
path = os.getcwd()

# Grab path to figures folder
if os.path.isdir(os.path.join(path, 'Figures')) == False:
    raise Exception('Figures directory does not exist, run retrieve script')
figures_dir_path = os.path.join(path, 'Figures')

# Grab path to data folder
if os.path.isdir(os.path.join(path, 'Data')) == False:
    raise Exception('Data directory does not exist, run retrieve script')
data_dir_path = os.path.join(path, 'Data')

def execute_query(query):
    """
        Executes a SQL query on the database
    """

    with engine.connect() as connection:
        with connection.begin():
            connection.execute(query)


################################################################################
#                                                                              #
#                           create the tables                                  #
#                                                                              #
################################################################################

# drop tables
for d in ['incidents', 'imagery']:
    drop_query = f'DROP TABLE IF EXISTS {d} CASCADE'
    execute_query(drop_query)

# create tables queries
create_table_imagery = f"""
        CREATE TABLE imagery (
            index INT GENERATED ALWAYS AS IDENTITY,
            filename character varying(2048) NOT NULL,
            datetime TIMESTAMP without time zone NOT NULL,
            geometry geometry(POLYGON,4326) NOT NULL,
            info JSONB NOT NULL,
            PRIMARY KEY(index)
        )
        """

# create tables queries
create_table_incidents = f"""
        CREATE TABLE incidents (
            index INT GENERATED ALWAYS AS IDENTITY,
            datetime TIMESTAMP without time zone NOT NULL,
            geometry geometry(POINT,4326) NOT NULL,
            info character varying(2048) NOT NULL,
            PRIMARY KEY(index)
        )
        """

# execute
execute_query(create_table_incidents)
execute_query(create_table_imagery)



################################################################################
#                                                                              #
#                        upload the landmine incidents                         #
#                                                                              #
################################################################################

# Load the data
landmines_df = pd.read_csv(os.path.join(data_dir_path, 'landmines.csv'))

# Redefine the types of the date and time columns
landmines_df.loc[:, 'datetime'] = pd.to_datetime(landmines_df.datetime, format='%Y')

# remove invalid rows
landmines_df = landmines_df[landmines_df['datetime'].notna()]

# Convert the data frame to a geo data frame
landmines_gdf = gpd.GeoDataFrame(landmines_df, crs='EPSG:4326', geometry=gpd.points_from_xy(landmines_df.longitude, landmines_df.latitude))

# Drop the lat/lng column
landmines_gdf = landmines_gdf.drop(['latitude', 'longitude'], axis=1)

# Reset the data frame's index
landmines_gdf = landmines_gdf.reset_index(drop=True)

# add to database
landmines_gdf.to_postgis(
    con=engine,
    name='incidents',
    if_exists='append',
    dtype={
        'info': types.Text(),
        'datetime': types.DateTime(),
        'geometry': geoTypes(geometry_type='POINT', srid=4326)
    }
)


################################################################################
#                                                                              #
#                            upload the imagery                                #
#                                                                              #
################################################################################

# list of imagey
imagery_paths = [os.path.join(figures_dir_path, 'kandahar-compressed.tif')]

# init imagery dict
imagery_dict = []

# go through
for imagery_path in imagery_paths:

    # grab filename
    filename = os.path.basename(imagery_path)

    # load using rasterio
    satdat = imagery_helper.load(imagery_path)

    # parse crs
    crs = str(satdat.read_crs()).split(':')[-1]

    # grab meta data
    metadata = dict(**satdat.profile)

    # convert to json
    metadata.update(crs=crs, transform=list(metadata["transform"]))
    info = json.dumps(metadata)

    # Get bounds, in map units
    bound_left = satdat.bounds.left
    bound_right = satdat.bounds.right
    bound_top = satdat.bounds.top
    bound_bottom = satdat.bounds.bottom

    # convert to points
    p1 = (bound_left, bound_top)
    p2 = (bound_right, bound_top)
    p3 = (bound_right, bound_bottom)
    p4 = (bound_left, bound_bottom)
    p5 = (bound_left, bound_top)

    # convert to polygon
    bb_polygon = Polygon([p1, p2, p3, p4, p5])

    # append to dict
    imagery_dict.append({
        'filename': filename,
        'info': info,
        'datetime': '2004',
        'geometry': bb_polygon
    })


# convert imagery dict to geodataframe
imagery_gdf = gpd.GeoDataFrame(imagery_dict, crs=f"EPSG:{crs}")

# Redefine the types of the date and time columns
imagery_gdf.loc[:, 'datetime'] = pd.to_datetime(imagery_gdf.datetime, format='%Y')

# Reset the data frame's index
imagery_gdf = imagery_gdf.reset_index(drop=True)

# add to database
imagery_gdf.to_postgis(
    con=engine,
    name='imagery',
    if_exists='append',
    dtype={
        'filename': types.Text(),
        'datetime': types.DateTime(),
        'geometry': geoTypes(geometry_type='POLYGON', srid=crs),
        'info': postgresTypes.JSONB
    }
)
