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
    parser.add_argument('--U1range', nargs='+', type=argpair, help='U1 range to consider (value pair with min. and max value, e.g. --U1range 5,20')

    # I1 range:
    parser.add_argument('--I1range', nargs='+', type=argpair, help='I1 range to consider (value pair with min. and max value, e.g. --I1range 0.1,0.5')

    # BJT option:
    parser.add_argument('--bjtvbe', help='BJT VBE-on voltage for conversion of PSU U2 voltage to base current using R2CONTROL from the data file: Ibase = (U2-BJTVBE)/R2CONTROL')


    # Say Hello:
    say_hello('curveprocess', 'Extract and calculate parameters from pypsucurvetrace data')

    logger.warning('...not yet implemented... just messing around with ideas!')

    args = parser.parse_args()

    # determine data file(s):
    datafiles = args.datafiles

    # U1range, I1range:
    U1range = args.U1range
    I1range = args.I1range
    
    print(U1range)
    print(I1range)


def curves_RMSdelta(cdata1, cdata2, U1range, I1range, R2_val=None, BJT_VBE=None):
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
    
    if R2_val is not None:
        if BJT_VBE is not None:
            cX2_1 = convert_to_bjt(cX2_1, BJT_VBE, R2_val)
            cX2_2 = convert_to_bjt(cX2_2, BJT_VBE, R2_val)
    
    
    logger.warning('...calculate X2 RMS difference here...')
    
    deltaX2_RMS = None
    
    return deltaX2_RMS
