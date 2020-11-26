#
# This file is part of eo-filling.py.
# Copyright (C) 2020 Rennan Marujo.
#
# eo-filling.py is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#


# Standard library imports
import logging
# Third party imports
import numpy
import rasterio
# Local application imports
from .utils import get_gaps, optimize_seg


def calc_mean_ts(ts_list):
    return numpy.mean(ts_list, axis=0)

def fill_temporal(list_img_path, multtemp_seg_path):
    multtemp_seg_ds = rasterio.open(multtemp_seg_path)
    multtemp_seg = multtemp_seg_ds.read(1)
    multtemp_seg = optimize_seg(multtemp_seg)

    # For each multi temporal segment
    for segment in numpy.arange(0,numpy.nanmax(multtemp_seg)+1):
        # TODO get segment window
        # Open each image using the window
        for img_path in list_img_path:
            # TODO Open each image using the window
            # TODO build window brick
            calc_mean_ts(img_brick)

        # TODO Extract each time series from the segment
        calc_mean_ts(segment_list)
        # TODO Fill NA using segment mean
