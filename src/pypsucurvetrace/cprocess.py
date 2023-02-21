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
import logging

from pypsucurvetrace.read_datafile import read_datafile
from pypsucurvetrace.curvetrace_tools import say_hello



import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt



# set up logger:
logger = logging.getLogger('curveprocess')
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


if __name__ == "__main__":
    cprocess()


def cprocess():
    ################
    # main program #
    ################

    # input arguments:
    parser = argparse.ArgumentParser(description='curveprocess is a Python program to determine DUT parameters from from pypsucurvetrace data files.')
    parser.add_argument('datafiles', nargs='+', help='Names (and paths) of pypsucurvetrace data files, can use wildcards.')

    # U1 value for parameter calculation:
    parser.add_argument('--U1', type=float, help='U1 value for parameter calculation.')

    # I1 value for parameter calculation:
    parser.add_argument('--I1', type=float, help='I1 value for parameter calculation.')

    # use preheat values as target point for the parameter extraction:
    parser.add_argument('--preheat', action='store_true', help='Determine the parameters at the preheat values of U1 and I1; use the measured U2 preheat value instead of interpolating U2 from the curve data.')

    # BJT option:
    parser.add_argument('--bjtvbe', help='BJT VBE-on voltage for conversion of PSU U2 voltage to base current using R2CONTROL from the data file: Ibase = (U2-BJTVBE)/R2CONTROL')




    logger.warning('cprocess / curveprocess is under construction!')





    # Say Hello:
    say_hello('curveprocess', 'Extract and calculate parameters from pypsucurvetrace data')

    args = parser.parse_args()

    # determine data file(s):
    datafiles = args.datafiles

    # U1, I1:
    U1 = None
    I1 = None
    if args.preheat:
        use_preheat = True
    else:
        use_preheat = False
        try:
    	    U1 = args.U1
        except:
    	    logger.error('U1 value missing or invalid')
        try:
    	    I1 = args.I1
        except:
    	    logger.error('I1 value missing or invalid')
   	
    # BJT Vbe-on value:
    BJT_VBE = None # default
    if args.bjtvbe:
	    BJT_VBE = float(args.bjtvbe)




    # prepare output:
    sep = ', '
    if BJT_VBE is None:
        # voltage controlled DUT
        print( 'Filename' + sep + 'Label' + sep + 'U1' + sep + 'I1' + sep + 'U2' + sep + 'dI1_dU2' + sep + 'dU1_dU2' + sep + 'dI1_dU1' + sep + 'T')
    else:
        # current controlled DUT
        print( 'Filename' + sep + 'Label' + sep + 'U1' + sep + 'I1' + sep + 'I2' + sep + 'dI1_dI2' + sep + 'dU1_dI2' + sep + 'dI1_dU1' + sep + 'T')
    
    # process all datafiles:
    for i in range(len(datafiles)):
    
        # init
	    X2 = None # U2 or I2 (depending if DUT is voltage controlled or current controlled)
	    T  = None
        
        # read data file:
	    d, l, p, R2_val = read_datafile(datafiles[i])
	    
	    if use_preheat:
	        try:
	            U1 = float(p.U0)
	            I1 = float(p.I0)
	            X2 = float(p.Uc)
	            T  = float(p.T)
	        except:
	            logger.error('Could not determine U1, I1 and U2 from preheat data')
	    
	    else:
	        logger.info('...use I1 and U1 from args, determine U2 or I2 and T from data...')
	        X2 = None
	        T  = None



	    dI1_dX2, dU1_dX2, dI1_dU1 = proc_curves(d, U1, I1, R2_val, BJT_VBE)
	    
	    
	    
	    # print pre-heat data:
	    print( Path(d.datafile).stem + sep + l + sep + str(U1) + sep + str(I1) + sep + str(X2) + sep + str(dI1_dX2) + sep + str(dU1_dX2) + sep + str(dI1_dU1) + sep + str(T))
	    
	    
	    
def proc_curves(cdata, U1, I1, R2_val=None, BJT_VBE=None):
    # determine derivatives of curve data at the (U1/I1) points. Convert to BJT/current-controlled data first, if R2_val and BJT_VBE are not None.
    #
    # INPUT:
    # cdata: curve-data object (output from read_datafile)
    # U1: array of U1 values where outputs should be calculated
    # I1: array of I1 values where outputs should be calculated
    #
    # OUTPUT:
    # dI1_dX2: dI1/dU2 or dI1/dI2 derivative(s) at point(s) (U1/I1)
    # dU1_dX2: dU1/dU2 or dU1/dI2 derivative(s) at point(s) (U1/I1)
    # dI1_dU1: dI1/dU1 derivative(s) at point(s) (U1/I1)
    
    if R2_val is not None:
        if BJT_VBE is not None:
            logger.info('...need to convert U2 to I2 using BJT formula...')

    dI1_dX2 = None
    dU1_dX2 = None
    dI1_dU1 = None


    logger.warning('toying around with grid data and interpolation, CALCULATION OR DERIVATIVES NOT YET IMPLEMENTED...')

    # get U1, U2, I1 data:
    U1 = cdata.get_U1_meas(exclude_CC = True)
    U2 = cdata.get_U2_set(exclude_CC = True)
    I1 = cdata.get_I1_meas(exclude_CC = True)

    # plot raw data:
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(U1, U2, I1, color='white', edgecolors='grey', alpha=0.5)
    ax.scatter(U1, U2, I1, c='red')
    plt.show()

    # interpolate:
    u1 = np.linspace(U1.min(), U1.max(), 1000)
    u2 = np.linspace(U2.min(), U2.max(), 1000)
    UU1, UU2 = np.meshgrid(u1,u2)
    II1 = griddata((U1, U2), I1, (UU1, UU2), method='cubic')

    # plot interpolated data (contours):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.contour(UU1, UU2, II1)
    plt.ioff()
    plt.show()
    
    return dI1_dX2, dU1_dX2, dI1_dU1

