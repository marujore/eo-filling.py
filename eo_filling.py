#!/usr/bin/env python

import numpy
import os
import rasterio
import time

from matplotlib import pyplot as plt
from osgeo import gdal

def get_gaps(img):
    gaps = numpy.argwhere( numpy.isnan( img ) )
    # print("get_gaps:{}".format(gaps[0,:]))
    return( gaps )

def get_valids(img):
    valids = numpy.argwhere( ~numpy.isnan( img ) )
    return( valids )

def fillMarujo2019(img_targ, img_ref, img_seg1, img_seg2, img_seg3):
    print("Fill Marujo")
    

def fillMaxwell2007(img_targ, img_ref, img_seg1, img_seg2, img_seg3):
    print("Fill Maxwell 2007")
    # print("gaps_targ.shape:{}".format(gaps_targ.shape))
    print( img_targ[gaps_targ[0,0], gaps_targ[0,1]] )

    print("Searching for segments containing gaps...")
    ### Get which segments contains NA on target image
    indices_gap_targ = numpy.array( list( zip(gaps_targ[:,0], gaps_targ[:,1] ) ) )
    segments_targ = img_seg1[ indices_gap_targ[:,0], indices_gap_targ[:,1] ]
    segments_targ = numpy.unique( segments_targ[~numpy.isnan( segments_targ )] )
    print( "len segs:{}".format( len( segments_targ) ) )
    print( "segs containing na:{}".format( segments_targ[0] ) )

    # print("Searching for reference segments...")
    # valids_ref = get_valids( img_ref )
    # ### Get which segments contains NA on reference image
    # indices_valid_ref = numpy.array( list( zip(valids_ref[:,0], valids_ref[:,1] ) ) )
    # segments_ref = img_seg1[ indices_valid_ref[:,0], indices_valid_ref[:,1] ]
    # segments_ref = numpy.unique( segments_ref[~numpy.isnan( segments_ref )] )
    
    # print("Calculating intersection ...")
    # segments = numpy.intersect1d(segments_targ, segments_ref)

    # print("Gap-filling ... ({})".format(len(segments)))
    ### Filter segs img ref
    last_seg = numpy.nanmax(segments_targ)
    for seg in segments_targ:
    # seg = 20
    # if seg ==20:
        # print( "TEST bfr: {}".format(img_targ[17,31]) )
        print( "Seg:{} of {}".format(seg, last_seg) )
        ### Get seg pixel position
        seg_pixels = numpy.nonzero( img_seg1 == seg )
        # print("Seg_pixels:{}".format(seg_pixels))
        seg_indices = numpy.array( list( zip(seg_pixels[:][0], seg_pixels[:][1] ) ) )
        # print("Seg indices: {}".format(seg_indices))
        ### Get targ pix values
        targ_values_seg = img_targ[ seg_indices[:,0], seg_indices[:,1] ]
        ### Check if any is not nan
        if( numpy.any( ~numpy.isnan(targ_values_seg) ) ):
            # print("Filling ..")
            ### Get nan position and replace by mean value
            nan_pos = numpy.isnan( targ_values_seg )
            # print("targ_values_seg: {}".format(img_targ[ seg_indices[:,0], seg_indices[:,1] ]))
            # print("nan_pos: {}".format( nan_pos ))
            # print("targ_values_seg_nanpos: {}".format(img_targ[ seg_indices[:,0], seg_indices[:,1] ][nan_pos]))
            # print("mean:{}".format(numpy.nanmean(targ_values_seg)))
            img_targ[ seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos] ] = numpy.nanmean(targ_values_seg)
        # print("targ_values_seg_after: {}".format(img_targ[ seg_indices[:,0], seg_indices[:,1] ]))
        # print( "TEST after: {}".format(img_targ[17,31]) )
    return img_targ

def fillMaxwell2004(img_targ, gaps_targ, img_ref, gaps_ref, img_seg1):
    print("Fill Maxwell 2004")
    # print("gaps_targ.shape:{}".format(gaps_targ.shape))
    print( img_targ[gaps_targ[0,0], gaps_targ[0,1]] )

    ### Get which segments contains NA on target image
    print("Searching for segments containing gaps...")
    indices_gap_targ = numpy.array( list( zip(gaps_targ[:,0], gaps_targ[:,1] ) ) )
    segments_targ = img_seg1[ indices_gap_targ[:,0], indices_gap_targ[:,1] ]
    segments_targ = numpy.unique( segments_targ[~numpy.isnan( segments_targ )] )
    print( "len segs:{}".format( len( segments_targ) ) )
    print( "segs containing na:{}".format( segments_targ[0] ) )

    last_seg = numpy.nanmax(segments_targ)
    for seg in segments_targ:
        print( "Seg:{} of {}".format(seg, last_seg) )
        ### Get seg pixel position
        seg_pixels = numpy.nonzero( img_seg1 == seg )
        seg_indices = numpy.array( list( zip(seg_pixels[:][0], seg_pixels[:][1] ) ) )
        ### Get targ pix values
        targ_values_seg = img_targ[ seg_indices[:,0], seg_indices[:,1] ]
        ### Check if any is not nan
        if( numpy.any( ~numpy.isnan(targ_values_seg) ) ):
            ### Get nan position and replace by mean value
            nan_pos = numpy.isnan( targ_values_seg )
            img_targ[ seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos] ] = numpy.nanmean(targ_values_seg)
    return img_targ
    

        

def main():
    input_targ_filename = "/home/marujo/Marujo/EO_filling_py/input/images/L7/20150810_L7/20150810_sr_band4.tif"
    input_ref_filename = "/home/marujo/Marujo/EO_filling_py/input/images/L8/20150802_L8/LC08_22KDF_20150802_sr_band5.tif"
    input_seg1_filename = "/home/marujo/Marujo/EO_filling_py/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_050.tif"
    input_seg2_filename = "/home/marujo/Marujo/EO_filling_py/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_100.tif"
    input_seg3_filename = "/home/marujo/Marujo/EO_filling_py/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_200.tif"

    out_dir = "/home/marujo/Marujo/EO_filling_py/output/"

    print("Loading target image ...")
    with rasterio.open(input_targ_filename) as dataset:
        # print(dataset.profile)
        na = dataset.nodatavals
        print(na)
        img_targ = dataset.read(1)
        img_targ[ img_targ < -100000 ] = numpy.nan
        # print(img_targ.shape)
        kwargs = dataset.meta

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
        print("Loading Segmentation 1 image ...")
        with rasterio.open(input_seg1_filename) as dataset:
            # print(dataset.profile)
            img_seg1 = dataset.read(1)
            img_seg1[ img_seg1 < -100000 ] = numpy.nan
            # print("img_seg1.shp:{}".format(img_seg1.shape) )
            # print(img_seg1[0,0])

        img_filled = fillMaxwell2004(img_targ, gaps_targ, img_ref, gaps_ref, img_seg1)
        filename = out_dir + os.path.basename(input_targ_filename)
        with rasterio.open( str(filename), 'w', **kwargs ) as dst:
            dst.write_band(1, img_filled)


if (__name__ == '__main__'):
    print('START [:')
    start = time.time()
    main()
    end = time.time()
    print('Duration time: {}'.format(end - start))
    print('END :]')

#sys.exit(0)