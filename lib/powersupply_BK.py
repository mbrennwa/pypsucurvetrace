"""
Python class to control B&K power supplies
"""

import serial
import sys
import time

# Python dictionary of known B&K power supply models (Vmin,Vmax,Imax,Pmax,VresolutionSet,IresolutionSet,VresolutionRead,IresolutionRead,MaxSettleTime)
BK_SPECS = {
		"9185B_HIGH":	( 0.0, 610.0,  0.35, 210,  0.02,  0.00001, 0.3,  0.0015, 2.0 ),  # 9185B in "HIGH" setting, confirmed working
		"9185B_LOW":	( 0.0, 400.0,  0.5 , 210,  0.02,  0.00001, 0.3,  0.0015, 2.0 )  # 9185B in "LOW" setting, confirmed working
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
		baud = 57600
		from pkg_resources import parse_version
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
		try:
			typestring = self._query('*IDN?').split(",") # <manufacturer>,<model>,<serial number>,<firmware version>,0
			
			# parse typestring:
			if len(typestring) < 1:
				raise RuntimeError ('No B&K power supply connected to ' + port)
			if not ( typestring[0].upper() == 'B&K PRECISION'):
				raise RuntimeError ('No B&K power supply connected to ' + port)
			if '9185B' in typestring[1]:
				self.MODEL = '9185B_' + voltagemode.upper()
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
			self.MAXSETTLETIME = v[8]
			self.READIDLETIME = self.MAXSETTLETIME/50

			# Clear status and errors:
			self._query('*CLS',answer=False)

			# Reset to factory default:
			self._query('SYStEM:RECALL:DEFAULT',answer=False)

			# Set voltage range
			if self.MODEL == '9185B_HIGH':
				self._query('SOURCE:VOLTAGE:RANGE HIGH',answer=False)
			if self.MODEL == '9185B_LOW':
				self._query('SOURCE:VOLTAGE:RANGE LOW',answer=False)


		except serial.SerialTimeoutException:
		    raise RuntimeError('No B&K powersupply connected to ' + port)
		except KeyError:
		    raise RuntimeError('Unknown B&K model ' + self.MODEL)
	
	def _query(self, cmd, answer=True, attempt = 1):
		"""
		tx/rx to/from PS
		"""

		if attempt > 10:
			raise RuntimeError('B&K PSU does not respond to ' + cmd + ' command after 10 attempts. Giving up...')
		elif attempt > 1:
			if self._debug:
				_BK_debug('*** Retrying (attempt ' + str(attempt) + ')...')

		# just in case, make sure the buffers are empty before doing anything
		self._Serial.reset_output_buffer()
		self._Serial.reset_input_buffer()
		time.sleep(0.03)

		if self._debug: _BK_debug('B&K <- %s\n' % cmd)
		self._Serial.write((cmd + '\n').encode())
		
		if not answer:
			ans = None
		else:
			ans = self._Serial.readline().decode('utf-8').rstrip("\n\r")
			if self._debug: _BK_debug('B&K -> %s\n' % ans)
			if ans == '':
				### _BK_debug('*** No answer from B&K PSU! Command: ' + cmd)
				self._Serial.flushOutput()			
				time.sleep(0.1)
				self._Serial.flushInput()
				time.sleep(0.1)			
				ans = self._query(cmd,True,attempt+1)

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


	def voltage(self, voltage):
		"""
		set voltage: silently saturates at VMIN and VMAX
		"""
		if voltage > self.VMAX:
			voltage = self.VMAX
		if voltage < self.VMIN:
			voltage = self.VMIN
		voltage = round (voltage/self.VRESSET) * self.VRESSET
		self._query('SOURCE:VOLTAGE ' + str(voltage),answer=False)


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


	def reading(self):
		"""
		read applied output voltage and current and if PS is in "CV" or "CC" mode
		"""

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

		return (V, I, S)


