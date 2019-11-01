#!/usr/bin/env python

import numpy
import rasterio
import time

from matplotlib import pyplot as plt
from osgeo import gdal

def get_gaps(img):
    gaps = numpy.argwhere( numpy.isnan( img ) )
    # print(gaps[0,:])
    return( gaps )

def fillMarujo2019(img_targ, img_ref, img_seg1, img_seg2, img_seg3):
    print("Fill Marujo")
    

def fillMaxwell2007(img_targ, img_ref, img_seg1, img_seg2, img_seg3):
    print("Fill Maxwell 2007")
    

def fillMaxwell2004(img_targ, gaps_targ, img_ref, gaps_ref, img_seg1):
    print("Fill Maxwell 2004")
    # print(gaps_targ.shape)
    # print(gaps_targ[1000,0])
    segments = numpy.unique( img_seg1[ gaps_targ[:,0], gaps_targ[:,1] ] )
    print( len( segments) )
    print(segments)
    
    


def main():
    input_targ_filename = "/home/marujo/Marujo/EO_filling_py/input/images/L7/20150810_L7/20150810_sr_band4.tif"
    input_ref_filename = "/home/marujo/Marujo/EO_filling_py/input/images/L8/20150802_L8/LC08_22KDF_20150802_sr_band5.tif"
    input_seg1_filename = "/home/marujo/Marujo/EO_filling_py/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_050.tif"
    input_seg2_filename = "/home/marujo/Marujo/EO_filling_py/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_100.tif"
    input_seg3_filename = "/home/marujo/Marujo/EO_filling_py/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_200.tif"

    print("Loading target image ...")
    with rasterio.open(input_targ_filename) as dataset:
        # print(dataset.profile)
        na = dataset.nodatavals
        print(na)
        img_targ = dataset.read(1)
        img_targ[ img_targ < -100000 ] = numpy.nan
        # print(img_targ.shape)

    gaps_targ = get_gaps(img_targ)
    ### if there are gaps to be filled
    if ( len(gaps_targ) > 0 ):
        print("Loading reference image ...")
        with rasterio.open(input_ref_filename) as dataset:
            # print(dataset.profile)
            img_ref = dataset.read(1)
            img_ref[ img_ref < -100000 ] = numpy.nan
            # print(img_ref.shape)
        
        gaps_ref = get_gaps(img_ref)
        ### if ref has valid value in targ gap
        if( numpy.any( numpy.in1d(gaps_targ, gaps_ref, invert= True) ) ):
            print("Loading Segmentation 1 image ...")
            with rasterio.open(input_seg1_filename) as dataset:
                # print(dataset.profile)
                img_seg1 = dataset.read(1)
                img_seg1[ img_seg1 < -100000 ] = numpy.nan
                # print(img_seg1.shape)

            fillMaxwell2004(img_targ, gaps_targ, img_ref, gaps_ref, img_seg1)


if (__name__ == '__main__'):
    print('START [:')
    start = time.time()
    main()
    end = time.time()
    print('Duration time: {}'.format(end - start))
    print('END :]')

#sys.exit(0)