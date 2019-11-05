#!/usr/bin/env python

import numpy
import rasterio
import time

from matplotlib import pyplot as plt
from osgeo import gdal

def get_gaps(img):
    gaps = numpy.argwhere( numpy.isnan( img ) )
    # print("get_gaps:{}".format(gaps[0,:]))
    return( gaps )

def fillMarujo2019(img_targ, img_ref, img_seg1, img_seg2, img_seg3):
    print("Fill Marujo")
    

def fillMaxwell2007(img_targ, img_ref, img_seg1, img_seg2, img_seg3):
    print("Fill Maxwell 2007")
    

def fillMaxwell2004(img_targ, gaps_targ, img_ref, gaps_ref, img_seg1):
    print("Fill Maxwell 2004")
    print("gaps_targ.shape:{}".format(gaps_targ.shape))
    print( img_targ[gaps_targ[0,0], gaps_targ[0,1]] )

    indices = numpy.array( list( zip(gaps_targ[:,0], gaps_targ[:,1] ) ) )
    ### Get segments which contains NA
    segments = img_seg1[ indices[:,0], indices[:,1] ]
    segments = numpy.unique( segments[~numpy.isnan( segments )] )
    print( "len segs:{}".format( len( segments) ) )
    
    #filter segs img ref
    # for seg in segments:
    seg = 1
    if seg ==1:
        print( "TEST bfr: {}".format(img_targ[0,81]) )
        print( "Seg:{}".format(seg) )
        ### Get seg pixel position
        seg_pixels = numpy.nonzero( img_seg1 == seg )
        seg_indices = numpy.array( list( zip(seg_pixels[:][0], seg_pixels[:][1] ) ) )
        print("Seg indices: {}".format(seg_indices))
        ### Get targ pix values
        targ_values_seg = img_targ[ seg_indices[:,0], seg_indices[:,1] ]
        ### Check if any is not nan
        if( numpy.any( ~numpy.isnan(targ_values_seg) ) ):
            print("There are no nan to use")
            ### Get nan position and replace by mean value
            nan_pos = numpy.isnan( targ_values_seg )
            img_targ[ seg_indices[:,0], seg_indices[:,1] ][nan_pos] = numpy.nanmean(targ_values_seg)
        print(seg_indices[:,0], seg_indices[:,1])
        print( "TEST after: {}".format(img_targ[0,81]) )
    

        

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
                print("img_seg1.shp:{}".format(img_seg1.shape) )
                # print(img_seg1[0,0])

            fillMaxwell2004(img_targ, gaps_targ, img_ref, gaps_ref, img_seg1)


if (__name__ == '__main__'):
    print('START [:')
    start = time.time()
    main()
    end = time.time()
    print('Duration time: {}'.format(end - start))
    print('END :]')

#sys.exit(0)