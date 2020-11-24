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
# Local application imports
from .utils import get_from_set, get_gaps, optimize_seg


def fill_maxwell_2004(img_target, img_seg, n_target=None):
    """Fill image using segmentation (Maxwell et. al, 2004).

    Args:
        img_target - Array, Target Image (To be filled)
        img_seg - Array, Segmentation Image
        n_target - Array, optional bool array indicating pixels to be filled

    Returns:
        Array, Filled image
    """
    img_seg = optimize_seg(img_seg)
    if n_target is None:
        logging.info('Searching for segments containing gaps...')
        n_target = get_gaps(img_target)
    # Not nan indices in target and in seg
    nn = ~(n_target | numpy.isnan(img_seg))
    # Not nan target and seg
    img_target_nn, img_seg_nn = img_target[nn], img_seg[nn]
    # Unique, Indices, Count
    unq, idx, cnt = numpy.unique(img_seg_nn, return_inverse=True, return_counts=True)
    # Target segment mean values
    target_seg_avg = dict(zip(unq, numpy.bincount(idx, img_target_nn) / cnt))
    # Get Segmentation pixels that were filled
    filled = img_seg[n_target]
    # Get Filled values and fill target image
    get_from_set_vec = numpy.vectorize(get_from_set)
    img_target[n_target] = get_from_set_vec(filled, target_seg_avg)

    return img_target


def fill_maxwell_2007(img_target, seg_lists, gaps_target=None):
    """Fill image using multi-scale segmentation (Maxwell et. al, 2007).
    note: Filling is optimized by using all segment available on a segmentation level (first fill all small segments, than medium and larges consecutively),
    instead of changing segmentation level when no valid value is found within a segment.

    Args:
        img_targ - Array, Target Image (To be filled)
        seg_lists - Array, Hierarchical Segmentation Image with small area segments
        gaps_targ - Array, optional bool array indicating pixels to be filled

    Returns:
        Array, Filled image
    """
    logging.info('Fill image using multi-scale segmentation (Maxwell et. al, 2007)')
    img_filled = numpy.copy(img_target)
    for seg_list in seg_lists:
        img_filled = fill_maxwell_2004(img_filled, seg_list, gaps_target)

    return img_filled


def fill_marujo(img_target, img_ref, img_seg, n_target=None):
    """Fill image using segmentation through pixel weighting.

    Args:
        img_target - Array, Target Image (To be filled)
        img_ref - Array, Reference Image
        img_seg - Array, Segmentation Image
        n_target - Array, optional bool array indicating pixels to be filled

    Returns:
        Array, Filled image
    """
    img_seg = optimize_seg(img_seg)
    if n_target is None:
        logging.info('Searching for segments containing gaps...')
        n_target = get_gaps(img_target)
    # Not NaN indices in target and in seg
    nn = ~(n_target | numpy.isnan(img_seg))
    # Not NaN on target, seg and ref
    img_target_nn, img_seg_nn, img_ref_nn = img_target[nn], img_seg[nn], img_ref[nn]
    # unique, indices, count
    unq, idx, cnt = numpy.unique(img_seg_nn, return_inverse=True, return_counts=True)
    # Target segment mean values
    target_seg_avg = dict(zip(unq, numpy.bincount(idx, img_target_nn) / cnt))
    # reference segment mean values
    ref_seg_avg = dict(zip(unq, numpy.bincount(idx, img_ref_nn) / cnt))

    # Get Segmentation pixels that were filled
    filled = img_seg[n_target]
    # Get Filled values and fill target image
    get_from_set_vec = numpy.vectorize(get_from_set)
    target_avg = get_from_set_vec(filled, target_seg_avg)
    ref_avg = get_from_set_vec(filled, ref_seg_avg)

    # Calculate Pixel weight
    pixel_weight = (img_ref[n_target] / ref_avg) * target_avg
    img_target[n_target] = pixel_weight

    return img_target


def fill_marujo_multseg(img_target, img_ref, seg_lists, gaps_target=None):
    """Fill image using multi-scale segmentation through pixel weighting.

    Args:
        img_target - Array, Target Image (To be filled)
        img_ref - Array, Reference Image
        seg_lists - List, Hierarchical Segmentation Image sorted from small to large area segments
        gaps_target - Array, optional bool array indicating pixels to be filled

    Returns:
        Array, Filled image
    """
    logging.info('Fill image using multi-scale segmentation through pixel weighting (Marujo et. al, 2020)')
    img_filled = numpy.copy(img_target)
    for seg_list in seg_lists:
        img_filled = fill_marujo(img_filled, img_ref, seg_list, gaps_target)

    return img_filled
