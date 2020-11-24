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
                              [nan, nan, nan, 20],
                              [nan, nan, 30, 30]])

    img_reference = numpy.array([[5, 5, 10, 10],
                                 [5, 15, 10, 10],
                                 [15, 15, 3, 10],
                                 [15, 15, 15, 15]])

    segmentation_list = list()
    segmentation_list.append(numpy.array([[1, 1, 2, 2],
                                          [1, 2, 2, 2],
                                          [4, 4, 4, 2],
                                          [5, 5, 3, 3]]))

    segmentation_list.append(numpy.array([[1, 1, 2, 2],
                                          [1, 2, 2, 2],
                                          [3, 3, 3, 2],
                                          [4, 3, 3, 3]]))

    segmentation_list.append(numpy.array([[1, 1, 1, 1],
                                          [1, 1, 1, 1],
                                          [1, 1, 1, 1],
                                          [1, 1, 1, 1]]))
    # Search for no data
    logging.info('Filling')
    img_filled = eo_filling.fill_maxwell_2007(img_target, segmentation_list)
    logging.info(img_filled)
    img_filled = eo_filling.fill_marujo_multseg(img_target, img_reference, segmentation_list)
    logging.info(img_filled)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Starting Test')
    start = time.time()
    main()
    end = time.time()
    logging.info('Duration time: {}'.format(end - start))
