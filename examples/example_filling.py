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


def main():
    nan = numpy.nan
    img_target = numpy.array([[10, 10, 20, 20],
                            [10, nan, nan, 20],
                            [30, nan, nan, 20],
                            [30, 30, 30, 30]])
    img_reference = numpy.array([[5, 5, 10, 10],
                           [5, 15, 10, 10],
                           [15, 15, 3, 10],
                           [15, 15, 15, 15]])
    img_segmentation = numpy.array([[1, 1, 2, 2],
                           [1, 3, 2, 2],
                           [3, 3, 2, 2],
                           [3, 3, 3, 3]])

    # Search for no data
    gaps_target = eo_filling.get_gaps(img_target)
    if numpy.any(gaps_target):
        logging.info('Filling')
        img_filled = eo_filling.fill_maxwell_2004(img_target, img_segmentation, gaps_target)
        logging.info(img_filled)
        img_filled = eo_filling.fill_marujo(img_target, img_reference, img_segmentation, gaps_target)
        logging.info(img_filled)
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
