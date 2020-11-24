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


def get_from_set(key, myset):
    """Get a set value given a key or numpy.nan if not found

    Args:
        key - key to search in set
        myset - a Set

    Returns:
        value or numpy.nan
    """
    return myset[key] if key in myset else numpy.nan


def get_gaps(img, nodata=numpy.nan):
    if numpy.isnan(nodata):
        return numpy.isnan(img)
    else:
        return img == nodata


def optimize_seg(input_array):
    """Optimize segmentation by checking if values are missing in Range of values and changing them case affirmative

    Args:
        img_seg - Array, Segmentation Image

    Returns:
        Array, with indices as Range 0:N, where N is the number of segments
    """
    logging.info('Optimizing Segmentation')
    # Search missing values
    arr = input_array.ravel()
    # Count unique values
    unique_values = set(numpy.unique(arr))
    unique_quantity = len(unique_values)
    desired_values = set(numpy.arange(unique_quantity))
    missing_values = list(desired_values - unique_values)
    if len(missing_values) > 0:
        count = 0
        extra_values = unique_values - desired_values
        for value in extra_values:
            input_array[input_array == value] = missing_values[count]
            count = count + 1

    return input_array
