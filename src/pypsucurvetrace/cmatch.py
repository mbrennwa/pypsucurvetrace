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
from pypsucurvetrace.curvetrace_tools import say_hello, get_logger, convert_to_bjt, error_and_exit, valuepairs


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
    parser.add_argument('--U1range', type=valuepairs, help='U1 range to consider (value pair with min. and max value, e.g. --U1range [5,20]')

    # I1 range:
    parser.add_argument('--I1range', type=valuepairs, help='I1 range to consider (value pair with min. and max value, e.g. --I1range [5,20]')

    # BJT option:
    parser.add_argument('--bjtvbe', help='BJT VBE-on voltage for conversion of PSU U2 voltage to base current using R2CONTROL from the data file: Ibase = (U2-BJTVBE)/R2CONTROL')
    
    # do not show a "hello" message
    parser.add_argument('--nohello', action='store_true', help='Do not print the hello / about message (useful when the output needs further processing).')

    # parse args:
    args = parser.parse_args()

    # Say Hello:
    if not args.nohello:
        say_hello('curveprocess', 'Extract and calculate parameters from pypsucurvetrace data')

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
        label_X2_delta_RMS              = 'delta-Ib (A-RMS)'
        label_X2_delta_RMS_mean_removed = 'delta-Ib mean subtracted (A-RMS)'
    else:
        # voltage controlled DUT
        label_X2_delta_RMS              = 'delta-Vg (V-RMS)'
        label_X2_delta_RMS_mean_removed = 'delta-Vg mean subtracted (V-RMS)'
    
    print( 'Filename-1' + sep + 'Sample-1' + sep + 'Filename-2' + sep + 'Sample-2' + sep + 
            label_U1_low + sep + label_U1_high + sep + label_I1_low + sep + label_I1_high + sep + 
            label_X2_delta_RMS + sep + label_X2_delta_RMS_mean_removed )

    try:
        U1range  = [ min(min(U1range)), max(max(U1range)) ]
        if U1range[0] == U1range[1]:
            logger.warning('Width of U1 range is zero, ignoring U1 range.')
            U1range = None
    except:
        logger.warning('Could not parse U1 range, ignoring U1 range.')
        U1range = None
        
    try:
        I1range  = [ min(min(I1range)), max(max(I1range)) ]
        if I1range[0] == I1range[1]:
            logger.warning('Width of I1 range is zero, ignoring I1 range.')
            I1range = None
    except:
        logger.warning('Could not parse I1 range, ignoring I1 range.')
        I1range = None
    
    datafiles.sort()
    for i in range(N-1):
        for j in range(N):
            if j > i:
                # read data files:
                d1, l1, p1, R2_val1 = read_datafile(datafiles[i])
                d2, l2, p2, R2_val2 = read_datafile(datafiles[j])
                
                # determine RMS delta:
                dx2_0RMS, dx2_cRMS = curves_RMSdelta(d1, d2, U1range, I1range, R2_val1, R2_val2, BJT_VBE, BJT_VBE)
                
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
                try: dx2_0RMS = "{:.{}g}".format( dx2_0RMS, Nd )
                except: dx2_0RMS = 'N/A'
                try: dx2_cRMS = "{:.{}g}".format( dx2_cRMS, Nd )
                except: dx2_cRMS = 'N/A'
                    
                print( Path(d1.datafile).stem + sep + l1 + sep +
	                   Path(d2.datafile).stem + sep + l2 + sep +
	                   U1_low + sep +
	                   U1_high + sep +
	                   I1_low + sep +
	                   I1_high + sep +
	                   dx2_0RMS + sep +
	                   dx2_cRMS
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
    cI1_1 = cdata1.get_I1_meas(exclude_CC = True)
    cX2_1 = cdata1.get_U2_set(exclude_CC = True)
    cU1_2 = cdata2.get_U1_meas(exclude_CC = True)
    cI1_2 = cdata2.get_I1_meas(exclude_CC = True)
    cX2_2 = cdata2.get_U2_set(exclude_CC = True)

    # convert U2 to Ib, if necessary:
    if R2_val1 is not None:
        if BJT_VBE1 is not None:
            cX2_1 = convert_to_bjt(cX2_1, BJT_VBE1, R2_val1)
    if R2_val2 is not None:
        if BJT_VBE2 is not None:
            cX2_2 = convert_to_bjt(cX2_2, BJT_VBE2, R2_val2)

    # determine U1 and I1 range to consider:
    UU1 = np.unique(np.concatenate((cU1_1,cU1_2)))
    II1 = np.unique(np.concatenate((cI1_1,cI1_2)))
    if U1range is None:
        U1range = [ min(UU1) , max(UU1) ]
    if I1range is None:
        I1range = [ min(II1) , max(II1) ]
        
    # determine u1 and i1 interpolation grid coordinates:
    u1 = np.linspace( U1range[0], U1range[1], num=2*len(UU1), endpoint=True)
    i1 = np.linspace( I1range[0], I1range[1], num=2*len(II1), endpoint=True)

    # calculate x2 = f(u1,i1) surfaces (interpolation):
    x2_1 = X2_surface(cU1_1, cI1_1, cX2_1, u1, i1)
    x2_2 = X2_surface(cU1_2, cI1_2, cX2_2, u1, i1)
    
    dx2_0 = x2_2 - x2_1
    dx2_0 = dx2_0[~np.isnan(dx2_0)]
    
    dx2_c = dx2_0 - np.mean(dx2_0) # ignoring constant offset
    
    try:
        dx2_0RMS = np.sqrt( sum(dx2_0**2) / len(dx2_0) )
    except:
        dx2_0RMS = None
    try:
        dx2_cRMS = np.sqrt( sum(dx2_c**2) / len(dx2_c) )
    except:
        dx2_cRMS = None
    
    return dx2_0RMS, dx2_cRMS
    

def X2_surface(U1, I1, X2, u1, i1):
    # determine the 2D surface representing the function x2 = f(u1,i1) at the grid points defined by (u1,i1)
    uu1, ii1 = np.meshgrid(u1,i1)
    x2 = griddata((U1, I1), X2, (uu1, ii1), method='linear')
    return x2
