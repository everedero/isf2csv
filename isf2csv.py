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

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        isf_filename = sys.argv[1]
    else:
        #raise IOError("Please input a file name")
        isf_filename = "/home/parallels/Documents/isf2csv/tek0008CH2.isf"

    with open(isf_filename, 'rb') as myfile:
        text = myfile.read()


#""":WFMPRE:NR_PT 10000;:WFMPRE:BYT_NR 2;BIT_NR 16;ENCDG BINARY;BN_FMT RI;BYT_OR MSB;WFID "Ch2, DC coupling, 5.000V/div, 400.0ns/div, 10000 points, Sample mode";NR_PT 10000;PT_FMT Y;XUNIT "s";XINCR 400.0000E-12;XZERO -1.6012E-6;PT_OFF 0;YUNIT "V";YMULT 781.2500E-6;YOFF -12.6720E+3;YZERO 0.0E+0;VSCALE 5.0000;HSCALE 100.0000E-9;VPOS -1.9800;VOFFSET 0.0E+0;HDELAY 398.8000E-9;DOMAIN TIME;WFMTYPE ANALOG;CENTERFREQUENCY 0.0E+0;SPAN 0.0E+0;REFLEVEL 0.0E+0;:CURVE #520000"""

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
    
    import matplotlib.pyplot as plt
    plt.plot(data_unpacked)
          
    
