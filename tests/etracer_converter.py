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



##############################################################################################
# This is a draft bit of code to convert etracer CSV data files to pypsucurvetrace data file #
##############################################################################################



import pandas as pd
import sys


# set up logger:
sys.path.append( '../src' )
from pypsucurvetrace.curvetrace_tools import get_logger
logger = get_logger('curvetrace')



etracer_file = 'etracer_example_data.csv'
# ETRACER_CSV_FORMAT_VERSION:2.0
# Each curve-set contains 6 rows: [HV1_V HV1_I HV2_V HV2_I NEGV SWEEP_SOURCE]
# SWEEP_SOURCE types: 0:NONE 1:NEGV 2:HV2
# Each row starts with a curve-set sequential number starting from 0 followed by data pts.
# ETD_FILE:Z:/home/mbrennwa/etracer/tubecfg/12AT7.etd
# NEGV:ON NEGV_SWEEP:ON NEGV_SETTING: [0.0:4.0:0.5]
# HV2:ON HV2_LINK:ON HV2_SETTING:[0.0:0.0:0.0]


logger.info('Converting etracer file ' + etracer_file + '...')

# Check etracer file format version:
with open(etracer_file, 'r') as file:
    try:
        version = file.readline().strip().split(' ')[1].split(':')
        if version[0].upper() == 'ETRACER_CSV_FORMAT_VERSION':
            if version[1] != '2.0':
                logger.warning('Unknown etracer csv format version ' + version[1] + '. Be careful...')
        else:
            raise ValueError('CSV file does not appear to contain etracer data.')
    except Exception as e:
        logger.error(e)

# Read data:
X = pd.read_csv(etracer_file, comment='#', header=None)
idx = X[0].unique() # index to curvesets
logger.info('Number of curvesets = ' + str(len(idx)))
U1I1U2 = []
for i in idx:
    # parse and add curve data to C
    x = X[X[0]==i].dropna(axis=1, how='all').dropna(axis=1, how='all') # curve data at current index, without the NaN part
    u2 = x.iloc[4].median()
    for k in range(1,x.shape[1]): # skip the first entry (which is the etracer curve-set index)
        U1I1U2.append([x.iloc[0][k], x.iloc[1][k]/1000.0, u2])

# Output in pypsu format to STDOUT:
print('% DATA CONVERTED FROM ETRACER FILE ' + etracer_file)
for k in range(len(U1I1U2)):
    l = str(U1I1U2[k][0]) + ' ' + str(U1I1U2[k][1]) + ' ' + str(U1I1U2[k][0]) + ' ' + str(U1I1U2[k][1]) + ' ' + '0 ' + str(U1I1U2[k][2]) + ' ' + 'NA ' + str(U1I1U2[k][2]) + ' ' + 'NA 0 NA'
    print( l ) # output to STDOUT