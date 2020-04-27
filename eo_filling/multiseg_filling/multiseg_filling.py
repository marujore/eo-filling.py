# 3rdparty
import numpy
import rasterio


def get_from_set(key, myset):
    """Get a set value given a key or numpy.nan if not found

    Args:
        key - key to search in set
        myset - a Set

    Returns:
        value or numpy.nan
    """
    return myset[key] if key in myset else numpy.nan


# def searchMissingValues(input_array):
#     """Search for the values that are not within Range 0:x, where x is the max value of input_array

#     Args:
#         input_array - an Array

#     Returns:
#         Array, containing missing values
#     """
#     return list(set(range(input_array[len(input_array)-1])[0:]) - set(input_array))


# def makeSegConsecutive(img_seg, missing_values):
#     """Convert segmentation indices to make values consecutives

#     Args:
#         img_seg - Array, Segmentation Image
#         missing_values - Array, containing missing values

#     Returns:
#         Array, with indices as Range 0:N, where N is the number of segments
#     """
#     extra_values = set(img_seg) - set(range(len(img_seg)))
#     cont = 0
#     for value in extra_values:
#         img_seg[img_seg == value] = missing_values[0]
#         cont = cont + 1
#     return img_seg


# def optimizeSegmentation(img_seg):
#     """Optimize segmentation by checking if values are missing in Range of values and changing them case affirmative

#     Args:
#         img_seg - Array, Segmentation Image

#     Returns:
#         Array, with indices as Range 0:N, where N is the number of segments
#     """
#     missing_values = searchMissingValues(img_seg)
#     if len(missing_values) > 0:
#         img_seg = makeSegConsecutive(img_seg, missing_values)

#     return img_seg


def get_gaps(img):
    """Check position of numpy.nans

    Args:
        img - Array, Image

    Returns:
        Array (bool), indicating numpy.nans
    """
    gaps = numpy.argwhere(numpy.isnan(img))

    return(gaps)


def fill_maxwell_2004(img_targ, img_seg, gaps_targ=None):
    """Fill image using segmentation (Maxwell et. al, 2004).

    Args:
        img_targ - Array, Target Image (To be filled)
        img_seg - Array, Segmentation Image
        gaps_targ - Array, optional bool array indicating pixels to be filled

    Returns:
        Array, Filled image
    """
    print('Filling image using segmentation')
    if gaps_targ is None:
        print('Searching for segments containing gaps...')
        gaps_targ = get_gaps(img_targ)
    ###Target nan pixels
    n_targ = numpy.isnan(img_targ)
    ###Not nan indices in target and in seg
    nn = ~(n_targ|numpy.isnan(img_seg))
    ###Not nan target and seg
    img_targ_nn, img_seg_nn = img_targ[nn], img_seg[nn]
    ###unique, indices, count
    unq, idx, cnt = numpy.unique(img_seg_nn,return_inverse=True,return_counts=True)
    ###Target segment mean values
    targ_seg_avg = dict(zip(unq,numpy.bincount(idx,img_targ_nn)/cnt))
    ###Get Segmentation pixels that were filled
    filled = img_seg[n_targ]
    ###Get Filled values and fill target image
    get_from_set_vec = numpy.vectorize(get_from_set)
    img_targ[n_targ] = get_from_set_vec(filled, targ_seg_avg)

    return img_targ


def fill_maxwell_2007(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3):
    """Fill image using multi-scale segmentation (Maxwell et. al, 2007).
    note: Filling is optimized by using all segment available on a segmentation level (first fill all small segments, than medium and larges consecutively),
    instead of changing segmentation level when no valid value is found within a segment.

    Args:
        img_targ - Array, Target Image (To be filled)
        img_seg1 - Array, Hierarchical Segmentation Image with small area segments
        img_seg2 - Array, Hierarchical Segmentation Image with medium area segments
        img_seg3 - Array, Hierarchical Segmentation Image with large area segments
        gaps_targ - Array, optional bool array indicating pixels to be filled

    Returns:
        Array, Filled image
    """
    print('Fill image using multi-scale segmentation (Maxwell et. al, 2007)')
    img_filled = fill_maxwell_2004(img_targ, img_seg1, gaps_targ)
    img_filled = fill_maxwell_2004(img_filled, img_seg2, None)
    img_filled = fill_maxwell_2004(img_filled, img_seg3, None)

    return img_targ


def fill_marujo(img_targ, img_ref, img_seg, gaps_targ=None):
    """Fill image using segmentation through pixel weighting.

    Args:
        img_targ - Array, Target Image (To be filled)
        img_ref - Array, Reference Image
        img_seg - Array, Segmentation Image
        gaps_targ - Array, optional bool array indicating pixels to be filled

    Returns:
        Array, Filled image
    """
    if gaps_targ is None:
        print('Searching for segments containing gaps...')
        gaps_targ = get_gaps(img_targ)

    ###Target NaN pixels
    n_targ = numpy.isnan(img_targ)
    ###Not NaN indices in target and in seg
    nn = ~(n_targ|numpy.isnan(img_seg))
    ###Not NaN on target, seg and ref
    img_targ_nn, img_seg_nn, img_ref_nn = img_targ[nn], img_seg[nn], img_ref[nn]
    #unique, indices, count
    unq, idx, cnt = numpy.unique(img_seg_nn,return_inverse=True,return_counts=True)
    ###Target segment mean values
    targ_seg_avg = dict(zip(unq,numpy.bincount(idx,img_targ_nn)/cnt))
    #reference segment mean values
    ref_seg_avg = dict(zip(unq,numpy.bincount(idx,img_ref_nn)/cnt))

    ###Get Segmentation pixels that were filled
    filled = img_seg[n_targ]
    ###Get Filled values and fill target image
    get_from_set_vec = numpy.vectorize(get_from_set)
    targ_avg = get_from_set_vec(filled, targ_seg_avg)
    ref_avg = get_from_set_vec(filled, ref_seg_avg)

    ###Calculate Pixel weight
    pixel_weight = (img_ref[n_targ]/ref_avg) * targ_avg
    img_targ[n_targ] = pixel_weight

    return img_targ


def fill_marujo_multseg(img_targ, img_ref, img_seg1, img_seg2, img_seg3, gaps_targ=None):
    """Fill image using multi-scale segmentation through pixel weighting.

    Args:
        img_targ - Array, Target Image (To be filled)
        img_ref - Array, Reference Image
        img_seg1 - Array, Hierarchical Segmentation Image with small area segments
        img_seg2 - Array, Hierarchical Segmentation Image with medium area segments
        img_seg3 - Array, Hierarchical Segmentation Image with large area segments
        gaps_targ - Array, optional bool array indicating pixels to be filled

    Returns:
        Array, Filled image
    """
    print('Fill image using multi-scale segmentation through pixel weighting (Marujo et. al, 2020)')
    img_filled = fill_marujo(img_targ, img_ref, img_seg1, gaps_targ)
    img_filled = fill_marujo(img_filled, img_ref, img_seg2, None)
    img_filled = fill_marujo(img_filled, img_ref, img_seg3, None)

    return img_targ
