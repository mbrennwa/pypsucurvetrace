"""
Python class for abstract power supply objects.
Classes of specific real-world power supplies will derive from this class.
"""

import time
import numpy as np
import lib.powersupply_VOLTCRAFT as powersupply_VOLTCRAFT
import lib.powersupply_KORAD as powersupply_KORAD

# PSU object:
#    .setVoltage(voltage)   set voltage
#    .setCurrent(current)   set current
#    .turnOff()   	    turn PSU output off
#    .turnOn()   	    turn PSU output on
#    .read()                read current voltage, current, and limiter mode (voltage or current limiter active)
#    #### .settletime()             estimated settle time to attain stable voltage + current at PSU output after changing the setpoint (s)
#    .VMAX                  max. supported voltage (V)
#    .VMIN                  min. supported voltage (V)
#    .IMAX                  max. supported current (V)
#    .PMAX                  max. supported power (W)
#    .VRES                  resolution of voltage readings (V)
#    .IRES                  resolution of current readings (A)
#    .MAXSETTLETIME         max. time allowed to attain stable output values (will complain if output not stable after this time) (s)
#    .SETTLEPOLLTIME        time between readings for checking if output values of newly set voltage/current values are at set point (s)
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
		self.MAXSETTLETIME = 0.0
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
				self._PSU = powersupply_VOLTCRAFT.VOLTCRAFT(port,debug=False)
				self.VMIN = self._PSU.VMIN
				self.VMAX = self._PSU.VMAX
				self.IMAX = self._PSU.IMAX
				self.PMAX = self._PSU.PMAX
				self.VRES = self._PSU.VRES
				self.IRES = self._PSU.IRES
				self.MAXSETTLETIME = self._PSU.MAXSETTLETIME
				self.SETTLEPOLLTIME = self._PSU.SETTLEPOLLTIME
				self.MODEL = self._PSU.MODEL
				self.CONNECTED = True

			elif self.COMMANDSET == 'KORAD':
				self._PSU = powersupply_KORAD.KORAD(port,debug=False)
				self.VMIN = self._PSU.VMIN
				self.VMAX = self._PSU.VMAX
				self.IMAX = self._PSU.IMAX
				self.PMAX = self._PSU.PMAX
				self.VRES = self._PSU.VRES
				self.IRES = self._PSU.IRES
				self.MAXSETTLETIME = self._PSU.MAXSETTLETIME
				self.SETTLEPOLLTIME = self._PSU.SETTLEPOLLTIME
				self.MODEL = self._PSU.MODEL
				self.CONNECTED = True

			else:
				raise RuntimeError ('Unknown commandset ' + commandset + '! Cannot continue...')

		


	########################################################################################################
	

	def setVoltage(self,value,wait_stable):
		"""
		PSU.setVoltage(value,wait_stable)
		
		Set PSU voltage.
		
		INPUT:
		value: voltage set-point value (float)
		wait_stable: wait until output voltage reaches the set-point value (bool)
		
		OUTPUT:
		(none)
		"""
		
		if self.COMMANDSET == 'KORAD':
			self._PSU.voltage(value)
		elif self.COMMANDSET == 'VOLTCRAFT':
			self._PSU.voltage(value)
		else:
			raise RuntimeError('Cannot set voltage on power supply with ' + self.COMMANDSET + ' command set.')

		# wait for stable output voltage:
		if wait_stable:
			stable = False
			t0 = time.time() # start time (now)
			while not time.time() > t0+self.MAXSETTLETIME:
				v = self.read()[0]
				if abs( v - value) <= 1.3*self.VRES/2:
					stable = True
					break
				else:
					time.sleep(self.SETTLEPOLLTIME)
			if not stable:
				print (self.LABEL + ' warning: voltage setpoint not reached after ' + str(self.MAXSETTLETIME) + ' s!')


	########################################################################################################
	

	def setCurrent(self,value,wait_stable):
		"""
		PSU.setCurrent(value,wait_stable)
		
		Set PSU current.
		
		INPUT:
		value: current set-point value (float)
		wait_stable: wait until output current reaches the set-point value (bool)
		
		OUTPUT:
		(none)
		"""
		
		if self.COMMANDSET == 'KORAD':
			self._PSU.current(value)
		elif self.COMMANDSET == 'VOLTCRAFT':
			self._PSU.current(value)
		else:
			raise RuntimeError('Cannot set current on power supply with ' + self.COMMANDSET + ' command set.')

		# wait for stable output current:
		if wait_stable:
			stable = False
			t0 = time.time() # start time (now)
			while not time.time() - t0 > self.MAXSETTLETIME:
				v = self.read()[1]
				if abs( v - value) <= 1.3*self.IRES:
					stable = True
					break
				else:
					time.sleep(self.SETTLEPOLLTIME)
			if not stable:
				print (self.LABEL + ' warning: current setpoint not reached after ' + str(self.MAXSETTLETIME) + ' s!')
		


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

		V = []
		I = []
		L = []
		if self.COMMANDSET == 'KORAD':
			V,I,L = self._PSU.reading()
		elif self.COMMANDSET == 'VOLTCRAFT':
			t0 = time.time()
			while True:
				v,i,l = self._PSU.reading()
				V.append(v)
				I.append(i)
				L.append(l)
				# print(V)
				# print(I)
				if len(V) >= 5:
					if max(V)-min(V) <= self.VRES:
						if max(I)-min(I) <= self.IRES:
							break
					V = V[-5:]
					I = I[-5:]
					L = L[-5:]
				if time.time() - t0 > 5.0:
					print('Could not get stable readings after 5 seconds!')
			V = np.mean(V)
			I = np.mean(I)
			if "CC" in L:
				L = "CC"
			else:
				L = "CV"
		else:
			raise RuntimeError('Cannot read values from power supply with ' + self.COMMANDSET + ' command set.')

		return (V,I,L)
