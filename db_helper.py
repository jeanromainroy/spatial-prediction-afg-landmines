################################################################################
#                                                                              #
# Functions to interact with the database                                      #
#                                                                              #
################################################################################

import numpy as np
import pandas as pd
import geopandas as gpd

from shapely.wkt import loads as wkt_loads

from sqlalchemy import create_engine

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


def get_incidents_count():
    """
        Returns the number of incidents
    """

    # SQL Query
    sql_query = 'SELECT COUNT(*) FROM incidents'

    count = 0
    with engine.connect() as connection:
        with connection.begin():

            # execute
            resultproxy = connection.execute(sql_query)

            # parse
            results = sqlresults_to_dict(resultproxy)

            # grab count
            count = results[0]['count']

    return count


def get_incidents(
        OFFSET=0,
        LIMIT=1000,
        BBOX_BUFFER=200,
        CRS='4326'
    ):
    """
        Returns the incidents. Geometries are returned as text
    """

    # SQL Query
    sql_query = f"""
        SELECT
            id,
            datetime,
            ST_AsText(ST_Transform(geometry, {CRS})) as location,
            info,
            Box2D(ST_Transform(ST_Buffer(geometry, {BBOX_BUFFER}), {CRS})) as bbox,
        FROM
            incidents
    """

    # run
    results = pd.read_sql_query(
        con=engine,
        sql=sql_query
    )

    # parse geometries
    results['location'] = results['location'].apply(wkt_loads)
    results['bbox'] = results['bbox'].apply(wkt_loads)

    # convert to geodataframe
    results = gpd.GeoDataFrame(results)

    return results
