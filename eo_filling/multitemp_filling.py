#
# This file is part of eo-filling.py.
# Copyright (C) 2020 Rennan Marujo.
#
# eo-filling.py is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#


import numpy
import os
import rasterio
import time

from matplotlib import pyplot as plt
from osgeo import gdal

#TODO import from core utils
def get_gaps(img):
    gaps = numpy.argwhere( numpy.isnan( img ) )
    return( gaps )

def calc_mean_ts(ts_list):
    

def fill_temporal(img_targ, img_seg):
    ### Get which segments contains NA on target image
    print("Searching for segments containing gaps...")
    indices_gap_targ = numpy.array( list( zip(gaps_targ[:,0], gaps_targ[:,1] ) ) )
    segments_targ = img_seg1[ indices_gap_targ[:,0], indices_gap_targ[:,1] ]
    segments_targ = numpy.unique( segments_targ[~numpy.isnan( segments_targ )] )
    print( "len segs:{}".format( len( segments_targ) ) )
    print( "segs containing na:{}".format( segments_targ[0] ) )

    ### Filter segs img ref
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
            print("fill L1")
            nan_pos = numpy.isnan( targ_values_seg )
            ref_values_seg = img_ref[ seg_indices[:,0], seg_indices[:,1] ]
            mean_ref = numpy.nanmean(ref_values_seg)
            pixel_weight = ref_values_seg/mean_ref
            img_targ[ seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos] ] = numpy.nanmean(targ_values_seg) * pixel_weight[nan_pos]
        ### Otherwise uses segmentation level above
        else:
            seg_num = img_seg2[ seg_indices[0,0], seg_indices[0,1] ]
            ### Get seg pixel position
            seg_pixels = numpy.nonzero( img_seg2 == seg_num )
            seg_indices = numpy.array( list( zip(seg_pixels[:][0], seg_pixels[:][1] ) ) )
            ### Get targ pix values
            targ_values_seg = img_targ[ seg_indices[:,0], seg_indices[:,1] ]
            ### Check if any is not nan
            if( numpy.any( ~numpy.isnan(targ_values_seg) ) ):
                ### Get nan position and replace by mean value
                print("fill L2")
                nan_pos = numpy.isnan( targ_values_seg )
                ref_values_seg = img_ref[ seg_indices[:,0], seg_indices[:,1] ]
                mean_ref = numpy.nanmean(ref_values_seg)
                pixel_weight = ref_values_seg/mean_ref
                img_targ[ seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos] ] = numpy.nanmean(targ_values_seg) * pixel_weight[nan_pos]
            ### Otherwise uses segmentation level above
            else:
                seg_num = img_seg3[ seg_indices[0,0], seg_indices[0,1] ]
                ### Get seg pixel position
                seg_pixels = numpy.nonzero( img_seg3 == seg_num )
                seg_indices = numpy.array( list( zip(seg_pixels[:][0], seg_pixels[:][1] ) ) )
                ### Get targ pix values
                targ_values_seg = img_targ[ seg_indices[:,0], seg_indices[:,1] ]
                ### Check if any is not nan
                if( numpy.any( ~numpy.isnan(targ_values_seg) ) ):
                    ### Get nan position and replace by mean value
                    print("fill L3")
                    nan_pos = numpy.isnan( targ_values_seg )
                    ref_values_seg = img_ref[ seg_indices[:,0], seg_indices[:,1] ]
                    mean_ref = numpy.nanmean(ref_values_seg)
                    pixel_weight = ref_values_seg/mean_ref
                    img_targ[ seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos] ] = numpy.nanmean(targ_values_seg) * pixel_weight[nan_pos]
                else:
                    print("No fill")
    return img_targ

def test_temporal():
    input_targ_filename = "/home/marujo/Marujo/EO_filling_py/input/images/L7/20150810_L7/20150810_sr_band4.tif"
    input_seg_filename = "/home/marujo/Marujo/EO_filling_py/input/segmentation/L8/LC0820150802/LC08_22KDF_20150802_sr_evi_050.tif"
    
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
        print("Loading Segmentation image ...")
        with rasterio.open(input_seg_filename) as dataset:
            # print(dataset.profile)
            img_seg1 = dataset.read(1)
            img_seg1[ img_seg1 < -100000 ] = numpy.nan

        img_filled = fill_marujo_2019(img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3)
        filename = out_dir + os.path.basename(input_targ_filename)
        with rasterio.open( str(filename), 'w', **kwargs ) as dst:
            dst.write_band(1, img_filled)

def main():
    test_temporal()

if (__name__ == '__main__'):
    print('START [:')
    start = time.time()
    main()
    end = time.time()
    print('Duration time: {}'.format(end - start))
    print('END :]')

#sys.exit(0)