"""
Python class to control B&K power supplies
"""

import serial
import sys
import time


# Python dictionary of known B&K power supply models (Vmin,Vmax,Imax,Pmax,VresolutionSet,IresolutionSet,VresolutionRead,IresolutionRead,VoffsetMax,IoffsetMax,MaxSettleTime)
BK_SPECS = {
		"9185B_HIGH":	( 0.0, 610.0,  0.35, 210,  0.02,    0.00001, 0.3,    0.0015, 0.02, 0.0, 2.0 ),  # 9185B in "HIGH" setting, confirmed working
		"9185B_LOW":	( 0.0, 400.0,  0.5 , 210,  0.02,    0.00001, 0.3,    0.0015, 0.02, 0.0, 2.0 ),  # 9185B in "LOW" setting, confirmed working
		# "9120A":	    ( 0.0, 32.0,   3.0 , 96,   0.0005,  0.0001,  0.0001, 0.00001, 2.0 )   # 9120A, currently testing / under construction
		"9120A":	    ( 0.0, 32.0,   3.0 , 96,   0.0005,  0.0001,  0.0001, 0.00001, 0.012, 0.0002, 2.0 )   # 9120A, currently testing / under construction
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
			else:
				print ( 'Unknown B&K model: ' + typestring[1] )
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
			self.READIDLETIME = self.MAXSETTLETIME/50
			
			# helper fields to work around the issue with the readdout of the CV/CC limiter:
			self._VLIMITSETTING = None
			self._ILIMITSETTING = None

			# Clear status and errors:
			self._query('*CLS',answer=False)

			# Reset to factory default:
			self._query('SYStEM:RECALL:DEFAULT',answer=False)

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

		if self._debug:
			_BK_debug('B&K <- %s\n' % cmd)
		self._Serial.write((cmd + '\n').encode())
		
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
		volt = round (volt/self.VRESSET) * self.VRESSET
		self._query('SOURCE:VOLTAGE ' + str(volt),answer=False)
		self._VLIMITSETTING = volt


	def current(self, current):
		"""
		set current: silently saturates at IMIN and IMAX
		"""
		if current > self.IMAX:
			current = self.IMAX
		if current < 0.0:
			current = 0.0
		current = round (current/self.IRESSET) * self.IRESSET
		self._query('SOURCE:CURRENT ' + str(current),answer=False)
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
					
				### # read voltage TWICE, as some units sometimes return awkward numbers with the first reading
				### V = float (self._query('MEASURE:VOLTAGE?'))
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
				### if I > 1.1*self.IMAX:
				### 	# The BK 9120A sometimes reports wrong current numbers that are way higher than the possible max value, so try one more time!
				### 	k = k+1
				### else:
				### 	break
				break
			except:
				k = k+1
				self._Serial.reset_output_buffer()
				self._Serial.reset_input_buffer()
				time.sleep(0.05)
				pass

		# read output limit status:
		### k = 1
		### while True:
		### 	try:
		### 		if k > 10:
		### 			raise RuntimeException("Could not read output limit status from B&K PSU!")
		### 			
		### 		# THIS SOMEHOW MESSES UP THE COMMUNICATION WITH THE PSU:				
		### 		S = int(self._query('STATus:OPERation:CONDition?'))
		### 		
		### 		if S&8 != 0:
		### 			S = 'CC'
		### 		elif S&4 != 0:
		### 			S = 'CV'
		### 		else:
		### 			S = None
		### 			print('BK PSU: Could not determine CV or CC condition.')
		### 		break
		### 	except:
		### 		k = k+1
		### 		self._Serial.reset_output_buffer()
		### 		self._Serial.reset_input_buffer()
		### 		time.sleep(0.05)
		### 		pass
		
		# Reading the CV/CC mode from the PSU unit messes up the communication with the PSU
		# Try to determine the CV/CC mode from the V and I readings:
		
		S = 'CV'
		if self._ILIMITSETTING is None:
			# ILIMITSETTING has not yet been set in self.current()
			print('_ILIMITSETTING is None.')
			S = '?'
		else:
			if I >= self._ILIMITSETTING - self.IRESREAD - self.IOFFSETMAX:
				# the current reading is close to the ILIMITSETTING value
				if V < self._VLIMITSETTING - self.VRESREAD - self.VOFFSETMAX:
					# the voltage reading is clearly lower to the VLIMITSETTING value
					S = 'CC'

		return (V, I, S)

