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


def test_maxwell_2004(img_targ, img_seg, gaps_targ, kwargs, filename=None):
    img_filled = eo_filling.fill_maxwell_2004(img_targ, img_seg, gaps_targ)
    img_filled[numpy.isnan(img_filled)] = kwargs['nodata']
    with rasterio.open(str(filename), 'w', **kwargs) as dst:
        dst.write_band(1, img_filled.astype(kwargs['dtype']))
    return


def test_maxwell_2007(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3, kwargs, filename=None):
    img_filled = eo_filling.fill_maxwell_2007(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3)
    img_filled[numpy.isnan(img_filled)] = kwargs['nodata']
    with rasterio.open(str(filename), 'w', **kwargs) as dst:
        dst.write_band(1, img_filled.astype(kwargs['dtype']))
    return


def test_marujo_2019(img_targ, img_ref, img_seg1, img_seg2, img_seg3, gaps_targ, kwargs, filename=None):
    img_filled = eo_filling.fill_marujo_multseg(img_targ, img_ref, img_seg1, img_seg2, img_seg3, gaps_targ)
    img_filled[numpy.isnan(img_filled)] = kwargs['nodata']
    with rasterio.open(str(filename), 'w', **kwargs) as dst:
        dst.write_band(1, img_filled.astype(kwargs['dtype']))
    return


def main():
    input_targ_filename = '/home/marujo/git_hub/EO-filling.py/examples/multiseg/input/images/L7/L7_20150810_sr_band4.tif'
    input_ref_filename = '/home/marujo/git_hub/EO-filling.py/examples/multiseg/input/images/L8/LC08_22KDF_20150802_sr_band5.tif'
    input_seg1_filename = '/home/marujo/git_hub/EO-filling.py/examples/multiseg/input/segmentation/LC08_22KDF_20150802_seg_evi_050.tif'
    input_seg2_filename = '/home/marujo/git_hub/EO-filling.py/examples/multiseg/input/segmentation/LC08_22KDF_20150802_seg_evi_100.tif'
    input_seg3_filename = '/home/marujo/git_hub/EO-filling.py/examples/multiseg/input/segmentation/LC08_22KDF_20150802_seg_evi_200.tif'
    out_dir = '/home/marujo/git_hub/EO-filling.py/examples/multiseg/output/'


    print('Loading target image ...')
    with rasterio.open(input_targ_filename) as dataset:
        na = dataset.nodatavals
        img_targ = dataset.read(1).astype(float)
        img_targ[img_targ == na] = numpy.nan
        kwargs = dataset.meta
        print(kwargs)

    gaps_targ = eo_filling.get_gaps(img_targ)
    ###Check if there are gaps to be filled
    if (len(gaps_targ) <= 0):
        print('Nothing to fill')
        return
    else:
        print('Loading reference image ...')
        with rasterio.open(input_ref_filename) as dataset:
            img_ref = dataset.read(1).astype(float)
            img_targ[img_targ == na] = numpy.nan

        print('Loading Segmentation 1 image ...')
        with rasterio.open(input_seg1_filename) as dataset:
            img_seg1 = dataset.read(1).astype(float)
            img_targ[img_targ == na] = numpy.nan

        print('Loading Segmentation 2 image ...')
        with rasterio.open(input_seg2_filename) as dataset:
            img_seg2 = dataset.read(1).astype(float)
            img_targ[img_targ == na] = numpy.nan

        print('Loading Segmentation 3 image ...')
        with rasterio.open(input_seg3_filename) as dataset:
            img_seg3 = dataset.read(1).astype(float)
            img_targ[img_targ == na] = numpy.nan

    # test_maxwell_2004(img_targ, img_seg1, gaps_targ, kwargs, filename=out_dir+'filled_singleseg.tif')
    # test_maxwell_2007(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3, kwargs, filename=out_dir+'filled_multiseg.tif')
    test_marujo_2019(img_targ, img_ref, img_seg1, img_seg2, img_seg3, gaps_targ, kwargs, filename=out_dir+'filled_multiseg_pixelweight.tif')


if (__name__ == '__main__'):
    print('START [:')
    start = time.time()
    main()
    end = time.time()
    print('Duration time: {}'.format(end - start))
    print('END :]')
