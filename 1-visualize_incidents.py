import os

# Lib for tabular data processing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Lib to import our accidents data
import db_helper

# Find the current working directory
path = os.getcwd()

# Grab path to figures folder
if os.path.isdir(os.path.join(path, 'Figures')) == False:
    raise Exception('Figures directory does not exist, run retrieve script')
figures_dir_path = os.path.join(path, 'Figures')


def draw_as_pdf(geometries, out_path):
    """
        Function to draw geometries on a pdf
    """

    if os.path.exists(out_path) == False:

        # plot
        fig, ax = plt.subplots()
        geometries.plot(ax=ax, color='teal', markersize=0.1)
        ax.set_axis_off()
        fig.tight_layout()
        fig.savefig(out_path, format='pdf')
        plt.close()


################################################################################
#                                                                              #
#                  Loading a sample the processed incidents                    #
#                                                                              #
################################################################################

# set crs
bbox_crs = '4326'

# Load the data
df = db_helper.get_incidents(OFFSET=0, LIMIT=10000, CRS=bbox_crs)

# Keep certain columns
df = df.loc[:, ['index', 'geometry']]

# outpath
out_path = os.path.join(figures_dir_path, 'incidents.pdf')

# write
draw_as_pdf(df, out_path)
