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

    # U1/I1 value(s) for parameter calculation:
    parser.add_argument('--U1I1', type=argpair, help='U1/I1 point(s) where the DUT parameters are determined. A single U1/I1 value pair is specified as [U1,I1] (for example: --U1I1 [20,0.5]). Multiple pairs can be specified as a list of pairs (for example: --U1I1 [15,0.5] [15,1] [20,0.7]), or as [U1_start:U1_end,I1_start:I1_end,N,scale] (for example: --U1I1 [0:30,0.1:1,10] for 10 points spaced linearly from U1=0...30V and I1=0.1...1A; or --U1I1 [0:30,0.1:1,10,log] for log spacing)')

    # use preheat values as target point for the parameter extraction:
    parser.add_argument('--preheat', action='store_true', help='Determine the parameters at the preheat values of U1 and I1; use the measured U2 preheat value instead of interpolating U2 from the curve data.')

    # BJT option:
    parser.add_argument('--bjtvbe', help='BJT VBE-on voltage for conversion of PSU U2 voltage to base current using R2CONTROL from the data file: Ibase = (U2-BJTVBE)/R2CONTROL')


    # Say Hello:
    say_hello('curveprocess', 'Extract and calculate parameters from pypsucurvetrace data')

    args = parser.parse_args()

    # determine data file(s):
    datafiles = args.datafiles

    # U1, I1:
    U1I1 = []
    if args.preheat:
        use_preheat = True
    else:
        use_preheat = False
        try:
            U1I1 = args.U1I1
            if U1I1 is None:
                raise RuntimeError('U1I1 argument missing.')
        except Exception as e:
            error_and_exit(logger, 'U1/I1 value(s) missing or invalid', e)
    
    # BJT Vbe-on value:
    BJT_VBE = None # default
    if args.bjtvbe:
	    BJT_VBE = float(args.bjtvbe)

    # prepare output, header:
    sep = ', '
    label_U1 = 'U1 (V)' # operating point voltage
    label_I1 = 'I1 (A)' # operating point current
    label_X2 = 'Ug (V)' # gate / grid current
    label_dI1_dU1 = 'go (A/V)' # output impedance
    label_dI1_dX2 = 'gm (A/V)' # transconductance
    label_dU1_dX2 = 'μ (V/V)'  # voltage gain
    if BJT_VBE is not None:
        # current controlled DUT (BJT), see also https://de.wikipedia.org/wiki/Mathematische_Beschreibung_des_Bipolartransistors#Kleinsignalparameter
        label_X2 = 'Ib (A)' # base current
        label_dI1_dX2 = 'hfe (A/A)' # current gain
        label_dU1_dX2 = 'rbe (V/A)' # 
    print( 'Filename' + sep + 'Sample' + sep + label_U1 + sep + label_I1 + sep + label_X2 + sep + label_dI1_dX2 + sep + label_dI1_dU1 + sep + label_dU1_dX2 + sep + 'T (°C)')
    
    # process all datafiles:
    for i in range(len(datafiles)):
    
        # read data file:
	    d, l, p, R2_val = read_datafile(datafiles[i])
	    
	    T = None
	    try:
	        T  = float(p.T)
	    except:
	        pass
	    
	    if use_preheat:
	        try:
	            U1I1 = [ [float(p.U1),], [float(p.I1),] ]
	            X2 = float(p.U2)
	            if BJT_VBE is not None:
	                X2 = convert_to_bjt(X2, BJT_VBE, R2_val)
	        except Exception as e:
	            error_and_exit(logger, 'Could not determine U1, I1 and U2 from preheat data', e)

	    for j in range(len(U1I1[0])):
            # determine DUT parameters at U1/I1 point(s):
	        XX2, dI1_dX2, dU1_dX2, dI1_dU1 = proc_curves(d, U1I1[0][j], U1I1[1][j], R2_val, BJT_VBE)
	        if not use_preheat:
	            X2 = XX2
	            
	        # print parameters:
	        Nd = 4
	        if T is None:
	            TT = "NA"
	        else:
	            TT = "{:.{}g}".format( T, Nd )
	        print( Path(d.datafile).stem + sep + l + sep +
	               "{:.{}g}".format( U1I1[0][j], Nd ) + sep +
	               "{:.{}g}".format( U1I1[1][j], Nd ) + sep +
	               "{:.{}g}".format( X2, Nd ) + sep +
	               "{:.{}g}".format( dI1_dX2, Nd ) + sep +
	               "{:.{}g}".format( dI1_dU1, Nd ) + sep +
	               "{:.{}g}".format( dU1_dX2, Nd ) + sep +
	               TT )
	    
	    
def proc_curves(cdata, U1, I1, R2_val=None, BJT_VBE=None):
    # determine derivatives of curve data at the (U1/I1) points. Convert to BJT/current-controlled data first, if R2_val and BJT_VBE are not None.
    #
    # INPUT:
    # cdata: curve-data object (output from read_datafile)
    # U1: U1 value where outputs should be calculated (float)
    # I1: I1 value where outputs should be calculated (float)
    #
    # OUTPUT:
    # X2: U2 or I2 corresponding to specified (U1/I1) poins
    # dI1_dX2: dI1/dU2 or dI1/dI2 derivative(s) at point (U1/I1), aka. gm (transconductance) or hfe (current gain)
    # dU1_dX2: dU1/dU2 or dU1/dI2 derivative(s) at point (U1/I1), aka. μ (gain)
    # dI1_dU1: dI1/dU1 derivative(s) at point (U1/I1), aka. go (output impedance)
    
    # get curve data:
    cU1 = cdata.get_U1_meas(exclude_CC = True)
    cX2 = cdata.get_U2_set(exclude_CC = True)
    cI1 = cdata.get_I1_meas(exclude_CC = True)
     
    if R2_val is not None:
        if BJT_VBE is not None:
            cX2 = convert_to_bjt(cX2, BJT_VBE, R2_val)
            
    # grid points for interpolation:
    scale = 100
    delta_u1 = np.nan
    delta_i1 = np.nan
    delta_x2 = np.nan
    u1 = np.unique(cU1)
    i1 = np.unique(cI1)
    x2 = np.unique(cX2)
    if len(u1) > 1 and len(i1) > 1 and len(x2) > 1:
        try:
            u = np.unique(cU1); delta_u1 = (u.max()-u.min())/(len(u)-1)/scale
            u = np.unique(cI1); delta_i1 = (u.max()-u.min())/(len(u)-1)/scale
            u = np.unique(cX2); delta_x2 = (u.max()-u.min())/(len(u)-1)/scale
        except:
            pass
    if delta_u1 == 0 or np.isnan(delta_u1):
        error_and_exit(logger, 'U1 range must be greater than zero!')
    if delta_i1 == 0 or np.isnan(delta_i1):
        error_and_exit(logger, 'I1 range must be greater than zero!')
    if delta_x2 == 0 or np.isnan(delta_x2):
        error_and_exit(logger, 'U2 range must be greater than zero!')
    
    # interpolation coordinates for U1, I1 and X2 (only use the range that is relevant for analysis around the (U1/I1) point)
    NG = 3 # number of grid points near U1 and I1 (don't need much)
    u1 = np.arange(U1-NG*delta_u1, U1+NG*delta_u1+delta_u1/2, delta_u1)
    i1 = np.arange(I1-NG*delta_i1, I1+NG*delta_i1+delta_i1/2, delta_i1)
    x2 = np.arange(cX2.min(), cX2.max()+delta_x2/2, delta_x2)


    ##########################################
    # determine dI1_dX2, dI1_dU1 and dU1_dX2 #
    ##########################################

    # determine smooth function II1 = f(u1,x2):
    UU1, XX2 = np.meshgrid(u1,x2)
    II1 = griddata((cU1, cX2), cI1, (UU1, XX2), method='cubic')  # cubic spline interpolation
    
    # determine vector gradient of II1(u1,x2) surface (vector elements are gradients along the u1 and x2 axes)
    g = np.gradient(II1, delta_x2, delta_u1)
    # dI1_dX2 <--> g[0] is the gradient in horizontal direction
    # dI1_dU1 <--> g[1] is the gradient in vertical direction
    
    # find gradient values of the specifed (U1,I1) position:
    try:
        l = np.nanargmin(abs(u1-U1)) # index to u1 value closest to U1
        k = np.nanargmin(abs(II1[:,l]-I1)) # index to II1[:,l] value closest to I1
        dI1_dX2 = g[0][k,l]
        dI1_dU1 = g[1][k,l]
    except:
        dI1_dX2 = np.nan
        dI1_dU1 = np.nan

    dU1_dX2 = dI1_dX2 / dI1_dU1


    ######################
    # determine X2 value #
    ######################
    
    X2 = griddata((cU1, cI1), cX2, (U1, I1), method='linear') # linear interpolation (cubic spline tends to screw up somehow...)

    return X2, dI1_dX2, dU1_dX2, dI1_dU1
