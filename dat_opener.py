# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 11:26:56 2024

@author: Lab
"""
import numpy as np
import struct


def read_dat(filename):
    """
    Function opens .dat file.
    """

    # binary data file reading
    with open(filename, "rb") as binary_file:
        data_bin = binary_file.read()

    zero = struct.unpack('>H', data_bin[0:2])[0]
    height = struct.unpack('>H', data_bin[2:4])[0]
    zero = struct.unpack('>H', data_bin[4:6])[0]
    width = struct.unpack('>H', data_bin[6:8])[0]

    try:
        s = '>H' + 'H' * (height * width - 1)
        data = np.fromiter(struct.unpack(s, data_bin[8:]), dtype='uint16')
    except struct.error:
        try:
            s = '>B' + 'B' * (height * width - 1)
            data = np.fromiter(struct.unpack(s, data_bin[8:]), dtype='uint8')
        # data = data*8
        # print("Warning: 8bit image. Read with adjustment to 12bit format (magnified by 8).")
        except:
            print("ERROR: could not read data file {}".format(filename))
            return None

    data = np.reshape(data, (height, width))
    if width < height:
        return data.T, height, width  # Transpose array and swap height and width.
    else:
        return data, width, height
