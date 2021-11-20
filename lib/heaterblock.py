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
		
		# try to connect / configure PSU and TSENSOR, and start controller thread:
		try:

			self._PSU   = None
			self._TSENS = None
			self._last_T_reading = None

			self._target_T = target_temperature

			if config['HEATERBLOCK']['TEMPSENS_TYPE'].upper() != 'DS1820':
				raise ValueError('Unknown T sensor type ' + config['HEATERBLOCK']['TEMPSENS_TYPE'] + '.')
			
			# connect / configure T sensor:
			# logging.info('Trying to configure heaterblock T sensor...')
			self._TSENS = TSENS(config['HEATERBLOCK']['TEMPSENS_COMPORT'] , romcode = '')
			self._TSENS_configured = True
			# logging.info('...done.')

			# connect / configure PSU:
			# logging.info('Trying to configure heaterblock PSU...')
			self._PSU = PSU(config['HEATERBLOCK']['PSU_COMPORT'],config['HEATERBLOCK']['PSU_TYPE'],'HEATERBLOCK_PSU')
			self.turn_off()
			self._PSU.setVoltage(0.0,wait_stable=False)
			self._PSU.setCurrent(0.0,wait_stable=False)

			self._heater_R = float(config['HEATERBLOCK']['HEATER_RESISTANCE'])

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

			# thread to read T sensor and for PID control:
			self._controller = heater_control_thread( self, float(config['HEATERBLOCK']['CONTROLLER_SECONDS']))
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
					if voltage > 0.0:
						current = power/voltage
					else:
						current = 0.0
					current = min( current, self._PSU.IMAX )
					self._PSU.setVoltage(voltage,wait_stable=False)
					self._PSU.setCurrent(current,wait_stable=False)
				except Exception as e:
					logging.warning('Could not set heater power: ' + traceback.format_exc())
	
		
	def get_temperature(self, do_read = True):
		# get T sensor reading:
		if self._TSENS is None:
			temp = None
		else:
			if self._last_T_reading is None:
				do_read = True
			if do_read:
				temp,unit = self._TSENS.temperature()
				if unit != 'deg.C':
					raise ValueError('T value has wrong unit (' + unit + ').')
				self._last_T_reading = temp
				self._last_time = time.time()
			else:
				temp = self._last_T_reading
		return temp
		

	def get_temperature_string(self, do_read = True):
		try:
			T_HB = float(self.get_temperature()) # this will fail if T_HB cannot be converted to a proper number
			T_HB = "{:.2f}".format(T_HB) # convert and format numeric value to string
		except:
			T_HB = "NA"
		return T_HB


	def set_target_temperature(self, T_value):
		# set target temperature:
		self._target_T = T_value


	def get_target_temperature(self):
		# get target temperature:
		return self._target_T
		

	def get_target_temperature_string(self, do_read = True):
		try:
			T = float(self.get_target_temperature()) # this will fail if T_HB cannot be converted to a proper number
			T = "{:.2f}".format(T) # convert and format numeric value to string
		except:
			T = "NA"
		return T


	def turn_on(self):
		# turn on PSU / heater power:
		if self._PSU != None:
			try:
				self._PSU.turnOn()
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


	def terminate_controller_thread(self):
		# turn off PSU / heater power:
		self._controller.terminate()



# thread to read T sensor set heater power in the background (PID controller):
class heater_control_thread(Thread):


	def __init__(self, heaterblock, interval_seconds=1):
		Thread.__init__(self)
		
		self._heaterblock = heaterblock
		self._interval = interval_seconds
		
		# Init and configure PID controller:
		self._pid = PID(Kp=self._heaterblock._PID_Kp, Ki=self._heaterblock._PID_Ki, Kd=self._heaterblock._PID_Kd)
		self._pid.output_limits = (0, self._heaterblock.max_power)

		self._do_run = True
		self._is_running = False
	
		
	def run(self):
		try:
			self._is_running = True

			while self._do_run:
			
				# sleep between PID iterations:
				last_time = time.time()
				while time.time() < last_time + self._interval:
					time.sleep(self._interval/10)
				
				# get heaterblock temperature:
				T = self._heaterblock.get_temperature(do_read=True)

				# determine and set heating power:
				if self._heaterblock.is_on():
					if T != None:
						
						T_target = self._heaterblock.get_target_temperature()
						if T_target is None:
							logging.warning('Heaterblock target temperature is not set. Turning heaterblock off...')
							self._heaterblock.turn_off()
						else:
							self._pid.setpoint = T_target  # update target value for PID
							power = self._pid(T)                             # determine heater power
							self._heaterblock.set_power(power)               # set heater power
		except Exception as e:
			logging.debug('Heaterblock PID controller failed: ' + traceback.format_exc())
		finally:
			# try to turn off the power supply
			try:
				self._heaterblock.turn_off()
			except:
				pass
				
			# let others know that thread is not running anymore
			self._is_running = False		
	
	
	def terminate(self):
		self._do_run = False
		while self._is_running:
			time.sleep(0.01)
