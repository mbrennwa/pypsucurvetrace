"""
Python class for abstract power supply objects.
Classes of specific real-world power supplies will derive from this class.
"""

import time
import numpy as np
from numpy.polynomial.polynomial import polyval
import logging

import lib.powersupply_VOLTCRAFT as powersupply_VOLTCRAFT
import lib.powersupply_KORAD as powersupply_KORAD
import lib.powersupply_BK as powersupply_BK

# set up logger:
logger = logging.getLogger('powersupply')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

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
#    .VRESSET               resolution of voltage setting (V)
#    .IRESSET               resolution of current setting (A)
#    .VRESREAD              resolution of voltage readings (V)
#    .IRESREAD              resolution of current readings (A)
#    .VOFFSETMAX            max. offset of V read vs set
#    .MAXSETTLETIME         max. time allowed to attain stable output values (will complain if output not stable after this time) (s)
#    .READIDLETIME          idle time between readings for checking if output values of newly set voltage/current values are at set point, or when checking if consecutive measurement readings are consistent (s)
#    .V_SET_CALPOLY         tuple of polynomial coefficients ai, such that for a desired voltage output x the correct setpoint y is given by y(x) = a0 + a1*x + a2*x^2 + ...
#    .V_READ_CALPOLY        tuple of polynomial coefficients ai, such that for a given voltage reading the true input voltage y is given by y(x) = a0 + a1*x + a2*x^2 + ...
#    .I_SET_CALPOLY         same as I_SET_CALPOLY, but for I setting
#    .I_READ_CALPOLY        same as V_READ_CALPOLY, but for I reading
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

	def __init__(self, port=None, commandset=None, label=None, V_SET_CALPOLY=None, V_READ_CALPOLY=None, I_SET_CALPOLY=None, I_READ_CALPOLY=None):
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
		self.VRESREAD = 0.0
		self.IRESREAD = 0.0
		self.VOFFSETMAX = 0.0
		self.IOFFSETMAX = 0.0

		# CALPOLY fields:
		if V_SET_CALPOLY is None:
			self.V_SET_CALPOLY = (0, 1)
		else:
			self.V_SET_CALPOLY = V_SET_CALPOLY
		if V_READ_CALPOLY is None:
			self.V_READ_CALPOLY = (0, 1)
		else:
			self.V_READ_CALPOLY = V_READ_CALPOLY
		if I_SET_CALPOLY is None:
			self.I_SET_CALPOLY = (0, 1)
		else:
			self.I_SET_CALPOLY = I_SET_CALPOLY
		if I_READ_CALPOLY is None:
			self.I_READ_CALPOLY = (0, 1)
		else:
			self.I_READ_CALPOLY = I_READ_CALPOLY
			
		# TEST config:
		self.TEST_VSTART = 0.0
		self.TEST_VEND = 0.0
		self.TEST_ILIMIT = 0.0
		self.TEST_PLIMIT = 0.0
		self.TEST_VIDLE = 0.0
		self.TEST_IIDLE = 0.0
		self.TEST_N = 1
		self.TEST_POLARITY = 1
		self.LABEL = label
		self.CONNECTED = False
		self.CONFIGURED = False

		# check inputs:
		if not port:
			logger.error (label + ': cannot connect to power supply (no serial port specified).')
			
		elif not commandset:
			logger.error (label + ': cannot connect to power supply (no type / command set specified).')

		elif not label:
			logger.error (label + ': cannot set up power supply (no label specified).')

		# connect to the PSUs and set it/them up:
		else:
			self._PSU = []

			if type(commandset) is tuple:
				num_PSU = len(commandset)
			else:
				num_PSU = 1

			for k in range(num_PSU):
				if num_PSU == 1:
					C = commandset.upper()
					P = port
				else:
					C = commandset[k].upper()
					P = port[k]

				if C == 'VOLTCRAFT':
					PSU = powersupply_VOLTCRAFT.VOLTCRAFT(P,debug=False)

				elif C == 'KORAD':
					PSU = powersupply_KORAD.KORAD(P,debug=False)

				elif C in [ "BK" , "BK9184B_HIGH" , "BK9185B_HIGH" ]:
					PSU = powersupply_BK.BK(P,voltagemode='HIGH',debug=False)
					C = 'BK'

				elif C in [ "BK9184B_LOW" , "BK9185B_LOW" ]:
					PSU = powersupply_BK.BK(P,voltagemode='LOW',debug=False)
					C = 'BK'

				else:
					raise RuntimeError ('Unknown commandset ' + C + '! Cannot continue...')

				PSU.COMMANDSET = C

				self._PSU.append(PSU)

			self.VMIN = 0.0
			self.VMAX = 0.0
			self.PMAX = 0.0
			self.IMAX = self._PSU[0].IMAX
			self.VRESSET = self._PSU[0].VRESSET
			self.IRESSET = self._PSU[0].IRESSET
			self.VRESREAD = self._PSU[0].VRESREAD
			self.IRESREAD = self._PSU[0].IRESREAD
			self.MAXSETTLETIME = self._PSU[0].MAXSETTLETIME
			self.READIDLETIME = self._PSU[0].READIDLETIME
			if num_PSU == 1:
				self.MODEL = self._PSU[0].MODEL
			else:
				self.MODEL = 'COMPOSITE'

			for k in range(num_PSU):
				self.VMIN += self._PSU[k].VMIN
				self.VMAX += self._PSU[k].VMAX
				self.PMAX += self._PSU[k].PMAX
				self.VOFFSETMAX += self._PSU[k].VOFFSETMAX
				self.IOFFSETMAX += self._PSU[k].IOFFSETMAX
				if self.IMAX > self._PSU[k].IMAX:
					self.IMAX = self._PSU[k].IMAX;
				if self.VRESSET < self._PSU[k].VRESSET:
					self.VRESSET = self._PSU[k].VRESSET
				if self.IRESSET < self._PSU[k].IRESSET:
					self.IRESSET = self._PSU[k].IRESSET
				if self.VRESREAD < self._PSU[k].VRESREAD:
					self.VRESREAD = self._PSU[k].VRESREAD
				if self.IRESREAD < self._PSU[k].IRESREAD:
					self.IRESREAD = self._PSU[k].IRESREAD
				if self.MAXSETTLETIME < self._PSU[k].MAXSETTLETIME:
					self.MAXSETTLETIME = self._PSU[k].MAXSETTLETIME
				if self.READIDLETIME < self._PSU[k].READIDLETIME:
					self.READIDETIME = self._PSU[k].READIDLETIME

			if num_PSU > 1:
				self.PMAX = min (self.PMAX,self.VMAX*self.IMAX)

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

		# make sure we're not trying to set a value that is not resolved by the setting resolution of the PSU,
		# which will never give a stable output at the unresolved value		
		value = round(value/self.VRESSET) * self.VRESSET
		
		# determine voltage settings for all PSU units:
		V = []
		if len(self._PSU) > 1:
			for k in range(len(self._PSU)):
				delta = value - sum(V)
				if delta < self._PSU[k].VMIN:
					if k > 0:
						V.append(self._PSU[k].VMIN)
						V[k-1] = V[k-1] - (V[k]-delta)
					else:
						raise RuntimeError('Cannot set voltage -- value is lower than VMIN.')
				if delta > 0:
					V.append( min(delta,self._PSU[k].VMAX) )
				else:
					V.append(0.0)


		else:
			V.append(value)


		for k in range(len(self._PSU)):
			if self._PSU[k].COMMANDSET in [ 'KORAD' , 'VOLTCRAFT' , 'BK' ]:
				
				# determine corrected voltage setpoint:
				VV = polyval(V[k], self.V_SET_CALPOLY)
				
				# set voltage at the PSU:
				self._PSU[k].voltage(VV)
				
			else:
				raise RuntimeError('Cannot set voltage on power supply with ' + self.COMMANDSET + ' command set.')

		# wait for stable output voltage:
		if wait_stable:
			stable = False
			limit = 0 	# number of readings with current limiter ON
			limit_max = 2	# max. allowed number of current limit ON readings
			t0 = time.time() # start time (now)
			r = self.read()
			delta = abs(r[0] - value)
			while not time.time() > t0+self.MAXSETTLETIME:

				delta = abs(r[0] - value)
				if r[2] == "CC":
					limit = limit + 1
					if limit > limit_max:
						break
				if delta <= 1.3*self.VRESREAD + self.VOFFSETMAX:
					stable = True
					break
				time.sleep(self.READIDLETIME)
				r = self.read()

			if not stable:
				if r[2] == "CC":
					pass # voltage setpoint running into current limit mode. Skip waiting for stable output voltage...
				else:
					logger.warning (self.LABEL + ': voltage setpoint not reached after ' + str(self.MAXSETTLETIME) + ' s! Offset = ' + str(delta) + ' V')


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

		for k in range(len(self._PSU)):
			if self._PSU[k].COMMANDSET in [ 'KORAD' , 'VOLTCRAFT' , 'BK' ]:
			
							
				# determine corrected current setpoint:
				VV = polyval(value, self.I_SET_CALPOLY)
				
				# set current at the PSU:
				self._PSU[k].current(VV)
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
					pass # current setpoint running into voltage limit mode. Skip waiting for stable output current...
				else:
					logger.warning (self.LABEL + ': current setpoint not reached after ' + str(self.MAXSETTLETIME) + ' s! Offset = ' + str(delta) + ' A')


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

		for k in range(len(self._PSU)):
			if self._PSU[k].COMMANDSET in [ 'KORAD' , 'VOLTCRAFT' , 'BK' ]:
				self._PSU[k].output(False)
				self._PSU[k].voltage(self.VMIN)
				self._PSU[k].current(0.0)

			else:
				raise RuntimeError('Cannot turn off power supply with ' + self._PSU[k].COMMANDSET + ' command set.')



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

		for k in range(len(self._PSU)):
			if self._PSU[k].COMMANDSET in [ 'KORAD' , 'VOLTCRAFT' , 'BK' ]:
				self._PSU[k].output(True)

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

			v = []
			i = []
			l = []
			for k in range(len(self._PSU)):
				if self._PSU[k].COMMANDSET in [ 'KORAD' , 'VOLTCRAFT' , 'BK' ]:
					vv,ii,ll = self._PSU[k].reading()
					
					# add values to the list:					
					v.append(vv)
					i.append(ii)
					l.append(ll)
				else:
					raise RuntimeError('Cannot read values from power supply with ' + self._PSU[k].COMMANDSET + ' command set.')
					break

			v = sum(v)
			i = sum(i)/len(i)
			if 'CC' in l:
				l = 'CC'
			else:
				l = 'CV'

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
					logger.info(self.LABEL + ': Could not get ' + str(N) + ' consistent readings in a row after ' + str(self.MAXSETTLETIME) + ' s! DUT drifting? Noise?')
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
					
		# determine corrected reading values:
		V = polyval(V, self.V_READ_CALPOLY)
		I = polyval(I, self.I_READ_CALPOLY)

		return (V,I,L)
