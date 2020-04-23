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


def filling_preparation_multseg(input_targ_filename, input_ref_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename, out_dir):
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

        return(img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3, out_dir, kwargs, input_targ_filename)
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


def fill_marujo_2019(img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3):
    print('Fill Marujo')
    print('Searching for segments containing gaps...')
    seg_num = numpy.nanmax(img_seg1)
    indices_gap_targ = numpy.array(list(zip(gaps_targ[:,0], gaps_targ[:,1])))
    segments_targ = img_seg1[indices_gap_targ[:,0], indices_gap_targ[:,1]]
    segments_targ = numpy.unique(segments_targ[~numpy.isnan(segments_targ)])
    print('len segs:{}'.format(len(segments_targ)))
    print('segs containing na:{}'.format(segments_targ[0]))

    #target nan pixels
    n_targ = numpy.isnan(img_targ)
    #not nan indices in target and in seg
    nn = ~(n_targ|numpy.isnan(img_seg1))
    #not nan target and seg
    img_targ_nn, img_seg1_nn, img_ref_nn = img_targ[nn], img_seg1[nn], img_ref[nn]
    #unique, indices, count
    unq, idx, cnt = numpy.unique(img_seg1_nn,return_inverse=True,return_counts=True)
    #target segment mean values
    targ_seg_avg = dict(zip(unq,numpy.bincount(idx,img_targ_nn)/cnt))
    #reference segment mean values
    ref_seg_avg = dict(zip(unq,numpy.bincount(idx,img_ref_nn)/cnt))

    # check for non-empty segments on targ and ref images
    segs_to_fill = set(segments_targ).intersection(targ_seg_avg).intersection(ref_seg_avg)

    #Get pos of segstofill


    for seg in segs_to_fill:
        targ_avg = targ_seg_avg[seg]
        ref_avg = ref_seg_avg[seg]
        prop = targ_avg/ref_avg

        print(targ_avg)

    # print(131048 in segs_to_fill)
    # img_segs_to_fill = numpy.isin(img_seg1,segs_to_fill)
    # print(numpy.any(img_segs_to_fill))

    # set(n_targ).intersection
    # img_targ[n_targ] = 




    # pos_of_interest = numpy.isin(img_seg1, segments_targ)
    # img_seg1_of_interest = img_seg1[pos_of_interest]
    # img_targ_of_interest = img_targ[pos_of_interest]
    # img_ref_of_interest = img_ref[pos_of_interest]
    # ref_seg_mean = {}
    # targ_seg_mean = {}

    # nn = ~(numpy.isnan(img_targ_of_interest)|numpy.isnan(img_seg1_of_interest))
    # img_targ_of_interest_nn, img_seg1_of_interest_nn = img_targ_of_interest[nn],img_seg1_of_interest[nn]
    # unq,idx,cnt=numpy.unique(img_targ_of_interest_nn,return_inverse=True,return_counts=True)
    # r = dict(zip(unq,numpy.bincount(idx,img_seg1_of_interest_nn)/cnt))
    # # print(r)
    # print(cnt)



    # nan_t = numpy.isnan(img_targ_of_interest)
    # nnan_t = ~nan_t
    # nan_r = numpy.isnan(img_ref_of_interest)
    # nnan_r = ~nan_r

    # seg_nnan_t = img_seg1[nnan_t]
    # seg_nnan_r = img_seg1[nnan_r]
    # img_targ[nan_t] = (numpy.bincount(seg_not_nan,img_targ[not_nan],seg_num+1)/numpy.bincount(seg_not_nan,None,seg_num+1))[img_seg1[nan]]
    # print(segments_of_interest)


    # nan = numpy.isnan(img_targ_of_interest)
    # not_nan = ~nan
    # seg_not_nan = img_seg1[not_nan]
    # img_targ[nan] = (numpy.bincount(seg_not_nan,img_targ[not_nan],seg_num+1)/numpy.bincount(seg_not_nan,None,seg_num+1))[img_seg1[nan]]
    # print(segments_of_interest)


    ### Filter segs img ref
    # last_seg = numpy.nanmax(segments_targ)
    # for seg in segments_targ:
    #     print('Seg:{} of {}'.format(seg, last_seg))
    #     ### Get seg pixel position
    #     seg_pixels = numpy.nonzero(img_seg1 == seg)
    #     seg_indices = numpy.array(list(zip(seg_pixels[:][0], seg_pixels[:][1])))
    #     ### Get targ pix values
    #     targ_values_seg = img_targ[seg_indices[:,0], seg_indices[:,1]]
    #     ### Check if any is not nan
    #     if( numpy.any( ~numpy.isnan(targ_values_seg) ) ):
    #         ### Get nan position and replace by mean value
    #         print('fill L1')
    #         nan_pos = numpy.isnan(targ_values_seg)
    #         ref_values_seg = img_ref[seg_indices[:,0], seg_indices[:,1]]
    #         mean_ref = numpy.nanmean(ref_values_seg)
    #         pixel_weight = ref_values_seg/mean_ref
    #         img_targ[ seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos]] = numpy.nanmean(targ_values_seg) * pixel_weight[nan_pos]
    #     ### Otherwise uses segmentation level above
    #     else:
    #         seg_num = img_seg2[seg_indices[0,0], seg_indices[0,1]]
    #         ### Get seg pixel position
    #         seg_pixels = numpy.nonzero(img_seg2 == seg_num )
    #         seg_indices = numpy.array(list( zip(seg_pixels[:][0], seg_pixels[:][1])))
    #         ### Get targ pix values
    #         targ_values_seg = img_targ[seg_indices[:,0], seg_indices[:,1]]
    #         ### Check if any is not nan
    #         if( numpy.any( ~numpy.isnan(targ_values_seg))):
    #             ### Get nan position and replace by mean value
    #             print('fill L2')
    #             nan_pos = numpy.isnan(targ_values_seg)
    #             ref_values_seg = img_ref[ seg_indices[:,0], seg_indices[:,1]]
    #             mean_ref = numpy.nanmean(ref_values_seg)
    #             pixel_weight = ref_values_seg/mean_ref
    #             img_targ[ seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos]] = numpy.nanmean(targ_values_seg) * pixel_weight[nan_pos]
    #         ### Otherwise uses segmentation level above
    #         else:
    #             seg_num = img_seg3[seg_indices[0,0], seg_indices[0,1]]
    #             ### Get seg pixel position
    #             seg_pixels = numpy.nonzero(img_seg3 == seg_num)
    #             seg_indices = numpy.array(list( zip(seg_pixels[:][0], seg_pixels[:][1])))
    #             ### Get targ pix values
    #             targ_values_seg = img_targ[seg_indices[:,0], seg_indices[:,1]]
    #             ### Check if any is not nan
    #             if( numpy.any(~numpy.isnan(targ_values_seg))):
    #                 ### Get nan position and replace by mean value
    #                 print('fill L3')
    #                 nan_pos = numpy.isnan( targ_values_seg)
    #                 ref_values_seg = img_ref[ seg_indices[:,0], seg_indices[:,1]]
    #                 mean_ref = numpy.nanmean(ref_values_seg)
    #                 pixel_weight = ref_values_seg/mean_ref
    #                 img_targ[seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos]] = numpy.nanmean(targ_values_seg) * pixel_weight[nan_pos]
    #             else:
    #                 print('No fill')
    # return img_targ


# def test_marujo_2019():
#     img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3, out_dir, kwargs, input_targ_filename = filling_preparation_multseg(input_targ_filename, input_ref_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename, out_dir)
#     img_filled = fill_marujo_2019(img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3)
#     # filename = out_dir + os.path.basename(input_targ_filename)
#     # with rasterio.open(str(filename), 'w', **kwargs) as dst:
#     #     dst.write_band(1, img_filled)
#     return


def fill_maxwell_2007(img_targ, gaps_targ, img_seg1, img_seg2, img_seg3):
    print('Fill Maxwell 2007')
    # print('gaps_targ.shape:{}'.format(gaps_targ.shape))

    ### Get which segments contains NA on target image
    print('Searching for segments containing gaps...')
    indices_gap_targ = numpy.array( list( zip(gaps_targ[:,0], gaps_targ[:,1])))
    segments_targ = img_seg1[ indices_gap_targ[:,0], indices_gap_targ[:,1]]
    segments_targ = numpy.unique(segments_targ[~numpy.isnan(segments_targ)])
    print('len segs:{}'.format(len(segments_targ)))
    print('segs containing na:{}'.format(segments_targ[0]))

    ### Filter segs img ref
    last_seg = numpy.nanmax(segments_targ)
    for seg in segments_targ:
        print('Seg:{} of {}'.format(seg, last_seg))
        ### Get seg pixel position
        seg_pixels = numpy.nonzero(img_seg1 == seg)
        seg_indices = numpy.array(list(zip(seg_pixels[:][0], seg_pixels[:][1])))
        ### Get targ pix values
        targ_values_seg = img_targ[seg_indices[:,0], seg_indices[:,1]]
        ### Check if any is not nan
        if(numpy.any(~numpy.isnan(targ_values_seg))):
            ### Get nan position and replace by mean value
            print('fill L1')
            nan_pos = numpy.isnan(targ_values_seg)
            img_targ[ seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos] ] = numpy.nanmean(targ_values_seg)
        ### Otherwise uses segmentation level above
        else:
            seg_num = img_seg2[seg_indices[0,0], seg_indices[0,1]]
            ### Get seg pixel position
            seg_pixels = numpy.nonzero(img_seg2 == seg_num)
            seg_indices = numpy.array(list(zip(seg_pixels[:][0], seg_pixels[:][1])))
            ### Get targ pix values
            targ_values_seg = img_targ[seg_indices[:,0], seg_indices[:,1]]
            ### Check if any is not nan
            if( numpy.any(~numpy.isnan(targ_values_seg))):
                ### Get nan position and replace by mean value
                print('fill L2')
                nan_pos = numpy.isnan(targ_values_seg)
                img_targ[seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos]] = numpy.nanmean(targ_values_seg)
            ### Otherwise uses segmentation level above
            else:
                seg_num = img_seg3[seg_indices[0,0], seg_indices[0,1]]
                ### Get seg pixel position
                seg_pixels = numpy.nonzero(img_seg3 == seg_num)
                seg_indices = numpy.array(list(zip(seg_pixels[:][0], seg_pixels[:][1])))
                ### Get targ pix values
                targ_values_seg = img_targ[seg_indices[:,0], seg_indices[:,1]]
                ### Check if any is not nan
                if( numpy.any(~numpy.isnan(targ_values_seg))):
                    ### Get nan position and replace by mean value
                    print('fill L3')
                    nan_pos = numpy.isnan(targ_values_seg)
                    img_targ[seg_indices[:,0][nan_pos], seg_indices[:,1][nan_pos]] = numpy.nanmean(targ_values_seg)
                else:
                    print('No fill')
    return img_targ


def test_maxwell_2007():
    img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3, out_dir, kwargs, input_targ_filename = filling_preparation_multseg(input_targ_filename, input_ref_filename, input_seg1_filename, input_seg2_filename, input_seg3_filename, out_dir)
    img_filled = fill_marujo_2019(img_targ, gaps_targ, img_ref, img_seg1, img_seg2, img_seg3)
    # filename = out_dir + os.path.basename(input_targ_filename)
    # with rasterio.open(str(filename), 'w', **kwargs) as dst:
    #     dst.write_band(1, img_filled)
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


def test_maxwell_2004():
    img_targ, gaps_targ, img_seg1, kwargs = filling_preparation_singseg(input_targ_filename, input_seg1_filename)
    img_filled = fill_maxwell_2004(img_targ, img_seg1, gaps_targ)
    filename = out_dir + os.path.basename(input_targ_filename)
    with rasterio.open(str(filename), 'w', **kwargs) as dst:
        dst.write_band(1, img_filled)
    return


def main():
    test_maxwell_2004()
    # test_maxwell_2007()
    # test_marujo_2019()

if (__name__ == '__main__'):
    print('START [:')
    start = time.time()
    set_values()
    main()
    end = time.time()
    print('Duration time: {}'.format(end - start))
    print('END :]')
