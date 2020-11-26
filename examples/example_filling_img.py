#
# This file is part of eo-filling.py.
# Copyright (C) 2020 Rennan Marujo.
#
# eo-filling.py is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

# Python Native
import logging
import time
# 3rd party
import eo_filling
import numpy
import rasterio


def main():
    img_target_ds = rasterio.open('/home/marujo/Downloads/eo-example/mosaic/L7/LE0720150810/LE07_22KDF_20150810_sr_band4.tif')
    img_reference_ds = rasterio.open('/home/marujo/Downloads/eo-example/mosaic/L8/LC0820150802/LC08_22KDF_20150802_sr_band5.tif')
    img_segmentation_ds = rasterio.open('/home/marujo/Downloads/eo-example/segmentation/LC0820150802/LC08_22KDF_20150802_sr_evi_200.tif')

    img_target = img_target_ds.read(1)
    img_reference = img_reference_ds.read(1)
    img_segmentation = img_segmentation_ds.read(1)

    profile = img_target_ds.profile

    img_target[img_target < 0] = -9999
    img_reference[img_reference < 0] = -9999

    # Search for no data
    gaps_target = eo_filling.get_gaps(img_target, -9999)
    if numpy.any(gaps_target):
        logging.info('Filling')

        img_filled = eo_filling.fill_maxwell_2004(img_target, img_segmentation, gaps_target)
        with rasterio.open('example_maxwell2004.tif', 'w', **profile) as dst:
            dst.write(img_filled.astype(profile['dtype']), 1)

        img_filled = eo_filling.fill_marujo(img_target, img_reference, img_segmentation, gaps_target)
        with rasterio.open('example_fillmarujo.tif', 'w', **profile) as dst:
            dst.write(img_filled.astype(profile['dtype']), 1)
    else:
        logging.info('Nothing to fill')
        return


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Starting Test')
    start = time.time()
    main()
    end = time.time()
    logging.info('Duration time: {}'.format(end - start))
