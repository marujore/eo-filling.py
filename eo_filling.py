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

# def get_valids(img):
#     valids = numpy.argwhere( ~numpy.isnan( img ) )
#     return( valids )

def fill_marujo_2019(img_targ, img_ref, img_seg1, img_seg2, img_seg3):
    print("Fill Marujo")
    
def test_marujo_2019():
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
        
        print("Loading Segmentation 1 image ...")
        with rasterio.open(input_seg1_filename) as dataset:
            # print(dataset.profile)
            img_seg1 = dataset.read(1)
            img_seg1[ img_seg1 < -100000 ] = numpy.nan

        print("Loading Segmentation 2 image ...")
        with rasterio.open(input_seg2_filename) as dataset:
            # print(dataset.profile)
            img_seg2 = dataset.read(1)
            img_seg2[ img_seg2 < -100000 ] = numpy.nan

        print("Loading Segmentation 3 image ...")
        with rasterio.open(input_seg3_filename) as dataset:
            # print(dataset.profile)
            img_seg3 = dataset.read(1)
            img_seg3[ img_seg3 < -100000 ] = numpy.nan

        img_filled = fill_marujo_2019(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3)
        filename = out_dir + os.path.basename(input_targ_filename)
        with rasterio.open( str(filename), 'w', **kwargs ) as dst:
            dst.write_band(1, img_filled)

def fill_maxwell_2007(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3):
    print("Fill Maxwell 2007")
    # print("gaps_targ.shape:{}".format(gaps_targ.shape))

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
            img_targ[ seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos] ] = numpy.nanmean(targ_values_seg)
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
                img_targ[ seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos] ] = numpy.nanmean(targ_values_seg)
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
                    img_targ[ seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos] ] = numpy.nanmean(targ_values_seg)
                else:
                    print("No fill")
    return img_targ

def test_maxwell_2007():
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
        
        print("Loading Segmentation 1 image ...")
        with rasterio.open(input_seg1_filename) as dataset:
            # print(dataset.profile)
            img_seg1 = dataset.read(1)
            img_seg1[ img_seg1 < -100000 ] = numpy.nan

        print("Loading Segmentation 2 image ...")
        with rasterio.open(input_seg2_filename) as dataset:
            # print(dataset.profile)
            img_seg2 = dataset.read(1)
            img_seg2[ img_seg2 < -100000 ] = numpy.nan

        print("Loading Segmentation 3 image ...")
        with rasterio.open(input_seg3_filename) as dataset:
            # print(dataset.profile)
            img_seg3 = dataset.read(1)
            img_seg3[ img_seg3 < -100000 ] = numpy.nan

        img_filled = fill_maxwell_2007(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3)
        filename = out_dir + os.path.basename(input_targ_filename)
        with rasterio.open( str(filename), 'w', **kwargs ) as dst:
            dst.write_band(1, img_filled)

def fill_maxwell_2004(img_targ, gaps_targ, img_seg1):
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
    

def test_maxwell_2004():
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
        
        print("Loading Segmentation 1 image ...")
        with rasterio.open(input_seg1_filename) as dataset:
            # print(dataset.profile)
            img_seg1 = dataset.read(1)
            img_seg1[ img_seg1 < -100000 ] = numpy.nan
            # print("img_seg1.shp:{}".format(img_seg1.shape) )
            # print(img_seg1[0,0])

        img_filled = fill_maxwell_2004(img_targ, gaps_targ, img_seg1)
        filename = out_dir + os.path.basename(input_targ_filename)
        with rasterio.open( str(filename), 'w', **kwargs ) as dst:
            dst.write_band(1, img_filled)        



def main():
    # test_maxwell_2004()
    test_maxwell_2007()


if (__name__ == '__main__'):
    print('START [:')
    start = time.time()
    main()
    end = time.time()
    print('Duration time: {}'.format(end - start))
    print('END :]')

#sys.exit(0)