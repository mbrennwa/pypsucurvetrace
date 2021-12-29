"""
Function to read PyPSUcurvetrace data files
"""

# imports:
# import traceback
# import time
# import math
# import datetime
# import configparser
# import argparse
import numpy as np
# import os.path

############################
# read and parse data file #
############################

def read_datafile(datafile):
	
	# find data label:
	label = None
	with open(datafile) as f:
		lines = f.read().split("\n")
	for i,line in enumerate(lines):
		if '* Sample: ' in line:
			label = line.split(': ')[1]

	# find heaterblock T settings (if any):
	Tset_val = None
	Tset_tol = None
	# UNDER CONSTRUCTION -- FOLLOW THE EXAMPLE OF THE label ABOVE
	print('******** UNDER CONSTRUCTION: read_datafile GET HEATERBLOCK TEMPERATURE SETTINGS...')

	# load data from file:
	data = np.loadtxt(datafile, comments='%')

	return data, label, Tset_val, Tset_tol
