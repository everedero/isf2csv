#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to convert Tektronix ISF files to CSV.

@author: Eve Redero
@license: GPL
"""

import os
import numpy as np
import sys
import re
from io import StringIO
import csv
import struct

if __name__ == "__main__":
    if len(sys.argv) > 1:
        isf_filename = sys.argv[1]
    else:
        raise IOError("Please input a file name")

    with open(isf_filename, 'rb') as myfile:
        text = myfile.read()

    # :CURVE separates preamble from binary values
    exp_split = re.compile(b":CURVE #")
    splitted = exp_split.split(text)
    # Save preamble and convert it to ASCII text
    preamble = splitted[0].decode('ascii')

    # Save what's after preamble
    data = splitted[1]
    # First byte is length of length information
    len_len = int(chr(data[0]))
    # Next len_len bytes are length of dataset
    data_len = int(data[1:len_len+1].decode('ascii'))

    # Removing data length bytes from data
    data = data[len_len+1::]

    if len(data) != data_len:
        raise IOError("Invalid data length")

    preamble = preamble.replace(";", "\n")
    #Parsing preamble
    fakefile = StringIO(preamble)
    reader = csv.reader(fakefile, delimiter=' ')
    preamble_vals=dict()
    for row in reader:
        preamble_vals[row[0]]=row[1]

    sample_byte_size = int(preamble_vals[':WFMPRE:BYT_NR'])
    sample_number = int(preamble_vals[':WFMPRE:NR_PT'])

    if sample_byte_size * sample_number != data_len:
          raise IOError("Invalid data length or sample size or sample number")

    struct_fmt = ''
    if sample_byte_size == 2: # signed short
        struct_fmt = 'h'
    elif sample_byte_size == 4: # signed int
            struct_fmt = 'i'
    elif sample_byte_size == 8: # signed long long
            struct_fmt = 'q'
    else:
        raise IOError("Unknown sample size number " +
                      "{}".format(sample_byte_size))

    if preamble_vals['BYT_OR'] == 'MSB': # MSB would mean Big Endian
        struct_fmt = '>' + struct_fmt
    elif preamble_vals['BYT_OR'] == 'LSB': # LSB Little Endian
        struct_fmt = '<' + struct_fmt
    else:
        raise IOError("Unknown byte ordering " +
                      "{}".format(preamble_vals['BYT_OR']))

    data_unpacked = [i[0] for i in struct.iter_unpack(struct_fmt, data)]

    data_matrix = np.array(data_unpacked)
    # Y scaling
    data_matrix = (data_matrix - float(preamble_vals['YOFF'])) \
        * float(preamble_vals['YMULT'])
    # X scaling
    x_matrix = np.arange(0, sample_number) * float(preamble_vals['XINCR'])

    # Create matrix with X and Y
    data_matrix = np.concatenate([x_matrix[:, np.newaxis],
                                  data_matrix[:, np.newaxis]], axis=1)

    basename = os.path.splitext(os.path.basename(isf_filename))[0]
    output_name = basename + '.csv'
    with open(output_name, 'w') as output_file:
        csv_out = csv.writer(output_file, delimiter=";")
        csv_out.writerow(["X axis ({})".format(preamble_vals['XUNIT']),
                      "Y axis ({})".format(preamble_vals['YUNIT'])])
        csv_out.writerows(data_matrix)

    # Exports a plot
    import matplotlib.pyplot as plt
    plt.plot(data_matrix[:, 0], data_matrix[:, 1])
    plt.xlabel(preamble_vals['XUNIT'])
    plt.ylabel(preamble_vals['YUNIT'])
    plt.grid()
    plt.savefig("{}.png".format(basename), dpi=200)
