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
# data classes / strucures #
############################

class preheat:
	U0 = None
	I0 = None
	Uc = None
	Ic = None
	T  = None


class measurement_data:

	def __init__ (self,datafile):
		self.rawdata = np.loadtxt(datafile, comments='%')
		self.CC_on = np.where( self.rawdata[:,4]+self.rawdata[:,9] == 0)
	
	def get_U1_meas (self,exclude_CC):
		if exclude_CC:
			x = self.rawdata[self.CC_on,2]
		else:
			x = self.rawdata[:,2]
		return x
		
	def get_I1_meas (self,exclude_CC):
		if exclude_CC:
			x = self.rawdata[self.CC_on,3]
		else:
			x = self.rawdata[:,3]
		return x
		
	def get_U2_set (self,exclude_CC):
		if exclude_CC:
			x = self.rawdata[self.CC_on,5]
		else:
			x = self.rawdata[:,5]
		return x
		
	def get_T (self,exclude_CC):
		if exclude_CC:
			try:
				x = self.rawdata[self.CC_on,10]
			except:
				x = np.matlib.repmat(None, len(exclude_CC))
		else:
			try:
				x = self.rawdata[:,10]
			except:
				x = np.matlib.repmat(None, len(self.rawdata[:,1]))
		return x		


############################
# read and parse data file #
############################

def read_datafile(datafile):
	'''
	data, label, preheat = read_datafile( datafile )
	
	Read data from PyPSUcurvetrace datafile.
	
	INPUT:
	datafile: file name/path of data file

	OUTPUT:
	data: measurement data (measurement_data struct)
	label: DUT/measurement label (string)
	preheat: DUT operating point at end of preheat/idle (preheat struct)
	'''

	# read file to parse header
	with open(datafile) as f:
		lines = f.read().split("\n")
	
	# find data label:
	label = None
	for i,line in enumerate(lines):
		if '* Sample: ' in line:
			label = line.split(': ')[1]

	# find operating point after pre-heat/idle:
	ph = preheat()
	for i,line in enumerate(lines):
		if '* OPERATING POINT AT END OF PREHEAT ' in line:
			u = line.split(': ')[1]
			u = u.split('=')
			ph.U0 = float(u[1].split('V')[0])
			ph.I0 = float(u[2].split('A')[0])
			ph.Uc = float(u[3].split('V')[0])
			ph.Ic = float(u[4].split('A')[0])
			try:
				ph.T = float(u[5].split('°C')[0])
			except:
				ph.T = None

	# load measurement data from file:
	data = measurement_data(datafile)

	return data, label, ph
