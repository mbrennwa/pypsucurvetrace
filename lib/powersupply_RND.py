"""
Python class to control RND power supplies
(This code follows the powersupply_PPS.py class) 
"""

import serial
import sys

RND_TIMEOUT = 10.0

def _rnd_debug(s):
	sys.stdout.write(s)
	sys.stdout.flush()

# RND(port='/dev/ttyUSB0'):
#    .output(state)
#    .voltage(voltage)
#    .current(current)
#    .reading()
#    .VMAX
#    .IMAX
#    .MODEL

class RND(object):
	"""
	Class for RND power supply
	"""

	def __init__(self, port):
		'''
		PSU(port)
		port : serial port (string, example: port = '/dev/serial/by-id/XYZ_123_abc')
		'''
		# open and configure serial port:\n    
		from pkg_resources import parse_version
		if parse_version(serial.__version__) >= parse_version('3.3') :
			# open port with exclusive access:
			self._Serial = serial.Serial(port, timeout=RND_TIMEOUT, exclusive = True)

		else:
			# open port (can't ask for exclusive access):
			self._Serial = serial.Serial(port, timeout=RND_TIMEOUT)

		self._Serial.flushInput()
		self._Serial.flushOutput()
		self._debug = bool(debug)
		try:
		    model = self._query('*IDN?')
		    self._MODEL = PPS_MODELS[model]
		    self._VMAX = model[0]
		    self._IMAX = model[1]
		except serial.SerialTimeoutException:
		    raise RuntimeError("No RND powersupply "
				       "connected to %s" % port)
		except KeyError:
		    raise RuntimeError("Unkown Voltcraft PPS model with "
				       "max V: %f, I: %f" % model)
		if bool(reset):
		    self.output(0)
		    self.voltage(0)
		    self.current(0)
		if not (prom is None):
		    self.use_preset(prom)
	
	def _query(self, cmd):
		"""
		tx/rx to/from PS
		"""
		if self._debug: _rnd_debug("RND <- %s<CR>\n" % cmd)
		self._Serial.write((cmd + '\r').encode())

		ans = elf._Serial.readline()
		if self._debug: _rnd_debug("RND -> %s<CR>\n" % ans)

		return ans

	def output(self, state):
		"""
		enable/disable the PS output
		"""
		state = int(not bool(state))
		self._query("SOUT%d" % state)

	def voltage(self, voltage):
		"""
		set voltage: silently saturates at 0 and VMAX
		"""
		voltage = max(min(int(float(voltage) * 10), int(self.VMAX*10)), 0)
		self._query("VOLT%03d" % voltage)

	def current(self, current):
		"""
		set current: silently saturates at 0 and IMAX
		"""
		current = max(min(int(float(current) * self.IMULT), int(self.IMAX * self.IMULT)), 0)
		self._query("CURR%03d" % current)

	def reading(self):
		"""
		read applied output voltage and current and if PS is in "CV" or "CC" mode
		"""
		s = self._query("GETD")
		V = int(s[0:4]) / 100.
		I = int(s[4:8]) / 100.
		MODE = bool(int(s[8]))
		return (V, I, ("CV", "CC")[MODE])
