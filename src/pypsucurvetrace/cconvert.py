# This file is part of pypsucurvetrace, a toolbox for I/V curve tracing of electronic parts using programmable power supplies.
#
# pypsucurvetrace is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pypsucurvetrace is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pypsucurvetrace.  If not, see <http://www.gnu.org/licenses/>.

import argparse
# from pathlib import Path
# import numpy as np
# from scipy.interpolate import griddata
import pandas as pd
# import sys


# from pypsucurvetrace.read_datafile import read_datafile
from pypsucurvetrace.curvetrace_tools import say_hello, get_logger, error_and_exit


# set up logger:
logger = get_logger('cconvert')

if __name__ == "__main__":
    cconvert()


def cconvert():
    ################
    # main program #
    ################

    # input arguments:
    parser = argparse.ArgumentParser(description='cconvert is a Python program to convert data files from various curve tracers to pypsucurvetrace format.')
    parser.add_argument('datafiles', nargs='+', help='Names (and paths) of data files, can use wildcards.')

    # use etracer format:
    parser.add_argument('--etracer', action='store_true', help='Input file format: ETracer')

    # parse args:
    args = parser.parse_args()

    # parse input-file format
    if args.etracer:
        input_format = 'etracer'
    else:
        error_and_exit(logger, 'No input format specified, cannot continue.')

    # determine data file(s):
    datafiles = args.datafiles
    
    # process all datafiles:
    for d in datafiles:

        if input_format == 'etracer':
            DAT = __convert_from_etracer(d)

        else:
            error_and_exit(logger, 'Unknown format (' + input_format + ')')

    # Output in pypsu format to STDOUT:
    print('% DATA CONVERTED FROM ' + input_format.upper() + ' FILE ' + d)
    for k in range(len(DAT)):
        l = ''
        l = str(DAT[k][0])
        for kk in range(10):
            l = l + ' ' + str(DAT[k][kk+1])
        print( l ) # output to STDOUT


def __convert_from_etracer(datafile):
    # Check etracer file format version:
    with open(datafile, 'r') as file:
        try:
            version = file.readline().strip().split(' ')[1].split(':')
            if version[0].upper() == 'ETRACER_CSV_FORMAT_VERSION':
                if version[1] != '2.0':
                    logger.warning('Unknown etracer csv format version ' + version[1] + '. Be careful...')
            else:
                raise ValueError('CSV file does not appear to contain etracer data.')
        except Exception as e:
            error_and_exit(logger, 'Could not parse etracer file header (' + str(e) + ')')

    # Read data:
    X = pd.read_csv(datafile, comment='#', header=None)
    idx = X[0].unique() # index to curvesets
    DAT = []
    for i in idx:
        # parse and add curve data to C
        x = X[X[0]==i].dropna(axis=1, how='all').dropna(axis=1, how='all') # curve data at current index, without the NaN part
        u2 = x.iloc[4].median()
        for k in range(1,x.shape[1]): # skip the first entry (which is the etracer curve-set index)
            DAT.append([x.iloc[0][k], x.iloc[1][k]/1000.0, x.iloc[0][k], x.iloc[1][k]/1000.0, 0, u2, 0, u2, 0, 0, 0])

    return DAT