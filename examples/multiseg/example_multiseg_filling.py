import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/marujo/git_hub/EO-filling.py')

# Python Native
import os
import time
from itertools import chain
from operator import sub
# 3rdparty
import numpy
import rasterio
from osgeo import gdal
#
from eo_filling.multiseg_filling import multiseg_filling as eo_filling


def set_values():
    ###WORK IN PROGRESS TEST DATASETS
    global input_targ_filename, input_ref_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename, out_dir
    input_targ_filename = '/home/marujo/git_hub/EO-filling.py/examples/input/images/L7/20150810_L7/20150810_sr_band4.tif'
    input_ref_filename = '/home/marujo/git_hub/EO-filling.py/examples/input/images/L8/20150802_L8/LC08_22KDF_20150802_sr_band5.tif'
    input_seg1_filename = '/home/marujo/git_hub/EO-filling.py/examples/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_050.tif'
    input_seg2_filename = '/home/marujo/git_hub/EO-filling.py/examples/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_100.tif'
    input_seg3_filename = '/home/marujo/git_hub/EO-filling.py/examples/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_200.tif'
    out_dir = '/home/marujo/git_hub/EO-filling.py/examples/output/'
    return


def filling_preparation_marujo2019(input_targ_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename, input_ref_filename):
    print('Loading target image ...')
    with rasterio.open(input_targ_filename) as dataset:
        na = dataset.nodatavals
        img_targ = dataset.read(1)
        img_targ[img_targ == na] = numpy.nan
        kwargs = dataset.meta

    gaps_targ = eo_filling.get_gaps(img_targ)
    ###Check if there are gaps to be filled
    if (len(gaps_targ) > 0):
        print('Loading reference image ...')
        with rasterio.open(input_ref_filename) as dataset:
            img_ref = dataset.read(1)
            img_ref[img_ref < -9999] = numpy.nan

        print('Loading Segmentation 1 image ...')
        with rasterio.open(input_seg1_filename) as dataset:
            img_seg1 = dataset.read(1)
            img_seg1[img_seg1 < -9999] = numpy.nan

        print('Loading Segmentation 2 image ...')
        with rasterio.open(input_seg2_filename) as dataset:
            img_seg2 = dataset.read(1)
            img_seg2[img_seg2 < -9999] = numpy.nan

        print('Loading Segmentation 3 image ...')
        with rasterio.open(input_seg3_filename) as dataset:
            img_seg3 = dataset.read(1)
            img_seg3[img_seg3 < -9999] = numpy.nan

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
        img_targ[img_targ < -9999] = numpy.nan
        # print(img_targ.shape)
        kwargs = dataset.meta

    gaps_targ = eo_filling.get_gaps(img_targ)
    ### if there are gaps to be filled
    if (len(gaps_targ) > 0):
        print('Loading Segmentation 1 image ...')
        with rasterio.open(input_seg1_filename) as dataset:
            img_seg1 = dataset.read(1)
            img_seg1[img_seg1 < -9999] = numpy.nan

        print('Loading Segmentation 2 image ...')
        with rasterio.open(input_seg2_filename) as dataset:
            img_seg2 = dataset.read(1)
            img_seg2[img_seg2 < -9999] = numpy.nan

        print('Loading Segmentation 3 image ...')
        with rasterio.open(input_seg3_filename) as dataset:
            img_seg3 = dataset.read(1)
            img_seg3[img_seg3 < -9999] = numpy.nan

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
        img_targ[img_targ < -9999] = numpy.nan
        # print(img_targ.shape)
        kwargs = dataset.meta

    gaps_targ = eo_filling.get_gaps(img_targ)
    ### if there are gaps to be filled
    if (len(gaps_targ) > 0):
        print('Loading Segmentation 1 image ...')
        with rasterio.open(input_seg1_filename) as dataset:
            img_seg = dataset.read(1)
            img_seg[img_seg < -9999] = numpy.nan

        return(img_targ, gaps_targ, img_seg, kwargs)
    else:
        print('Nothing to fill')
        return



def test_maxwell_2004():
    img_targ, gaps_targ, img_seg, kwargs = filling_preparation_singseg(input_targ_filename, input_seg1_filename)
    img_filled = eo_filling.fill_maxwell_2004(img_targ, img_seg, gaps_targ)
    filename = out_dir + os.path.basename(input_targ_filename)
    with rasterio.open(str(filename), 'w', **kwargs) as dst:
        dst.write_band(1, img_filled)
    return


def test_maxwell_2007():
    img_targ, gaps_targ, img_seg1, img_seg2, img_seg3, kwargs = filling_preparation_maxwell2007(input_targ_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename)
    img_filled = eo_filling.fill_maxwell_2007(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3)
    filename = out_dir + os.path.basename(input_targ_filename)
    with rasterio.open(str(filename), 'w', **kwargs) as dst:
        dst.write_band(1, img_filled)
    return


def test_marujo_2019():
    img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3, kwargs = filling_preparation_marujo2019(input_targ_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename, input_ref_filename)
    img_filled = eo_filling.fill_marujo_multseg(img_targ, img_ref, img_seg1, img_seg2, img_seg3, gaps_targ)
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
