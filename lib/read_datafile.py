"""
Function to read PyPSUcurvetrace data files
"""

# imports:
import numpy as np
import logging

# set up logger:
logger = logging.getLogger('read_datafile')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


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
		if len(self.rawdata.shape) == 1:
			# one data line only
			if len(self.rawdata) == 0:
				# empty data
				self.CC_on = self.rawdata
			else:
				# only one data line
				if self.rawdata[4]+self.rawdata[9] == 0:
					self.CC_on = [0] # index to first line
				else:
					self.CC_on = [] # empty index
		else:
			# two or more data lines
			self.CC_on = np.where( self.rawdata[:,4]+self.rawdata[:,9] == 0)
		
		# replace "-0.0" values by "0.0"	
		self.rawdata = np.where(self.rawdata==-0.0, 0.0, self.rawdata) 	
		
		self.datafile = datafile
		
	def __get_column(self,column,exclude_CC):
		if len(self.rawdata.shape) == 1:
			# one data line only
			x = self.rawdata[column]
			if exclude_CC:
				if len(self.CC_on) == 0: # empty index
					x = []
			x = np.array(x)
		else:
			# two or more data lines
			if exclude_CC:
				x = self.rawdata[:,column][self.CC_on]
			else:
				x = self.rawdata[:,column][:]
		return x
	
	def get_U1_meas (self,exclude_CC):
		return self.__get_column(2,exclude_CC)
		
	def get_I1_meas (self,exclude_CC):
		return self.__get_column(3,exclude_CC)
				
	def get_U2_set (self,exclude_CC):
		return self.__get_column(5,exclude_CC)
				
	def get_T (self,exclude_CC):
		try:
			T = self.__get_column(10,exclude_CC)
		except:
			if exclude_CC:
				T = np.matlib.repmat(None, len(exclude_CC))
			else:
				T = np.matlib.repmat(None, len(self.rawdata[:,1]))
		return T		


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
			break # break from the loop

	# find operating point after pre-heat/idle:
	ph = preheat()
	for i,line in enumerate(lines):
		if '* OPERATING POINT AT END OF PREHEAT ' in line:
			u = line.replace("Uc = U0=", "U0=") # workaround for buggy output from curvetrace
			u = u.split(': ')[1]
			u = u.split('=')
			ph.U0 = float(u[1].split('V')[0])
			ph.I0 = float(u[2].split('A')[0])
			ph.Uc = float(u[3].split('V')[0])
			ph.Ic = float(u[4].split('A')[0])
			try:
				ph.T = float(u[5].split('°C')[0])
			except:
				ph.T = None
			break # break from the loop

	# load measurement data from file:
	data = measurement_data(datafile)

	return data, label, ph
