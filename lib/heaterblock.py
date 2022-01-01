"""
Python class for heaterblock object.
"""

### import time
### import numpy as np
### import matplotlib.pyplot as plt
### from simple_pid import PID


import traceback
import logging
import time
import numpy as np

from simple_pid import PID
from threading import Thread
from lib.temperaturesensor_MAXIM import temperaturesensor_MAXIM as TSENS
from lib.powersupply import PSU


# heater class (dummy):
class heater:


	def __init__(self, config, target_temperature=0.0, init_on = False):
		
		# set / init all fields before trying to read from config file (which may not have all fields):
		self._PSU   = None
		self._TSENS = None
		self._power_is_on = False
		self._target_T = target_temperature

		# thread to read T sensor and for PID control:
		self._controller = None


		# try to connect / configure PSU and TSENSOR, and start controller thread:
		try:

			# read from config file and set up heater accordingly:
			self._T_buffer         = tuple(None for i in range(int(config['HEATERBLOCK']['TBUFFER_NUM'])))
			self._T_buffer_seconds = float(config['HEATERBLOCK']['TBUFFER_INTERVAL'])
			self._T_buffer_last    = time.time() - self._T_buffer_seconds
			if config['HEATERBLOCK']['TEMPSENS_TYPE'].upper() != 'DS1820':
				raise ValueError('Unknown T sensor type ' + config['HEATERBLOCK']['TEMPSENS_TYPE'] + '.')
			
			# connect / configure T sensor:
			self._TSENS = TSENS(config['HEATERBLOCK']['TEMPSENS_COMPORT'] , romcode = '')
			self._TSENS_configured = True

			# connect / configure PSU:
			self._PSU = PSU(config['HEATERBLOCK']['PSU_COMPORT'],config['HEATERBLOCK']['PSU_TYPE'],'HEATERBLOCK_PSU')
			self.turn_off()
			self._PSU.setVoltage(0.0,wait_stable=False)
			self._PSU.setCurrent(0.0,wait_stable=False)
			
			self._heater_R         = float(config['HEATERBLOCK']['HEATER_RESISTANCE'])
			
			# max. heater power:
			try:
				P_max = float(config['HEATERBLOCK']['MAX_POWER'])
			except:
				P_max = self._PSU.PMAX;
				pass
			self.max_power = min((P_max, self._PSU.PMAX))
			
			# PID coefficients:
			self._PID_Kp = float(config['HEATERBLOCK']['KP'])
			self._PID_Ki = float(config['HEATERBLOCK']['KI'])
			self._PID_Kd = float(config['HEATERBLOCK']['KD'])
			
			# heater controller thread:
			self._controller = heater_control_thread(self)
			self._controller.start()

			# turn heater on (if required):
			if init_on:
				self.turn_on()

		except KeyError as e:
			logging.warning('Could not configure heaterblock because ' + str(e) + ' is missing in the configuration file.')
			pass

		except Exception as e:
			logging.warning('Could not configure heaterblock: ' + traceback.format_exc())
			pass
					
	
	def set_power(self, power):
		# set heater power:
		if self._PSU != None:
			if self._power_is_on:
				try:
					power = max((0, power))               # make sure power is not negative (the PID may want that, but we can't)
					power = min((power, self.max_power))  # make sure power is not more than max. allowed values (the PID may want that, but we can't)
					voltage = np.sqrt(power*self._heater_R)
					voltage = min( voltage, self._PSU.VMAX )
					self._PSU.setVoltage(voltage,wait_stable=False)
				except Exception as e:
					logging.warning('Could not set heater power: ' + traceback.format_exc())
	
		
	def get_temperature(self, do_read = True):
		# get T sensor reading:
		if self._TSENS is None:
			temp = None
		else:
			if self._T_buffer[-1] is None:
				do_read = True
			if do_read:
				temp,unit = self._TSENS.temperature()
				if unit != 'deg.C':
					raise ValueError('T value has wrong unit (' + unit + ').')
				
				# add to T buffer:
				now = time.time()
				if self._T_buffer_last + self._T_buffer_seconds < now:
					self._T_buffer = self._T_buffer[1:] + (temp,)
					self._T_buffer_last = now

			temp = self._T_buffer[-1] # return last entry in T_buffer

		return temp
		

	def get_temperature_string(self, do_read = True):
		try:
			T_HB = float(self.get_temperature(do_read)) # this will fail if T_HB cannot be converted to a proper number
			T_HB = "{:.2f}".format(T_HB) # convert and format numeric value to string
		except:
			T_HB = "NA"
		return T_HB
		
	
	def temperature_is_stable(self):
		is_stable = True
		T_tgt, T_tol = self.get_target_temperature()
		
		if T_tgt != None:
			if any(map(lambda x: x is None, self._T_buffer)):
				# buffer still contains some None values, so we need more readings
				is_stable = False
			
			elif min(self._T_buffer) < T_tgt - T_tol:
				is_stable = False
				
			elif max(self._T_buffer) > T_tgt + T_tol:
				is_stable = False
		
		return is_stable


	def set_target_temperature(self, T_value, T_tolerance):
		# set target temperature:
		self._target_T_val = T_value
		self._target_T_tol = T_tolerance


	def get_target_temperature(self):
		# get target temperature:
		return self._target_T_val, self._target_T_tol
		

	def get_target_temperature_string(self, do_read = True):
		try:
			T_tgt, T_tol = self.get_target_temperature()
			T_tgt = float(T_tgt) # this will fail if T_tgt cannot be converted to a proper number
			T_tol = float(T_tol) # this will fail if T_tol cannot be converted to a proper number
			T = "{:.2f}".format(T_tgt) + " " + u"\u00B1" + " " + "{:.2f}".format(T_tol) # convert and format numeric value to string
		except:
			T = "NA"
		return T


	def turn_on(self):
		# turn on PSU / heater power:
		if self._PSU != None:
			try:
				self._PSU.turnOn()
				self._PSU.setVoltage(0.0,wait_stable=False) # set V = 0 to avoid uncontrolled power / current draw
				self._PSU.setCurrent(self._PSU.IMAX,wait_stable=False) # set current to max. to allow power control based on voltage limit only
				self._power_is_on = True
			except Exception as e:
				logging.warning('Could not turn on the heater: ' + traceback.format_exc())


	def turn_off(self):
		# turn off PSU / heater power:
		if self._PSU != None:
			try:
				self._PSU.turnOff()
				self._power_is_on = False
			except Exception as e:
				logging.warning('Could not turn off the heater: ' + traceback.format_exc())


	def is_on(self):
		return self._power_is_on


	def wait_for_stable_T(self, DUT_PSU_allowed_turn_off=None, terminal_output=False):
		
		if not self.is_on():
			delay = 0.0
			
		else:
			t0 = time.time()
												
			# wait for heaterblock to attain required temperature:
			is_first_line = True
			PSU_turned_off = False
			
			while not self.temperature_is_stable():
			
				# go to new line on terminal output:
				if terminal_output:
					if is_first_line:
						print('')
						is_first_line = False

				# if necessary and allowed: turn DUT PSU off (to speed up / allow cooling of heaterblock without heat input from DUT)
				T_tgt, T_tol = self.get_target_temperature()
				T_now        = self.get_temperature(do_read=True)
				
				if T_now > T_tgt + T_tol:
					if DUT_PSU_allowed_turn_off is not None:
						if DUT_PSU_allowed_turn_off.CONFIGURED:
							DUT_PSU_allowed_turn_off.turnOff()
							PSU_turned_off = True

				msg = 'Waiting for heaterblock temperature (current: ' + self.get_temperature_string() +' °C, target: ' + self.get_target_temperature_string() + ' °C)...'
				print (msg, end="\r")
				# time.sleep(0.5)
				# T_now = HEATER.get_temperature()
			
			if not is_first_line:
				print (' '*len(msg), end="\r") # clear previous line from terminal
				
			# turn DUT PSU on again (if necessary):
			if PSU_turned_off:
				DUT_PSU_allowed_turn_off.turnOn()
			
			delay = time.time() - t0
		
		return delay
		

	def terminate_controller_thread(self):
		# turn off PSU / heater power:
		self._controller.terminate()



# thread to read T sensor set heater power in the background (PID controller):
class heater_control_thread(Thread):


	def __init__(self, heaterblock):
	### def __init__(self, heaterblock, interval_seconds=1):
		Thread.__init__(self)
		
		self._heaterblock = heaterblock
		### self._interval = interval_seconds
		
		# Init and configure PID controller:
		self._pid = None
		self._is_running = False
		self._do_run = False
		try:
			self._pid = PID(Kp=self._heaterblock._PID_Kp, Ki=self._heaterblock._PID_Ki, Kd=self._heaterblock._PID_Kd)
			self._pid.output_limits = (0, self._heaterblock.max_power)
			self._do_run = True
		except :
			# may fail if heaterblock is not really set up
			logging.warning('Could not initialize heaterblock: ' + traceback.format_exc())
			pass
	
		
	def run(self):
	
		try:
			self._is_running = True

			while self._do_run:
			
				# sleep between PID iterations:
				### last_time = time.time()
				### while time.time() < last_time + self._interval:
				### 	time.sleep(self._interval/10)
				
				# get heaterblock temperature:
				T = self._heaterblock.get_temperature(do_read=True)

				# determine and set heating power:
				if self._heaterblock.is_on():
					if T != None:
						
						T_target, T_tol = self._heaterblock.get_target_temperature()
						
						if T_target is None:
							self._heaterblock.turn_off()
						else:
							self._pid.setpoint = T_target  # update target value for PID
							power = self._pid(T)                             # determine heater power
							self._heaterblock.set_power(power)               # set heater power
							
		except:
			logging.warning('Heaterblock PID controller failed: ' + traceback.format_exc())
			
		finally:
			# try to turn off the power supply
			try:
				self._heaterblock.turn_off()
			except:
				logging.warning('Could not turn off heaterblock: ' + traceback.format_exc())
				pass
				
			# let others know that thread is not running anymore
			self._is_running = False		
	
	
	def terminate(self):
		self._do_run = False
		while self._is_running:
			time.sleep(0.01)
