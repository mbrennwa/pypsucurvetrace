"""
Python class to control KORAD (RND) power supplies
(This code follows the powersupply_PPS.py class)
"""

# Useful information about KORAD command set: https://sigrok.org/wiki/Korad_KAxxxxP_series

# NOTE: KORAD KWR103 commands are "VOUT?" (not "VOUT1?") or "ISET" (not "ISET1"), etc. for the other "1" commands given in the manual. The manual seems to be wrong!

import serial
import sys
import time
import logging

# set up logger:
logger = logging.getLogger('powersupply_KORAD')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


# Python dictionary of known KORAD (RND) power supply models (Vmin,Vmax,Imax,Pmax,VresolutionSet,IresolutionSet,VresolutionRead,IresolutionRead,VoffsetMax,IoffsetMax,MaxSettleTime)

KORAD_SPECS = {
		"KA3003P":	( 0.0, 31.0,  3.0,  90,  0.01,  0.001, 0.01,  0.001, 0.0, 0.0, 2.0 ) , # not confirmed
		"KA3005P":	( 0.0, 31.0,  5.1, 150,  0.01,  0.001, 0.01,  0.001, 0.0, 0.0, 2.0 ) , # confirmed (with the RND incarnation of the KA3005P)
		"KD3005P":	( 0.0, 31.0,  5.1, 150,  0.01,  0.001, 0.01,  0.001, 0.0, 0.0, 2.0 ) , # not confirmed
		"KA3010P":	( 0.0, 31.0, 10.0, 300,  0.01,  0.001, 0.01,  0.001, 0.0, 0.0, 2.0 ) , # not confirmed
		"KA6002P":	( 0.0, 60.0,  2.0, 120,  0.01,  0.001, 0.01,  0.001, 0.0, 0.0, 2.0 ) , # not confirmed
		"KA6003P":	( 0.0, 60.0,  3.0, 180,  0.01,  0.001, 0.01,  0.001, 0.0, 0.0, 2.0 ) , # not confirmed
		"KA6005P":	( 0.0, 31.0,  5.0, 300,  0.01,  0.001, 0.01,  0.001, 0.0, 0.0, 2.0 ) , # not confirmed
		"KD6005P":	( 0.0, 31.0,  5.0, 300,  0.01,  0.001, 0.01,  0.001, 0.0, 0.0, 2.0 ) , # not confirmed
		"KWR103":	( 0.0, 60.5, 15.0, 300, 0.001,  0.001, 0.001, 0.001, 0.0, 0.0, 2.0 )   # confirmed (with the RND incarnation of the KWR103
}

KORAD_TIMEOUT = 2.0

def _KORAD_debug(s):
	sys.stdout.write(s)
	sys.stdout.flush()

# KORAD:
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
#    .VOFFSETMAX
#    .IOFFSETMAX
#    .MAXSETTLETIME
#    .READIDLETIME
#    .MODEL

class KORAD(object):
	"""
	Class for KORAD (RND) power supply
	"""

	def __init__(self, port, debug=False,):
		'''
		PSU(port)
		port : serial port (string, example: port = '/dev/serial/by-id/XYZ_123_abc')
		debug: flag for debugging info (bool)
		'''
		# open and configure serial port:
		baud = 9600
		from pkg_resources import parse_version
		if parse_version(serial.__version__) >= parse_version('3.3') :
			# open port with exclusive access:
			self._Serial = serial.Serial(port, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=KORAD_TIMEOUT, exclusive = True)

		else:
			# open port (can't ask for exclusive access):
			self._Serial = serial.Serial(port, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=KORAD_TIMEOUT)

		time.sleep(0.2) # wait a bit unit the port is really ready

		self._Serial.flushInput()
		self._Serial.flushOutput()
		self._debug = bool(debug)
		try:
			typestring = self._query('*IDN?').split(" ")

			# parse typestring:
			if len(typestring) < 2:
				raise RuntimeError ('No KORAD power supply connected to ' + port)
			if not ( typestring[0].upper() in [ 'KORAD' , 'RND' , 'VELLEMAN' , 'TENMA' ] ):
				raise RuntimeError ('No KORAD power supply connected to ' + port)
			if 'KA3003P' in typestring[1]:
				self.MODEL = 'KA3003P'
			elif 'KA3005P' in typestring[1]:
				self.MODEL = 'KA3005P'
			elif 'KD3005P' in typestring[1]:
				self.MODEL = 'KD3005P'
			elif 'KA3010P' in typestring[1]:
				self.MODEL = 'KD3010P'
			elif 'KA6002P' in typestring[1]:
				self.MODEL = 'KA6002P'
			elif 'KA6003P' in typestring[1]:
				self.MODEL = 'KA6003P'
			elif 'KA6005P' in typestring[1]:
				self.MODEL = 'KA6005P'
			elif 'KD6005P' in typestring[1]:
				self.MODEL = 'KD6005P'
			elif 'KWR103' in typestring[1]:
				self.MODEL = 'KWR103'
			else:
				logger.warning ( 'Unknown KORAD model: ' + typestring[1] )
				self.MODEL = '?????'

			v = KORAD_SPECS[self.MODEL]
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

		except serial.SerialTimeoutException:
		    raise RuntimeError('No KORAD powersupply connected to ' + port)
		except KeyError:
		    raise RuntimeError('Unknown KORAD model ' + self.MODEL)
	
	def _query(self, cmd, answer=True, attempt = 1):
		"""
		tx/rx to/from PS
		"""

		if attempt > 10:
			raise RuntimeError('KORAD PSU does not respond to ' + cmd + ' command after 10 attempts. Giving up...')
		elif attempt > 1:
			if self._debug:
				_pps_debug('*** Retrying (attempt ' + str(attempt) + ')...')

		# just in case, make sure the buffers are empty before doing anything:
		# (it seems some KORADs tend to have issues with stuff dangling in their serial buffers)
		self._Serial.reset_output_buffer()
		self._Serial.reset_input_buffer()
		time.sleep(0.03)

		if self._debug: _KORAD_debug('KORAD <- %s\n' % cmd)
		self._Serial.write((cmd + '\n').encode())
		
		if not answer:
			ans = None
		else:
			ans = self._Serial.readline().decode('utf-8').rstrip("\n\r")
			if self._debug: _KORAD_debug('KORAD -> %s\n' % ans)
			if ans == '':
				### _KORAD_debug('*** No answer from KORAD PSU! Command: ' + cmd)
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

		if self.MODEL == "KWR103":
			self._query('OUT:%d' % state,answer=False)
		else:
			self._query('OUT%d' % state,answer=False)


	def voltage(self, voltage):
		"""
		set voltage: silently saturates at VMIN and VMAX
		"""
		if voltage > self.VMAX:
			voltage = self.VMAX
		if voltage < self.VMIN:
			voltage = self.VMIN
		voltage = round (1000*voltage) / 1000
		if self.MODEL == "KWR103":
			self._query('VSET:' + str(voltage),answer=False)
		else:
			self._query('VSET1:' + str(voltage),answer=False)


	def current(self, current):
		"""
		set current: silently saturates at IMIN and IMAX
		"""
		if current > self.IMAX:
			current = self.IMAX
		if current < 0.0:
			current = 0.0
		current = round (1000*current) / 1000
		self._query('ISET:' + str(current),answer=False)
		if self.MODEL == "KWR103":
			self._query('ISET:' + str(current),answer=False)
		else:
			self._query('ISET1:' + str(current),answer=False)


	def reading(self):
		"""
		read applied output voltage and current and if PS is in "CV" or "CC" mode
		"""
		if self.MODEL == "KWR103":
			Vq = 'VOUT?'
			Iq = 'IOUT?'

		else:
			Vq = 'VOUT1?'
			Iq = 'IOUT1?'

		# read voltage:
		k = 1
		while True:
			try:
				if k > 10:
					raise RuntimeException("Could not read voltage from KORAD PSU!")
				V = float (self._query(Vq))
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
					raise RuntimeException("Could not read current from KORAD PSU!")
				I = float (self._query(Iq))
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
					raise RuntimeException("Could not read output limit status from KORAD PSU!")
				S = self._query('STATUS?')
				if S.encode()[0] & 0b00000001: # test bit-1 for CV or CC
					S = 'CV'
				else:
					S = 'CC'
				break
			except:
				k = k+1
				self._Serial.reset_output_buffer()
				self._Serial.reset_input_buffer()
				time.sleep(0.05)
				pass

		return (V, I, S)
