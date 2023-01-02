"""
Python class to control B&K power supplies
"""

import serial
import sys
import time
from math import ceil, log10
import logging

# set up logger:
logger = logging.getLogger('powersupply_BK')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


# Python dictionary of known B&K power supply models (Vmin,Vmax,Imax,Pmax,VresolutionSet,IresolutionSet,VresolutionRead,IresolutionRead,VoffsetMax,IoffsetMax,MaxSettleTime)
BK_SPECS = {
		"9185B_HIGH":	( 0.0, 610.0,  0.35, 210,  0.02,    0.00001, 0.3,    0.00001, 0.02, 0.0001, 2.0 ),  # 9185B in "HIGH" setting, confirmed working
		"9185B_LOW":	( 0.0, 400.0,  0.5 , 210,  0.02,    0.00001, 0.3,    0.00001, 0.02, 0.0001, 2.0 ),  # 9185B in "LOW" setting, confirmed working
		# "9120A":	    ( 0.0, 32.0,   3.0 , 96,   0.0005,  0.0001,  0.0001, 0.00001, 2.0 )   # 9120A, currently testing / under construction
		"9120A":	    ( 0.0, 32.0,   3.0 , 96,   0.0005,  0.0001,  0.0001, 0.00001, 0.012, 0.0002, 3.0 )   # 9120A, currently testing / under construction
}

BK_TIMEOUT = 2.0

def _BK_debug(s):
	sys.stdout.write(s)
	sys.stdout.flush()

# BK:
#    .output(state)
#    .voltage(voltage)
#    .current(current)
#    .reading()
#    .VMIN
#    .VMAX
#    .IMAX
#    .VRESSET
#    .IRESSET
#    .VRESREAD
#    .IRESREAD
#    .VOFFSETMAX
#    .IOFFSETMAX
#    .MAXSETTLETIME
#    .READIDLETIME
#    .MODEL

class BK(object):
	"""
	Class for B&K power supply.
	"""

	def __init__(self, port, debug=False,voltagemode='HIGH'):
		'''
		PSU(port)
		port : serial port (string, example: port = '/dev/serial/by-id/XYZ_123_abc')
		voltagemode: some models can work in LOW and HIGH voltage range
		debug: flag for debugging info (bool)
		'''

		self.MODEL = '?'

		# open and configure serial port:
		baud_rates = ( 57600, 38400, 19200, 14400, 9600, 4800 )
		
		from pkg_resources import parse_version
		typestring = None
		for baud in baud_rates:

			try:

				_BK_debug('*** Trying baud rate = ' + str(baud) + '...\n')

				if parse_version(serial.__version__) >= parse_version('3.3') :
					# open port with exclusive access:
					self._Serial = serial.Serial(port, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=BK_TIMEOUT, exclusive = True)

				else:
					# open port (can't ask for exclusive access):
					self._Serial = serial.Serial(port, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=BK_TIMEOUT)

				time.sleep(0.2) # wait a bit unit the port is really ready

				self._Serial.flushInput()
				self._Serial.flushOutput()
				self._debug = bool(debug)

				typestring = self._query('*IDN?', max_attempts = 1).split(",") # <manufacturer>,<model>,<serial number>,<firmware version>,0

				# break from the loop if successful connection:
				break
				
			except:
				# try to reset + close the serial port for the next attempt:
				self._Serial.reset_input_buffer()
				self._Serial.reset_output_buffer()
				self._Serial.close()
				time.sleep(1.5) # needs some time to calm down, BK 9120A needs a bit more than 1 second

		if typestring is None:
			raise RuntimeError('Could not connect to B&k power supply.')
				
		try:		
			# parse typestring:
			if len(typestring) < 1:
				raise RuntimeError ('No B&K power supply connected to ' + port)
			if not ( ( typestring[0].upper() == 'B&K PRECISION') or ( typestring[0].upper() == 'BK PRECISION') ):
				raise RuntimeError ('No B&K power supply connected to ' + port)
			if '9185B' in typestring[1]:
				self.MODEL = '9185B_' + voltagemode.upper()
			elif '9120A' in typestring[1]:
				self.MODEL = '9120A'
				logger.warning ( 'B&K 9120A communication tends to be unreliable. Be careful...' )
			else:
				logger.warning ( 'Unknown B&K model: ' + typestring[1] )
				self.MODEL = '?????'

			v = BK_SPECS[self.MODEL]
			self.VMIN = v[0]
			self.VMAX = v[1]
			self.IMAX = v[2]
			self.PMAX = v[3]
			self.VRESSET = v[4]
			self.IRESSET = v[5]
			self.VRESREAD = v[6]
			self.IRESREAD = v[7]
			self.VOFFSETMAX = v[8]
			self.IOFFSETMAX = v[9]
			self.MAXSETTLETIME = v[10]
			self.READIDLETIME = 0.02
			
			# helper fields to work around the issue with the readdout of the CV/CC limiter:
			self._VLIMITSETTING = None
			self._ILIMITSETTING = None

			# Clear status and errors:
			self._query('*CLS',answer=False)

			# Reset to default:
			self._query('*RST',answer=False)

			# Set voltage range
			if self.MODEL == '9185B_HIGH':
				self._query('SOURCE:VOLTAGE:RANGE HIGH',answer=False)
			if self.MODEL == '9185B_LOW':
				self._query('SOURCE:VOLTAGE:RANGE LOW',answer=False)
		except KeyError:
		    raise RuntimeError('Unknown B&K model ' + self.MODEL)

	
	def _query(self, cmd, answer=True, attempt = 1, max_attempts = 10):
		"""
		tx/rx to/from PS
		"""
		
		if attempt > max_attempts:
			raise RuntimeError('B&K PSU does not respond to ' + cmd + ' command after 10 attempts. Giving up...')
		elif attempt > 1:
			if self._debug:
				_BK_debug('*** Retrying (attempt ' + str(attempt) + ')...')

		# clean the pipes:
		self._Serial.flushOutput()
		self._Serial.flushInput()

		# send command to PSU:
		if self._debug:
			_BK_debug('B&K <- %s\n' % cmd)
		self._Serial.write((cmd + '\n').encode())
		self._Serial.flush() # wait until all data is written to the serial port

		# read answer (if requested):
		if not answer:
			ans = None
		else:
			ans = self._Serial.readline().decode('utf-8').rstrip("\n\r")
			if self._debug:
				_BK_debug('B&K -> %s\n' % ans)
			if ans == '':
				if self._debug:
					_BK_debug('*** No answer from B&K PSU! Command: ' + cmd)
				self._Serial.flushOutput()			
				time.sleep(0.1)
				self._Serial.flushInput()
				time.sleep(0.1)			
				ans = self._query(cmd,True,attempt+1, max_attempts)
				
		return ans
		

	def output(self, state):
		"""
		enable/disable the PS output
		"""
		state = int(bool(state))

		if state:
			self._query('OUTPUT ON',answer=False)
		else:
			self._query('OUTPUT OFF',answer=False)


	def voltage(self, volt):
		"""
		set voltage: silently saturates at VMIN and VMAX
		"""
		if volt > self.VMAX:
			volt = self.VMAX
		if volt < self.VMIN:
			volt = self.VMIN

		# round to closest setting value resolved by the PSU
		# (this may not exist / be resolved by the float type, so the float may have more digits than allowed!)
		volt = round(volt/self.VRESSET) * self.VRESSET
		
		# number of digits to be used in the command string:
		digits = ceil(-log10(self.VRESSET))
	
		# command string:
		fmt = "{:." + str(digits) + "f}"
		cmd = 'SOURCE:VOLTAGE ' + fmt.format(volt)

		# send command to PSU:
		self._query(cmd,answer=False)
		
		self._VLIMITSETTING = volt


	def current(self, current):
		"""
		set current: silently saturates at IMIN and IMAX
		"""
		if current > self.IMAX:
			current = self.IMAX
		if current < 0.0:
			current = 0.0

		# round to closest setting value resolved by the PSU
		# (this may not exist / be resolved by the float type, so the float may have more digits than allowed!)
		current = round (current/self.IRESSET) * self.IRESSET
		
		# number of digits to be used in the command string:
		digits = ceil(-log10(self.IRESSET))

		# command string:
		fmt = "{:." + str(digits) + "f}"
		cmd = 'SOURCE:CURRENT ' + fmt.format(current)
		
		# send command to PSU:
		self._query(cmd,answer=False)
		self._ILIMITSETTING = current
		
		
	def reading(self):
		"""
		read applied output voltage and current and if PS is in "CV" or "CC" mode
		"""
		
		self._query('*CLS', answer=False)
		
		# read voltage:
		k = 1
		while True:
			try:
				if k > 10:
					raise RuntimeException("Could not read voltage from B&K PSU!")
				V = float (self._query('MEASURE:VOLTAGE?'))
				break
			except:
				k = k+1
				self._Serial.reset_output_buffer()
				self._Serial.reset_input_buffer()
				time.sleep(0.05)
				pass

		# read current:
		k = 1
		while True:
			try:
				if k > 10:
					raise RuntimeException("Could not read current from B&K PSU!")
				I = float (self._query('MEASURE:CURRENT?'))
				break
			except:
				k = k+1
				self._Serial.reset_output_buffer()
				self._Serial.reset_input_buffer()
				time.sleep(0.05)
				pass

		# read output limit status:
		if self.MODEL == '9120A':
			# Reading the CV/CC mode from the PSU unit messes up the communication with the PSU
			### THIS SOMEHOW MESSES UP THE COMMUNICATION WITH THE 9120A, so threat his unit differently (see above):				
			### S = int(self._query('STATus:OPERation:CONDition?'))

			# Try to guesstimate the CV/CC mode from the V and I readings:
			S = 'CV'
			if self._ILIMITSETTING is None:
				# ILIMITSETTING has not yet been set in self.current()
				logger.debug('_ILIMITSETTING is None.')
				S = '?'
			else:
				if V-self.VRESREAD < 0.97*self._VLIMITSETTING:            # the voltage reading is lower than the VLIMITSETTING value, PSU did not reach the set value
					if I+self.IRESREAD >= 0.91*self._ILIMITSETTING:   # the current reading is close to the ILIMITSETTING value, so the current limiter is likely on and keeping the voltage low
						S = 'CC'

		elif self.MODEL in ['9185B_HIGH' , '9185B_LOW' ]:
		
			k = 1
			while True:
				try:
					if k > 10:
						raise RuntimeException("Could not read output limit status from B&K PSU!")
					S = self._query('OUTPUT:STATE?')
					break
				except:
					k = k+1
					self._Serial.reset_output_buffer()
					self._Serial.reset_input_buffer()
					time.sleep(0.05)
					pass
					
		else:
			raise RuntimeError('Cannot determine CV/CC mode for B&K model ' + self.MODEL)

		return (V, I, S)

