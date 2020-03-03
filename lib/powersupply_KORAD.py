"""
Python class to control KORAD (RND) power supplies
(This code follows the powersupply_PPS.py class)
"""

# Useful information about KORAD command set: https://sigrok.org/wiki/Korad_KAxxxxP_series

# NOTE: KORAD KWR103 commands are "VOUT?" (not "VOUT1?") or "ISET" (not "ISET1"), etc. for the other "1" commands given in the manual. The manual seems to be wrong!

import serial
import sys

# Python dictionary of known KORAD (RND) power supply models (Vmin,Vmax,Imax,Pmax,Vresolution,Iresolution,MaxSettleTime)
KORAD_MODELS = { "KWR103": (0.0,60.5,15.0,300,0.001,0.001,3.0) 
		}

KORAD_TIMEOUT = 10.0

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
#    .VRES
#    .IRES
#    .MAXSETTLETIME
#    .SETTLEPOLLTIME
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

		self._Serial.flushInput()
		self._Serial.flushOutput()
		self._debug = bool(debug)
		try:
			typestring = self._query('*IDN?').split(" ")
			if len(typestring) < 2:
				raise RuntimeError ('No KORAD power supply connected to ' + port)
			if not ( typestring[0].upper() == 'KORAD' ):
				raise RuntimeError ('No KORAD power supply connected to ' + port)
			self.MODEL = typestring[1]
			v = KORAD_MODELS[self.MODEL]
			self.VMIN = v[0]
			self.VMAX = v[1]
			self.IMAX = v[2]
			self.PMAX = v[3]
			self.VRES = v[4]
			self.IRES = v[5]
			self.MAXSETTLETIME = v[6]
			self.SETTLEPOLLTIME = self.MAXSETTLETIME/50

		except serial.SerialTimeoutException:
		    raise RuntimeError('No KORAD powersupply connected to ' + port)
		except KeyError:
		    raise RuntimeError('Unknown KORAD model ' + self.MODEL)
	
	def _query(self, cmd, answer=True):
		"""
		tx/rx to/from PS
		"""
		if self._debug: _KORAD_debug('KORAD <- %s\n' % cmd)
		self._Serial.write((cmd + '\n').encode())
		
		if answer:
			ans = self._Serial.readline().decode('utf-8').rstrip("\n\r")
			if self._debug: _KORAD_debug('KORAD -> %s\n' % ans)

			return ans

	def output(self, state):
		"""
		enable/disable the PS output
		"""
		state = int(bool(state))
		self._query('OUT:%d' % state,answer=False)

	def voltage(self, voltage):
		"""
		set voltage: silently saturates at VMIN and VMAX
		"""
		if voltage > self.VMAX:
			voltage = self.VMAX
		if voltage < self.VMIN:
			voltage = self.VMIN
		voltage = round (1000*voltage) / 1000
		self._query('VSET:' + str(voltage),answer=False)

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

	def reading(self):
		"""
		read applied output voltage and current and if PS is in "CV" or "CC" mode
		"""
		V = float (self._query('VOUT?'))
		I = float (self._query('IOUT?'))
		S = self._query('STATUS?')
		if S.encode()[0] & 0b00000001: # test bit-1 for CV or CC
			S = 'CV'
		else:
			S = 'CC'

		return (V, I, S)

###	def settletime(self):
###		"""
###		estimate settle time to attain stable output at PSU terminals in seconds. The time is determined by the charging process of the built-in capacitor at the PSU output, which is controlled by the current limit and the size of amplitude of the change in the voltage setting. This function assumes the "worst case", wher the voltage setting is changed from 0.0 V to the max. voltage.
###		"""
###		Ilim = float (self._query('ISET?'))		
###		if Ilim > 0.0:
###			if self.MODEL == 'KWR103':
###				# DETERMINED THIS EMPIRICALLY
###				T = max( [ 0.40 , 0.1 / Ilim ] )
###			else:
###				raise RuntimeError('Settle time for ' + self.MODEL + ' not known.')	
###		else:
###			# just some sufficiently large value:
###			T = 2.0
###
###		return T
