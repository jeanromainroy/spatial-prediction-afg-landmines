# Import libraries
import os
import datetime

import pandas as pd
import numpy as np
import geopandas as gpd

from sqlalchemy import create_engine, types
from sqlalchemy.dialects import postgresql as postgresTypes
from geoalchemy2.types import Geometry as geoTypes

# Append parent folder
import sys
sys.path.insert(0,'..')

# Set up database connection engine
from config import username, password, hostname, port, db_name
engine = create_engine(
    f'postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{db_name}',
    connect_args={'options': '-csearch_path={}'.format('public')}
)

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
for d in ['incidents']:
    drop_query = f'DROP TABLE IF EXISTS {d} CASCADE'
    execute_query(drop_query)

# create tables queries
create_table_incidents = f"""
        CREATE TABLE incidents (
            id INT GENERATED ALWAYS AS IDENTITY,
            datetime TIMESTAMP without time zone NOT NULL,
            geometry geometry(POINT,4236) NOT NULL,
            info character varying(2048) NOT NULL,
            PRIMARY KEY(id)
        )
        """

# execute
execute_query(create_table_incidents)


################################################################################
#                                                                              #
#                              weather stations                                #
#                                                                              #
################################################################################

# Load the data
landmines_df = pd.read_csv('landmines.csv')

# Redefine the types of the date and time columns
landmines_df.loc[:, 'datetime'] = pd.to_datetime(landmines_df.datetime, format='%Y')

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
    if_exists='replace',
    dtype={
        'info': types.Text(),
        'datetime': types.DateTime(),
        'geometry': geoTypes(geometry_type='POINT', srid=4326)
    }
)
