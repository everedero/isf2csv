# Tektronix ISF format converter

## Description
Tektronix oscilloscope output a binary .isf file.
The following scripts helps converting a file to .csv.

## ISF file description
This is provided by Tektronix in their FAQ [here](https://www.tek.com/en/support/faqs/what-format-isf-file)

The ISF format is the same as what the scope would send in response to the WAVFrm? command via an external program.

The response to the WAVFrm? command is documented in the programmers manual for your instrument, which you can download from the Tektronix website at www.tek.com/manuals.

The file looks like this:

```
:WFMPRE:BYT_NR 2;BIT_NR 16;ENCDG BIN;BN_FMT RI;BYT_OR MSB;NR_PT 10000;WFID "Ch1, DC coupling, 2.0E0 V/div, 1.0E-5 s/div, 10000 points, Sample mode";PT_FMT Y;XINCR 1.0E-8;PT_OFF 0;XZERO 3.5E-4;XUNIT "s";YMULT 3.125E-4;YZERO 0.0E0;YOFF 0.0E0;YUNIT "V";:CURVE #520000
```

The values from the ":" at the beginning of the file to the ";" just before the ":curve" are the preamble.
The binary block begins with ":CURVE #". The next value is referred to in the manual as X.
This is the ASCII representation of the number of bytes that follow that represent the record length.
The next bytes, referred to in the manual as the YYY bytes are the ASCII representation of the record length field.
In this example the 5 tells us that the next 5 bytes represent the record length.
The next 5 bytes are 20000, which tells us that the number of bytes returned in the curve will be 20,000.
Since we can see in the preamble that the number of bytes for each acquired sample point is 2 (BYT\_NR 2) we know that the number of sample acquired was 20,000 / 2 or 10,000 samples.

## Script usage
python3 isf2csv file.isf

## Preamble example
```
:WFMPRE:NR_PT 10000;:WFMPRE:BYT_NR 2;BIT_NR 16;ENCDG BINARY;BN_FMT RI;BYT_OR MSB;WFID "Ch2, DC coupling, 5.000V/div, 400.0ns/div, 10000 points, Sample mode";NR_PT 10000;PT_FMT Y;XUNIT "s";XINCR 400.0000E-12;XZERO -1.6012E-6;PT_OFF 0;YUNIT "V";YMULT 781.2500E-6;YOFF -12.6720E+3;YZERO 0.0E+0;VSCALE 5.0000;HSCALE 100.0000E-9;VPOS -1.9800;VOFFSET 0.0E+0;HDELAY 398.8000E-9;DOMAIN TIME;WFMTYPE ANALOG;CENTERFREQUENCY 0.0E+0;SPAN 0.0E+0;REFLEVEL 0.0E+0;:CURVE #520000
```
