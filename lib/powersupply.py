"""
Python class for abstract power supply objects.
Classes of specific real-world power supplies will derive from this class.
"""

import time
import numpy as np
import lib.powersupply_VOLTCRAFT as powersupply_VOLTCRAFT
import lib.powersupply_KORAD as powersupply_KORAD
import lib.powersupply_BK as powersupply_BK

# PSU object:
#    .setVoltage(voltage)   set voltage
#    .setCurrent(current)   set current
#    .turnOff()   	    turn PSU output off
#    .turnOn()   	    turn PSU output on
#    .read()                read current voltage, current, and limiter mode (voltage or current limiter active)
#    #### .settletime()             estimated settle time to attain stable voltage + current at PSU output after changing the setpoint (s)
#    .VMAX                  max. supported voltage (V, including VOFFSET)
#    .VMIN                  min. supported voltage (V, including VOFFSET)
#    .VOFFSET               external offset voltage (if fixed external voltage source is connected in series with the PSU)
#    .IMAX                  max. supported current (V)
#    .PMAX                  max. supported power (W)
#    .VRESSET               resolution of voltage setting (V)
#    .IRESSET               resolution of current setting (A)
#    .VRESREAD              resolution of voltage readings (V)
#    .IRESREAD              resolution of current readings (A)
#    .MAXSETTLETIME         max. time allowed to attain stable output values (will complain if output not stable after this time) (s)
#    .READIDLETIME          idle time between readings for checking if output values of newly set voltage/current values are at set point, or when checking if consecutive measurement readings are consistent (s)
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
		self.VOFFSET = 0.0
		self.IMAX = 0.0
		self.PMAX = 0.0
		self.VRESREAD = 0.0
		self.IRESREAD = 0.0
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

			elif self.COMMANDSET == 'KORAD':
				self._PSU = powersupply_KORAD.KORAD(port,debug=False)

			elif self.COMMANDSET in [ "BK" , "BK9184B_HIGH" , "BK9185B_HIGH" ]:
				self._PSU = powersupply_BK.BK(port,voltagemode='HIGH',debug=False)
				self.COMMANDSET = 'BK'

			elif self.COMMANDSET in [ "BK9184B_LOW" , "BK9185B_LOW" ]:
				self._PSU = powersupply_BK.BK(port,voltagemode='LOW',debug=False)
				self.COMMANDSET = 'BK'

			else:
				raise RuntimeError ('Unknown commandset ' + commandset + '! Cannot continue...')

			self.VMIN = self._PSU.VMIN
			self.VMAX = self._PSU.VMAX
			self.IMAX = self._PSU.IMAX
			self.PMAX = self._PSU.PMAX
			self.VRESSET = self._PSU.VRESSET
			self.IRESSET = self._PSU.IRESSET
			self.VRESREAD = self._PSU.VRESREAD
			self.IRESREAD = self._PSU.IRESREAD
			self.MAXSETTLETIME = self._PSU.MAXSETTLETIME
			self.READIDLETIME = self._PSU.READIDLETIME
			self.MODEL = self._PSU.MODEL
			self.CONNECTED = True
		


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

		# subtract external offset voltage (if any)
		value = value - self.VOFFSET

		# make sure we're not trying to set a value that is not resolved by the setting resolution of the PSU,
		# which will never give a stable output at the unresolved value		
		value = round(value/self.VRESSET) * self.VRESSET
		
		if self.COMMANDSET in [ 'KORAD' , 'VOLTCRAFT' , 'BK' ]:
			self._PSU.voltage(value)
		else:
			raise RuntimeError('Cannot set voltage on power supply with ' + self.COMMANDSET + ' command set.')

		# wait for stable output voltage:
		if wait_stable:
			stable = False
			limit = 0 	# number of readings with current limiter ON
			limit_max = 2	# max. allowed number of current limit ON readings
			t0 = time.time() # start time (now)

			while not time.time() > t0+self.MAXSETTLETIME:
				r = self.read()
				if r[2] == "CC":
					limit = limit + 1
					if limit > limit_max:
						break
				if abs(r[0] - value) <= 1.3*self.VRESREAD:
					stable = True
					break
				time.sleep(self.READIDLETIME)

			if not stable:
				if r[2] == "CC":
					pass
					### print(self.LABEL + ': voltage setpoint running into current limit mode. Skip waiting for stable output voltage...')
				else:
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
		
		# make sure we're not trying to set a value that is not resolved by the setting resolution of the PSU,
		# which will never give a stable output at the unresolved value		
		value = round(value/self.VRESSET) * self.VRESSET

		if self.COMMANDSET in [ 'KORAD' , 'VOLTCRAFT' , 'BK' ]:
			self._PSU.current(value)
		else:
			raise RuntimeError('Cannot set current on power supply with ' + self.COMMANDSET + ' command set.')

		# wait for stable output current:
		if wait_stable:
			stable = False
			limit = 0 	# number of readings with voltage limiter ON
			limit_max = 2	# max. allowed number of voltage limit ON readings
			t0 = time.time() # start time (now)
			while not time.time() - t0 > self.MAXSETTLETIME:
				r = self.read()
				if r[2] == "CV":
					limit = limit + 1
					if limit > limit_max:
						break
				if abs( r[1] - value) <= 1.3*self.IRESREAD:
					stable = True
					break
				else:
					time.sleep(self.READIDLETIME)
			if not stable:
				if r[2] == "CV":
					print(self.LABEL + ': current setpoint running into voltage limit mode. Skip waiting for stable output current...')
				else:
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

		if self.COMMANDSET in [ 'KORAD' , 'VOLTCRAFT' , 'BK' ]:
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

		if self.COMMANDSET in [ 'KORAD' , 'VOLTCRAFT' , 'BK' ]:
			self._PSU.output(True)

		else:
			raise RuntimeError('Cannot turn on power supply with ' + self.COMMANDSET + ' command set.')


	########################################################################################################
	

	def read(self,N=1):
		"""
		PSU.read(N=1)
		
		Read current output: voltage, current, limiting mode (CV or CC) 
		Optional (if N > 1): keep on reading voltage and current until N consecutive readings are stable to within the voltage and current resolution of the PSU, and return the mean of thos N last readings.

		INPUT:
		N (optional): number of consecutive readings that are stable to within the voltage and current resolution of the PSU (default: N = 1)

		OUTPUT:
		V: voltage in Volts (float)
		I: current in Amps (float)
		L: limiter mode, 'CV' = voltage limit, 'CC' = current limit (string)
		"""

		V = []
		I = []
		L = []

		limit = 0	# number of readings with current limiter ON
		limit_max = 2	# max. allowed number of current limit ON readings

		if N < 1:
			raise RuntimeError ('Number of consistent readings in a row must be larger than 1!')
		
		t0 = time.time()
		while True:

			if self.COMMANDSET in [ 'KORAD' , 'VOLTCRAFT' , 'BK' ]:
				v,i,l = self._PSU.reading()

			else:
				raise RuntimeError('Cannot read values from power supply with ' + self.COMMANDSET + ' command set.')
				break

			if N == 1:
				# just single readings, no need to match repeated readings to within the resolution of the PSU
				V = v;
				I = i;
				L = l;
				break

			else:
				V.append(v)
				I.append(i)
				if l == "CC":
					L.append(1.0)
					### print(self.LABEL + ': running in current limit mode. Skip reading ' + str(N) + ' consistent readings in a row...')
					limit = limit + 1
					if limit > limit_max: # ran into the current limit for the third time
						break
				else:
					L.append(0.0)
				if len(V) >= N:

					# we have enough readings, so let's check if they are consistent:
                                        if max(V)-min(V) <= 2*self.VRESREAD:
                                                if max(I)-min(I) <= 2*self.IRESREAD:
                                                        break

					# the readings are not yet consistent, so let's only keep the last N-1 readings and try again:
                                        V = V[-(N-1):]
                                        I = I[-(N-1):]
                                        L = L[-(N-1):]
                                        
                                        # wait a little while before taking the next reading
                                        time.sleep(self.READIDLETIME)

				if time.time() - t0 > self.MAXSETTLETIME:
					# getting consistent readings is taking too long; give up
					print(self.LABEL + ': Could not get ' + str(N) + ' consistent readings in a row after ' + str(self.MAXSETTLETIME) + ' s! DUT drifting? Noise?')
					break
		
		if N > 1:
			V = np.mean(V)
			I = np.mean(I)
			if limit > limit_max:
				L = "CC"
			else:
				if np.mean(L) > 0.25:
					L = "CC"
				else:
					L = "CV"
					
		# add external offset voltage (if any)
		V = V + self.VOFFSET

		return (V,I,L)
