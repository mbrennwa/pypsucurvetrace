"""
Python class for abstract power supply objects.
Classes of specific real-world power supplies will derive from this class.
"""

import lib.powersupply_PPS as powersupply_PPS
import lib.powersupply_KORAD as powersupply_KORAD

# PSU object:
#    .setVoltage(voltage)   set voltage
#    .setCurrent(current)   set current
#    .turnOff()   	    turn PSU output off
#    .turnOn()   	    turn PSU output on
#    .read()                read current voltage, current, and limiter mode (voltage or current limiter active)
#    .settletime()             estimated settle time to attain stable voltage + current at PSU output after changing the setpoint (s)
#    .VMAX                  max. supported voltage (V)
#    .VMIN                  min. supported voltage (V)
#    .IMAX                  max. supported current (V)
#    .PMAX                  max. supported power (W)
#    .VRES                  resolution of voltage readings (V)
#    .IRES                  resolution of current readings (A)
#    .TEST_VSTART           start value for test (V)
#    .TEST_VEND             end value for test (V)
#    .TEST_ILIMIT           current limit for test (A)
#    .TEST_PLIMIT           power limit for test (W)
#    .TEST_VIDLE            voltage limit for idle conditions during test (V)
#    .TEST_IIDLE            current limit for idle conditions during test (A)
#    .TEST_N                number of test voltage steps (V)
#    .TEST_POLARITY         polarity of connections to the PSU (1 or -1)
#    .COMMANDSET            commandset type string (indicating Voltcraft/Mason, Korad/RND, SCPI, etc.)
#    .MODEL                 PSU model string
#    .CONNECTED             Flag indicating if connection between computer and PSU is set up (bool)
#    .CONFIGURED            Flag indicating if test conditions have between configured (bool)

class PSU:
	"""
	Abstract power supply (PSU) class
	"""

	def __init__(self, port=None, commandset=None, label=None):
		'''
		PSU(port, type, label)
		port : serial port (string, example: port = '/dev/serial/by-id/XYZ_123_abc')
		commandset : specifies computer interface / command set (string).
			Voltcraft PPS / Mason: commandset = 'Voltcraft'
			Korad / RND: commandset = 'Korad'
			SCPI interface: commandset = 'SCPI'
		label: label or name to be used to describe / identify the PSU unit (string)
		'''

		# init generic PSU:
		self.VMIN = 0.0
		self.VMAX = 0.0
		self.IMAX = 0.0
		self.PMAX = 0.0
		self.VRES = 0.0
		self.IRES = 0.0
		self.TEST_VSTART = 0.0
		self.TEST_VEND = 0.0
		self.TEST_ILIMIT = 0.0
		self.TEST_PLIMIT = 0.0
		self.TEST_VIDLE = 0.0
		self.TEST_IIDLE = 0.0
		self.TEST_N = 1
		self.TEST_POLARITY = 1
		self.LABEL = label
		self.COMMANDSET = commandset
		self.MODEL = 'UNKNOWN'
		self.CONNECTED = False
		self.CONFIGURED = False

		# check inputs:
		if not port:
			print (label + ': cannot connect to power supply (no serial port specified).')
			
		elif not commandset:
			print (label + ': cannot connect to power supply (no type / command set specified).')

		elif not label:
			print (label + ': cannot set up power supply (no label specified).')

		# connect to the PSU and set it up:
		else:
			self.COMMANDSET == self.COMMANDSET.upper()
			if self.COMMANDSET == 'VOLTCRAFT':
				print ('NOT YET IMPLEMENTED: Connect to Voltcraft / Mason PPS')

			elif self.COMMANDSET == 'KORAD':
				self._PSU = powersupply_KORAD.KORAD(port)
				self.VMIN = self._PSU.VMIN
				self.VMAX = self._PSU.VMAX
				self.IMAX = self._PSU.IMAX
				self.PMAX = self._PSU.PMAX
				self.VRES = self._PSU.VRES
				self.IRES = self._PSU.IRES
				self.MODEL = self._PSU.MODEL
				self.CONNECTED = True

			else:
				raise RuntimeError ('Unknown commandset ' + commandset + '! Cannot continue...')

		


	########################################################################################################
	

	def setVoltage(self,value):
		"""
		PSU.setVoltage(value)
		
		Set PSU voltage.
		
		INPUT:
		value: voltage value (float)
		
		OUTPUT:
		(none)
		"""
		
		if self.COMMANDSET == 'KORAD':
			self._PSU.voltage(value)
		elif self.COMMANDSET == 'VOLTCRAFT':
			self._PSU.voltage(value)
		else:
			raise RuntimeError('Cannot set voltage on power supply with ' + self.COMMANDSET + ' command set.')


	########################################################################################################
	

	def setCurrent(self,value):
		"""
		PSU.setCurrent(value)
		
		Set PSU current.
		
		INPUT:
		value: current value (float)
		
		OUTPUT:
		(none)
		"""
		
		if self.COMMANDSET == 'KORAD':
			self._PSU.current(value)
		elif self.COMMANDSET == 'VOLTCRAFT':
			self._PSU.current(value)
		else:
			raise RuntimeError('Cannot set current on power supply with ' + self.COMMANDSET + ' command set.')



	########################################################################################################
	

	def turnOff(self):
		"""
		PSU.turnOff()
		
		Turn off PSU output
		
		INPUT:
		(none)

		OUTPUT:
		(none)
		"""

		if self.COMMANDSET == 'KORAD':
			self._PSU.output(False)
			self._PSU.voltage(self.VMIN)
			self._PSU.current(0.0)

		elif self.COMMANDSET == 'VOLTCRAFT':
			self._PSU.output(False)
			self._PSU.voltage(self.VMIN)
			self._PSU.current(0.0)

		else:
			raise RuntimeError('Cannot turn off power supply with ' + self.COMMANDSET + ' command set.')



	########################################################################################################
	

	def turnOn(self):
		"""
		PSU.turnOn()
		
		Turn on PSU output
		
		INPUT:
		(none)

		OUTPUT:
		(none)
		"""

		if self.COMMANDSET == 'KORAD':
			self._PSU.output(True)
		elif self.COMMANDSET == 'VOLTCRAFT':
			self._PSU.output(True)
		else:
			raise RuntimeError('Cannot turn on power supply with ' + self.COMMANDSET + ' command set.')


	########################################################################################################
	

	def read(self):
		"""
		PSU.read()
		
		Read current output: voltage, current, limiting mode (CV or CC) 
		
		INPUT:
		(none)

		OUTPUT:
		V: voltage in Volts (float)
		I: current in Amps (float)
		L: limiter mode, 'CV' = voltage limit, 'CC' = current limit (string)
		"""

		if self.COMMANDSET == 'KORAD':
			V,I,L = self._PSU.reading()
		elif self.COMMANDSET == 'VOLTCRAFT':
			V,I,L = self._PSU.reading()
		else:
			raise RuntimeError('Cannot read values from power supply with ' + self.COMMANDSET + ' command set.')

		return (V,I,L)



	########################################################################################################
	

	def settletime(self):
		"""
		Estimate settle time to attain stable output at PSU terminals in seconds. The time is determined by the charging process of the built-in capacitor at the PSU output, which is controlled by the current limit and the size of amplitude of the change in the voltage setting. This function assumes the "worst case", wher the voltage setting is changed from 0.0 V to the max. voltage.

		INPUT:
		(none)

		OUTPUT:
		T: settle time in seconds (float)
		"""
		
		if self.COMMANDSET == 'KORAD':
			T = self._PSU.settletime()
		else:
			raise RuntimeError('Cannot estimate settle time for power supply with ' + self.COMMANDSET + ' command set.')

		return T
