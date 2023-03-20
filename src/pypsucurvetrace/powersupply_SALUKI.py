"""
Python class to control SALUKI / MAYNUO power supplies
"""

import serial
import sys
import time
from math import ceil, log10
from pypsucurvetrace.curvetrace_tools import get_logger

# set up logger:
logger = get_logger('powersupply_SALUKI')


# Python dictionary of known SALUKI power supply models (Vmin,Vmax,Imax,Pmax,VresolutionSet,IresolutionSet,VresolutionRead,IresolutionRead,VoffsetMax,IoffsetMax,MaxSettleTime)
SALUKI_SPECS = {
		"SPS811":	( 0.0, 30.0,  5.0, 30, 0.0005, 0.0001,  0.0001, 0.00001,  0.0005, 0.0001, 1.0 ),  # SPS811,untested
		"SPS812":	( 0.0, 75.0,  2.0, 30, 0.001,  0.00005, 0.0001, 0.00001,  0.0005, 0.0001, 1.0 ),  # SPS812,untested
		"SPS813":	( 0.0, 150.0, 1.0, 30, 0.001,  0.00001, 0.0001, 0.00001,  0.0005, 0.0001, 1.0 ),  # SPS813,untested
		"SPS831":	( 0.0, 30.0,  1.0, 30, 0.0005, 0.00001, 0.0001, 0.000001, 0.0005, 0.0001, 1.0 ),  # SPS831, confirmed working
		
}

SALUKI_TIMEOUT = 2.0

def _SALUKI_debug(s):
	sys.stdout.write(s)
	sys.stdout.flush()

# SALUKI:
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

class SALUKI(object):
	"""
	Class for SALUKI power supply.
	"""

	def __init__(self, port, debug=False):
		'''
		PSU(port)
		port : serial port (string, example: port = '/dev/serial/by-id/XYZ_123_abc')
		debug: flag for debugging info (bool)
		'''

		self.MODEL = '?'

		# open and configure serial port:
		baud_rates = ( 9600, 57600, 38400, 19200, 14400, 4800 )
		
		from pkg_resources import parse_version
		typestring = None
		for baud in baud_rates:

			try:
			
				if parse_version(serial.__version__) >= parse_version('3.3') :
					# open port with exclusive access:
					self._Serial = serial.Serial(port, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=SALUKI_TIMEOUT, exclusive = True)

				else:
					# open port (can't ask for exclusive access):
					self._Serial = serial.Serial(port, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=SALUKI_TIMEOUT)

				time.sleep(0.2) # wait a bit unit the port is really ready
				
				self._Serial.flushInput()
				self._Serial.flushOutput()
				self._debug = bool(debug)

				typestring = self._query('*IDN?', max_attempts = 1) # <manufacturer>,<model>,<serial number>,<firmware version>,0

				# break from the loop if successful connection:
				break
				
			except:
				# try to reset + close the serial port for the next attempt:
				self._Serial.reset_input_buffer()
				self._Serial.reset_output_buffer()
				self._Serial.close()
				time.sleep(1.0) # needs some time to calm down

		if typestring is None:
			raise RuntimeError('Could not connect to SALUKI power supply.')
				
		try:		
			# parse typestring:
			if len(typestring) < 1:
				raise RuntimeError ('No SALUKI power supply connected to ' + port)
			
			typestring = typestring.upper()
			typestring = typestring.replace('MAYNUO', 'SALUKI')
			typestring = typestring.split(',')
			
			# Maynuo types: http://www.maynuo.com/english/pro.asp?tid=31
			
			if not ( typestring[0] == 'SALUKI' ):
				raise RuntimeError ('No SALUKI power supply connected to ' + port)
			
			if typestring[1] in ('M8831', 'SPS831'):
				self.MODEL = 'SPS831'
			
			elif typestring[1] in ('M8811', 'SPS811'):
				self.MODEL = 'SPS811'
				logger.warning ( 'Operation of SALUKI ' + self.MODEL + ' with pypsucurvetrace is untested -- be careful!' )
			
			elif typestring[1] in ('M8812', 'SPS812'):
				self.MODEL = 'SPS812'
				logger.warning ( 'Operation of SALUKI ' + self.MODEL + ' with pypsucurvetrace is untested -- be careful!' )
			
			elif typestring[1] in ('M8813', 'SPS813'):
				self.MODEL = 'SPS813'
				logger.warning ( 'Operation of SALUKI ' + self.MODEL + ' with pypsucurvetrace is untested -- be careful!' )
			
			else:
				logger.warning ( 'Unknown SALUKI model: ' + typestring[1] )
				self.MODEL = '?????'

			v = SALUKI_SPECS[self.MODEL]
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
			
			# helper fields to work around the missing readdout of the CV/CC mode:
			self._VLIMITSETTING = None
			self._ILIMITSETTING = None

			# Clear status and errors:
			self._query('*CLS',answer=False)

			# Reset to default:
			self._query('*RST',answer=False)

		except KeyError:
		    raise RuntimeError('Unknown SALUKI model ' + self.MODEL)

	
	def _query(self, cmd, answer=True, attempt = 1, max_attempts = 10):
		"""
		tx/rx to/from PS
		"""
		
		if attempt > max_attempts:
			raise RuntimeError('SALUKI PSU does not respond to ' + cmd + ' command after 10 attempts. Giving up...')
		elif attempt > 1:
			if self._debug:
				_SALUKI_debug('*** Retrying (attempt ' + str(attempt) + ')...')

		# clean the pipes:
		self._Serial.flushOutput()
		self._Serial.flushInput()

		# send command to PSU:
		if self._debug:
			_SALUKI_debug('SALUKI <- %s\n' % cmd)
		self._Serial.write((cmd + '\n').encode())
		self._Serial.flush() # wait until all data is written to the serial port

		# read answer (if requested):
		if not answer:
			ans = None
		else:
			ans = self._Serial.readline().decode('utf-8').rstrip("\n\r")
			if self._debug:
				_SALUKI_debug('SALUKI -> %s\n' % ans)
			if ans == '':
				if self._debug:
					_SALUKI_debug('*** No answer from SALUKI PSU! Command: ' + cmd)
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
			self._query('OUTPUT 1',answer=False)
		else:
			self._query('OUTPUT 0',answer=False)


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
		cmd = 'VOLTAGE ' + fmt.format(volt)

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
		cmd = 'CURRENT ' + fmt.format(current)
		
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
					raise RuntimeException("Could not read voltage from SALUKI PSU!")
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
					raise RuntimeException("Could not read current from SALUKI PSU!")
				I = float (self._query('MEASURE:CURRENT?'))
				break
			except:
				k = k+1
				self._Serial.reset_output_buffer()
				self._Serial.reset_input_buffer()
				time.sleep(0.05)
				pass

		# determine / guess output limit status:
		# (see email from sales01@salukitec.com 20 March 2023: The internal judgment standard of the instrument is that if the difference between the actual current and the current setting value is within 1mA, it will display CC (constant current); if the difference between the actual voltage and the voltage setting value is within 5mV, it will display CV (constant voltage). Errors are all exceeded, nothing is displayed (neither CV nor CC are displayed)
		if abs(I - self._ILIMITSETTING) <= 0.001:
		    S = 'CC'
		    
		elif abs(V - self._VLIMITSETTING) <= 0.005:
		    S = 'CV'
		    
		else:
		    S = '?'

		return (V, I, S)
