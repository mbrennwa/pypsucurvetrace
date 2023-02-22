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

from pypsucurvetrace.read_datafile import read_datafile
from pypsucurvetrace.curvetrace_tools import say_hello, get_logger, convert_to_bjt, error_and_exit



import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt




# set up logger:
logger = get_logger('curveprocess')

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
    logger.warning('cprocess / curveprocess is under construction!')
    logger.warning('cprocess / curveprocess is under construction!')
    logger.warning('cprocess / curveprocess is under construction!')
    logger.warning('cprocess / curveprocess is under construction!')
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
        U1 = args.U1
        if U1 is None:
            error_and_exit(logger, 'U1 value missing or invalid')
        I1 = args.I1
        if I1 is None:
   	    	error_and_exit(logger, 'I1 value missing or invalid')

   	
   	
    # BJT Vbe-on value:
    BJT_VBE = None # default
    if args.bjtvbe:
	    BJT_VBE = float(args.bjtvbe)




    # prepare output, header:
    sep = ', '
    label_U1 = 'U0 (V)' # operating point voltage
    label_I1 = 'I0 (A)' # operating point current
    label_X2 = 'Ug (V)' # gate / grid current
    label_dI1_dX2 = 'gm (A/V)' # gain
    label_dI1_dU1 = 'go (A/V)' # output impedance
    if BJT_VBE is not None:
        # voltage controlled DUT
        label_X2 = 'Ib (A)' # base current
        label_dI1_dX2 = 'hfe (A/A)' # gain
    print( 'Filename' + sep + 'Sample' + sep + label_U1 + sep + label_I1 + sep + label_X2 + sep + label_dI1_dX2 + sep + label_dI1_dU1 + sep + 'T (°C)')
    
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
	            if BJT_VBE is not None:
	                X2 = convert_to_bjt(X2, BJT_VBE, R2_val)
	                
	        except Exception as e:
	            error_and_exit(logger, 'Could not determine U1, I1 and U2 from preheat data', e)
	    
	    else:
	        logger.info('...determine T from data...')
	        T  = None



	    XX2, dI1_dX2, dI1_dU1 = proc_curves(d, U1, I1, R2_val, BJT_VBE)
	    if X2 is None:
	        X2 = XX2
	        
	    
	    
	    
	    
	    # print parameters:
	    print( Path(d.datafile).stem + sep + l + sep + str(U1) + sep + str(I1) + sep + str(X2) + sep + str(dI1_dX2) + sep + str(dI1_dU1) + sep + str(T))
	    
	    
	    
def proc_curves(cdata, U1, I1, R2_val=None, BJT_VBE=None):
    # determine derivatives of curve data at the (U1/I1) points. Convert to BJT/current-controlled data first, if R2_val and BJT_VBE are not None.
    #
    # INPUT:
    # cdata: curve-data object (output from read_datafile)
    # U1: array of U1 values where outputs should be calculated
    # I1: array of I1 values where outputs should be calculated
    #
    # OUTPUT:
    # X2: U2 or I2 corresponding to specified (U1/I1) point(s)
    # dI1_dX2: dI1/dU2 or dI1/dI2 derivative(s) at point(s) (U1/I1), aka. gm (transconductance) of hfe (current gain)
    # dI1_dU1: dI1/dU1 derivative(s) at point(s) (U1/I1), aka. go (output impedance)
    
    # make sure U1 and I1 are lists, not scalars:
    try:
        u = len(U1)
    except:
        U1 = [U1,]
    try:
        u = len(I1)
    except:
        I1 = [I1,]
    
    # number of (U1/I1) points where the DUT parameters need to be calculated
    N = len(U1)
    if len(I1) != N:
        error_and_exit(logger, 'U1 and I1 must be same length')
    

    logger.warning('toying around with grid data and interpolation, CALCULATION OR DERIVATIVES NOT YET IMPLEMENTED...')

    # get curve data:
    cU1 = cdata.get_U1_meas(exclude_CC = True)
    cX2 = cdata.get_U2_set(exclude_CC = True)
    cI1 = cdata.get_I1_meas(exclude_CC = True)
     
    if R2_val is not None:
        if BJT_VBE is not None:
            cX2 = convert_to_bjt(cX2, BJT_VBE, R2_val)
            
            
   

    # plot raw data:
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(cU1, cX2, cI1, color='white', edgecolors='grey', alpha=0.5)
    ax.scatter(cU1, cX2, cI1, c='red')
    plt.show()
    
    # grid points for interpolation:
    NG = 10
    N_u1 = (len(np.unique(cU1))-1)*NG + 1;
    N_x2 = (len(np.unique(cX2))-1)*NG + 1;
    N_i1 = (len(np.unique(cI1))-1)*NG + 1;
    
    # data grids:
    u1 = np.linspace(cU1.min(), cU1.max(), N_u1)  # interpolation coordinates for U1
    x2 = np.linspace(cX2.min(), cX2.max(), N_x2)  # interpolation coordinates for X2
    i1 = np.linspace(cI1.min(), cI1.max(), N_i1)  # interpolation coordinates for I1
    
    delta_u1 = (u1[-1]-u1[0])/N_u1
    if delta_u1 == 0:
        error_and_exit(logger, 'U1 range must be greater than zero!')
    delta_x2 = (x2[-1]-x2[0])/N_x2
    if delta_x2 == 0:
        error_and_exit(logger, 'U2 range must be greater than zero!')
    delta_i1 = (i1[-1]-i1[0])/N_i1
    if delta_i1 == 0:
        error_and_exit(logger, 'I1 range must be greater than zero!')
    
    # interpolate II1 = f(u1,x2) using smooth cublic splines:
    UU1, XX2 = np.meshgrid(u1,x2)
    II1 = griddata((cU1, cX2), cI1, (UU1, XX2), method='cubic')  # cubic spline interpolation
    
    # determine vector gradient of I1(U1,X2) surface (vector elements are gradients along the U1 and X2 axes)
    g = np.gradient(II1, delta_x2, delta_u1)
    # dI1_dX2 <--> g[0] is the gradient in horizontal direction
    # dI1_dU1 <--> g[1] is the gradient in vertical direction
    
    # init arrays for gradient values:
    dI1_dX2 = np.empty(N); dI1_dX2[:] = np.nan;
    dI1_dU1 = np.empty(N); dI1_dU1[:] = np.nan;
    
    # find gradient values of the specifed (U1,I1) positions:
    logger.info('...find gradient values of the specifed (U1,I1) positions...')
    # interpolate the gradient data calculated above to the specified (U1/I1) point(s)

    # plot interpolated data (contours):
    ### fig = plt.figure()
    ### ax = fig.add_subplot(111, projection='3d')
    ### ax.plot_surface(UU1, XX2, II1)
    ## ax.plot_surface(UU1, XX2, g[1])
    ### plt.ioff()
    ### plt.show()
    
    
    
    # determine X2 (either U2 or I2) that corresponds to the specified (U1/I1) point(s):
    X2 = None
    logger.info('...find X2 values of the specifed (U1,I1) positions...')
    # interpolate X2 = f(U1,I1) in the same way above (smooth spline interpolation) to calculate the X2 value(s) at the (U1/I1) point(s)
    # interpolate II1 = f(u1,x2) using smooth cublic splines:
    UU1, II1 = np.meshgrid(u1,i1)
    X2 = griddata((cU1, cI1), cX2, (U1, I1), method='cubic')  # cubic spline interpolation

    
    
    return X2, dI1_dX2, dI1_dU1

