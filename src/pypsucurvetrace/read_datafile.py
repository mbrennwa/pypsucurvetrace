"""
Function to read pypsucurvetrace data files
"""

# imports:
import numpy as np
from pypsucurvetrace.curvetrace_tools import get_logger

# set up logger:
logger = get_logger('read_datafile')


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

	def __init__ (self,datafile=None):
		
		self.datafile = datafile
		
		if datafile is None:
			# set up an empty measurement_data object:
			self.rawdata = np.array([])
		
		else:
			# load data from file
			try:
				self.rawdata = np.genfromtxt(self.datafile, comments='%') # this deals nicely with NA values (for example if the heaterblock T values are missing)
			except Exception as e:
				logger.error('Could not load data from file ' + self.datafile + ' (' + str(e) + ').')
			
			# replace "-0.0" values by "0.0"	
			self.rawdata = np.where(self.rawdata==-0.0, 0.0, self.rawdata) 	
		
	def __get_column(self,column,exclude_CC):
		
		if len(self.rawdata.shape) == 1:
			if len(self.rawdata) == 0:
				x = np.array([])
			else:
				# one data line only
				x = self.rawdata[column]
				if exclude_CC:
					if len(self.get_CC_on()) == 0: # empty index
						x = np.array([])
		else:
			# two or more data lines
			if exclude_CC:
				x = self.rawdata[:,column][self.get_CC_on()]
			else:
				x = self.rawdata[:,column][:]
		return x
		
	def get_CC_on (self):
		if len(self.rawdata.shape) == 1:
			# zero or one data line only
			if len(self.rawdata) == 0:
				# empty data
				CC_on = self.rawdata
			else:
				# only one data line
				if self.rawdata[4]+self.rawdata[9] == 0:
					CC_on = [0] # index to first line
				else:
					CC_on = [] # empty index
		else:
			# two or more data lines
			CC_on = np.where( self.rawdata[:,4]+self.rawdata[:,9] == 0)
			
		return CC_on

	
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
		
	def add_data(self, x):
		if len(self.rawdata) == 0:
			self.rawdata = np.array(x)
		else:
			self.rawdata = np.vstack([self.rawdata, x])


############################
# read and parse data file #
############################

def read_datafile(datafile):
	'''
	data, label, preheat, r2control = read_datafile( datafile )
	
	Read data from pypsucurvetrace datafile.
	
	INPUT:
	datafile: file name/path of data file

	OUTPUT:
	data: measurement data (measurement_data struct)
	label: DUT/measurement label (string)
	preheat: DUT operating point at end of preheat/idle (preheat struct)
	r2control: resistor value used to control U2 voltage and to convert PSU U2 voltage to BJT base current
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

	r2 = None
	for i,line in enumerate(lines):
		if '* R2CONTROL' in line:
		    try:
    			u = line.split('=')
    			r2 = float(u[1].split('Ohm')[0])
		    except:
    			pass
		    break # break from the loop

	# load measurement data from file:
	data = measurement_data(datafile)

	return data, label, ph, r2
