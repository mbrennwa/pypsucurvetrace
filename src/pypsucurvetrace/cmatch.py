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
from pathlib import Path
import numpy as np
from scipy.interpolate import griddata

from pypsucurvetrace.read_datafile import read_datafile
from pypsucurvetrace.curvetrace_tools import say_hello, get_logger, convert_to_bjt, error_and_exit, argpair


# set up logger:
logger = get_logger('curvematch')

if __name__ == "__main__":
    cmatch()
    

def cmatch():
    ################
    # main program #
    ################

    # input arguments:
    parser = argparse.ArgumentParser(description='curvematch is a Python program to determine the RMS difference between two pypsucurvetrace curve sets.')
    parser.add_argument('datafiles', nargs='+', help='Names (and paths) of pypsucurvetrace data files, can use wildcards.')

    # U1 range:
    parser.add_argument('--U1range', nargs=1, type=argpair, help='U1 range to consider (value pair with min. and max value, e.g. --U1range [5,20]')

    # I1 range:
    parser.add_argument('--I1range', nargs=1, type=argpair, help='I1 range to consider (value pair with min. and max value, e.g. --I1range [5,20]')

    # BJT option:
    parser.add_argument('--bjtvbe', help='BJT VBE-on voltage for conversion of PSU U2 voltage to base current using R2CONTROL from the data file: Ibase = (U2-BJTVBE)/R2CONTROL')


    # Say Hello:
    say_hello('curveprocess', 'Extract and calculate parameters from pypsucurvetrace data')

    logger.warning('...not yet implemented... just messing around with ideas!')

    args = parser.parse_args()

    # determine unique list of data file(s):
    datafiles = (list(set(args.datafiles)))
    N = len(datafiles)
    if N < 2:
        error_and_exit(logger, 'Need two or more different input datafiles')

    # U1range, I1range:
    U1range = args.U1range
    I1range = args.I1range

    # BJT Vbe-on value:
    BJT_VBE = None # default
    if args.bjtvbe:
	    BJT_VBE = float(args.bjtvbe)


    # prepare output, header:
    sep = ', '
    
    label_U1_low  = 'U1_range_low (V)'
    label_U1_high = 'U1_range_high (V)'
    label_I1_low  = 'I1_range_low (A)'
    label_I1_high = 'I1_range_high (A)'
    if BJT_VBE is not None:
        # current controlled DUT
        label_X2_delta_RMS = 'delta-Ib-RMS (A)'
    else:
        # voltage controlled DUT
        label_X2_delta_RMS = 'delta-Vg-RMS (V)'
        
    
        
    print( 'Filename-1' + sep + 'Sample-1' + sep + 'Filename-2' + sep + 'Sample-2' + sep + 
            label_U1_low + sep + label_U1_high + sep + label_I1_low + sep + label_I1_high + sep + 
            label_X2_delta_RMS )

    try:
        U1range  = [ min(U1range), max(U1range)]
        if U1range[0] == U1range[1]:
            logger.warning('Width of U1 range is zero, ignoring U1 range.')
            U1range = None
    except:
        U1range = None
        
    try:
        I1range  = [ min(I1range), max(I1range)]
        if I1range[0] == I1range[1]:
            logger.warning('Width of I1 range is zero, ignoring I1 range.')
            I1range = None
    except:
        I1range = None
        
    for i in range(N-1):
        for j in range(i+1,N):
        
            # read data files:
            d1, l1, p1, R2_val1 = read_datafile(datafiles[i])
            d2, l2, p2, R2_val2 = read_datafile(datafiles[j])
            
            # determine RMS delta:
            delta_X2_RMS = curves_RMSdelta(d1, d2, U1range, I1range, R2_val1, R2_val2, BJT_VBE, BJT_VBE)
            
	        # print results:
            Nd = 4
            try: U1_low = "{:.{}g}".format( U1range[0], Nd )
            except: U1_low = '--'
            try: U1_high = "{:.{}g}".format( U1range[1], Nd )
            except: U1_high = '--'
            try: I1_low = "{:.{}g}".format( I1range[0], Nd )
            except: I1_low = '--'
            try: I1_high = "{:.{}g}".format( I1range[1], Nd )
            except: I1_high = '--'
            try: delta_X2_RMS = "{:.{}g}".format( delta_X2_RMS, Nd )
            except: delta_X2_RMS = 'N/A'
                
            
            print( Path(d1.datafile).stem + sep + l1 + sep +
	               Path(d2.datafile).stem + sep + l2 + sep +
	               U1_low + sep +
	               U1_high + sep +
	               I1_low + sep +
	               I1_high + sep +
	               delta_X2_RMS
	              )


def curves_RMSdelta(cdata1, cdata2, U1range, I1range, R2_val1=None, R2_val2=None, BJT_VBE1=None, BJT_VBE2=None):
    # determine RMS difference between curve sets.
    #
    # INPUT:
    # cdata1, cdata2: curve-data objects (outputs from read_datafile)
    # U1range, I1range: U1 and I1 range that should be considered to calculate the RMS difference
    #
    # OUTPUT:
    # deltaX2: U2 or I2 RMS difference between the two curve sets
    
    # get curve data:
    cU1_1 = cdata1.get_U1_meas(exclude_CC = True)
    cX2_1 = cdata1.get_U2_set(exclude_CC = True)
    cI1_1 = cdata1.get_I1_meas(exclude_CC = True)
    cU1_2 = cdata2.get_U1_meas(exclude_CC = True)
    cX2_2 = cdata2.get_U2_set(exclude_CC = True)
    cI1_2 = cdata2.get_I1_meas(exclude_CC = True)
    
    if R2_val1 is not None:
        if BJT_VBE1 is not None:
            cX2_1 = convert_to_bjt(cX2_1, BJT_VBE1, R2_val1)
    if R2_val2 is not None:
        if BJT_VBE2 is not None:
            cX2_2 = convert_to_bjt(cX2_2, BJT_VBE2, R2_val2)
    
    
    logger.warning('...calculate X2 RMS difference here...')
    
    deltaX2_RMS = 1.23456
    
    return deltaX2_RMS
