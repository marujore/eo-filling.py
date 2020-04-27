# Python Native

# 3rd-party
import numpy

#EO_filling

def get_gaps(img):
    gaps = numpy.argwhere( numpy.isnan( img ) )
    return( gaps )