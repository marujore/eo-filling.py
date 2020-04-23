# Python Native
from itertools import chain
from operator import sub
import logging
import os
import time

# 3rdparty
from matplotlib import pyplot as plt
from osgeo import gdal
import numpy
import rasterio


def set_values():
    ###WORK IN PROGRESS TEST DATASETS
    global input_targ_filename, input_ref_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename, out_dir
    input_targ_filename = '/home/marujo/git_hub/EO_filling_py/input/images/L7/20150810_L7/20150810_sr_band4.tif'
    input_ref_filename = '/home/marujo/git_hub/EO_filling_py/input/images/L8/20150802_L8/LC08_22KDF_20150802_sr_band5.tif'
    input_seg1_filename = '/home/marujo/git_hub/EO_filling_py/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_050.tif'
    input_seg2_filename = '/home/marujo/git_hub/EO_filling_py/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_100.tif'
    input_seg3_filename = '/home/marujo/git_hub/EO_filling_py/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_200.tif'
    out_dir = '/home/marujo/git_hub/EO_filling_py/output/'
    return


def get_from_set(value, myset):
    return myset[value] if value in myset else numpy.nan


def searchMissingValues(input_array):
    return list(set(range(input_array[len(input_array)-1])[0:]) - set(input_array))


def makeSegConsecutive(img_seg, missing_values):
    extra_values = set(img_seg) - set(range(len(img_seg)))
    cont = 0
    for value in extra_values:
        img_seg[img_seg == value] = missing_values[0]
        cont = cont + 1
    return img_seg


def optimizeSegmentation(img_seg):
    missing_values = searchMissingValues(img_seg)
    if len(missing_values) > 0:
        img_seg = makeSegConsecutive(img_seg, missing_values)


def get_gaps(img):
    gaps = numpy.argwhere(numpy.isnan(img))
    return(gaps)


def filling_preparation_marujo2019(input_targ_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename, input_ref_filename):
    print('Loading target image ...')
    with rasterio.open(input_targ_filename) as dataset:
        # print(dataset.profile)
        na = dataset.nodatavals
        print(na)
        img_targ = dataset.read(1)
        img_targ[img_targ < -100000] = numpy.nan
        # print(img_targ.shape)
        kwargs = dataset.meta

    gaps_targ = get_gaps(img_targ)
    ###Check if there are gaps to be filled
    if (len(gaps_targ) > 0):
        print('Loading reference image ...')
        with rasterio.open(input_ref_filename) as dataset:
            img_ref = dataset.read(1)
            img_ref[img_ref < -100000] = numpy.nan

        print('Loading Segmentation 1 image ...')
        with rasterio.open(input_seg1_filename) as dataset:
            img_seg1 = dataset.read(1)
            img_seg1[img_seg1 < -100000] = numpy.nan

        print('Loading Segmentation 2 image ...')
        with rasterio.open(input_seg2_filename) as dataset:
            img_seg2 = dataset.read(1)
            img_seg2[img_seg2 < -100000] = numpy.nan

        print('Loading Segmentation 3 image ...')
        with rasterio.open(input_seg3_filename) as dataset:
            img_seg3 = dataset.read(1)
            img_seg3[img_seg3 < -100000] = numpy.nan

        return(img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3, kwargs)
    else:
        print('Nothing to fill')
        return


def filling_preparation_maxwell2007(input_targ_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename):
    print('Loading target image ...')
    with rasterio.open(input_targ_filename) as dataset:
        # print(dataset.profile)
        na = dataset.nodatavals
        print(na)
        img_targ = dataset.read(1)
        img_targ[img_targ < -100000] = numpy.nan
        # print(img_targ.shape)
        kwargs = dataset.meta

    gaps_targ = get_gaps(img_targ)
    ### if there are gaps to be filled
    if (len(gaps_targ) > 0):
        print('Loading Segmentation 1 image ...')
        with rasterio.open(input_seg1_filename) as dataset:
            img_seg1 = dataset.read(1)
            img_seg1[img_seg1 < -100000] = numpy.nan

        print('Loading Segmentation 2 image ...')
        with rasterio.open(input_seg2_filename) as dataset:
            img_seg2 = dataset.read(1)
            img_seg2[img_seg2 < -100000] = numpy.nan

        print('Loading Segmentation 3 image ...')
        with rasterio.open(input_seg3_filename) as dataset:
            img_seg3 = dataset.read(1)
            img_seg3[img_seg3 < -100000] = numpy.nan

        return(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3, kwargs)
    else:
        print('Nothing to fill')
        return


def filling_preparation_singseg(input_targ_filename, input_seg1_filename):
    print('Loading target image ...')
    with rasterio.open(input_targ_filename) as dataset:
        # print(dataset.profile)
        na = dataset.nodatavals
        print(na)
        img_targ = dataset.read(1)
        img_targ[img_targ < -100000] = numpy.nan
        # print(img_targ.shape)
        kwargs = dataset.meta

    gaps_targ = get_gaps(img_targ)
    ### if there are gaps to be filled
    if (len(gaps_targ) > 0):
        print('Loading Segmentation 1 image ...')
        with rasterio.open(input_seg1_filename) as dataset:
            img_seg1 = dataset.read(1)
            img_seg1[img_seg1 < -100000] = numpy.nan

        return(img_targ, gaps_targ, img_seg1, kwargs)
    else:
        print('Nothing to fill')
        return


def fill_maxwell_2004(img_targ, img_seg1, gaps_targ=None):
    print('Fill Maxwell 2004')
    print('Searching for segments containing gaps...')
    if gaps_targ is None:
        gaps_targ = get_gaps(img_targ)
    ###Target nan pixels
    n_targ = numpy.isnan(img_targ)
    ###Not nan indices in target and in seg
    nn = ~(n_targ|numpy.isnan(img_seg1))
    ###Not nan target and seg
    img_targ_nn, img_seg1_nn = img_targ[nn], img_seg1[nn]
    ###unique, indices, count
    unq, idx, cnt = numpy.unique(img_seg1_nn,return_inverse=True,return_counts=True)
    ###Target segment mean values
    targ_seg_avg = dict(zip(unq,numpy.bincount(idx,img_targ_nn)/cnt))
    ###Get Segmentation pixels that were filled
    filled = img_seg1[n_targ]
    ###Get Filled values and fill target image
    get_from_set_vec = numpy.vectorize(get_from_set)
    img_targ[n_targ] = get_from_set_vec(filled, targ_seg_avg)

    return img_targ


def fill_maxwell_2007(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3):
    print('Fill Maxwell 2007')
    img_filled = fill_maxwell_2004(img_targ, img_seg1, gaps_targ)
    img_filled = fill_maxwell_2004(img_filled, img_seg2)
    img_filled = fill_maxwell_2004(img_filled, img_seg3)

    return img_targ


def fill_marujo(img_targ, img_ref, img_seg1, gaps_targ=None):
    print('Fill Marujo')
    print('Searching for segments containing gaps...')
    if gaps_targ is None:
        gaps_targ = get_gaps(img_targ)

    ###Target NaN pixels
    n_targ = numpy.isnan(img_targ)
    ###Not NaN indices in target and in seg
    nn = ~(n_targ|numpy.isnan(img_seg1))
    ###Not NaN on target, seg and ref
    img_targ_nn, img_seg1_nn, img_ref_nn = img_targ[nn], img_seg1[nn], img_ref[nn]
    #unique, indices, count
    unq, idx, cnt = numpy.unique(img_seg1_nn,return_inverse=True,return_counts=True)
    ###Target segment mean values
    targ_seg_avg = dict(zip(unq,numpy.bincount(idx,img_targ_nn)/cnt))
    #reference segment mean values
    ref_seg_avg = dict(zip(unq,numpy.bincount(idx,img_ref_nn)/cnt))

    ###Get Segmentation pixels that were filled
    filled = img_seg1[n_targ]
    ###Get Filled values and fill target image
    get_from_set_vec = numpy.vectorize(get_from_set)
    targ_avg = get_from_set_vec(filled, targ_seg_avg)
    ref_avg = get_from_set_vec(filled, ref_seg_avg)

    prop = img_ref[n_targ]/ref_avg
    img_targ[n_targ] = targ_avg * prop

    return img_targ


def fill_marujo_multseg(img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3):
    print('Fill Marujo Multseg')
    img_filled = fill_marujo(img_targ, img_ref, img_seg1, gaps_targ)
    img_filled = fill_marujo(img_filled, img_ref, img_seg2)
    img_filled = fill_marujo(img_filled, img_ref, img_seg3)

    return img_targ


def test_maxwell_2004():
    img_targ, gaps_targ, img_seg1, kwargs = filling_preparation_singseg(input_targ_filename, input_seg1_filename)
    img_filled = fill_maxwell_2004(img_targ, img_seg1, gaps_targ)
    filename = out_dir + os.path.basename(input_targ_filename)
    with rasterio.open(str(filename), 'w', **kwargs) as dst:
        dst.write_band(1, img_filled)
    return


def test_maxwell_2007():
    img_targ, gaps_targ, img_seg1, img_seg2, img_seg3, kwargs = filling_preparation_maxwell2007(input_targ_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename)
    img_filled = fill_maxwell_2007(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3)
    filename = out_dir + os.path.basename(input_targ_filename)
    with rasterio.open(str(filename), 'w', **kwargs) as dst:
        dst.write_band(1, img_filled)
    return


def test_marujo_2019():
    img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3, kwargs = filling_preparation_marujo2019(input_targ_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename, input_ref_filename)
    img_filled = fill_marujo_multseg(img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3)
    # img_filled = fill_marujo(img_targ, img_ref, img_seg1, gaps_targ)
    filename = out_dir + os.path.basename(input_targ_filename)
    with rasterio.open(str(filename), 'w', **kwargs) as dst:
        dst.write_band(1, img_filled)
    return


def main():
    # test_maxwell_2004()
    test_maxwell_2007()
    # test_marujo_2019()

if (__name__ == '__main__'):
    print('START [:')
    start = time.time()
    set_values()
    main()
    end = time.time()
    print('Duration time: {}'.format(end - start))
    print('END :]')
