import time
import numpy as np
import matplotlib.pyplot as plt
from simple_pid import PID


import traceback
import logging
from lib.temperaturesensor_MAXIM import temperaturesensor_MAXIM as TSENS
from lib.powersupply import PSU


# heater class (dummy):
class heaterblock:

	def __init__(self, PSU_port, PSU_type, TSENS_port, resistance):
	
		# connect / configure PSU:
		try:
			logging.info('Trying to configure PSU...')
			
			self._PSU = PSU(port=PSU_port, commandset=PSU_type, label='Heaterblock_PSU')
			
			self.max_power = self._PSU.PMAX 

			logging.info('PSU max voltage = ' + str(self._PSU.VMAX))
			logging.info('PSU max current = ' + str(self._PSU.IMAX))
			logging.info('PSU max power   = ' + str(self._PSU.PMAX))
			
			# set initial voltage = 0, and initial current = max.
			self._PSU.setVoltage(0.0,wait_stable=False)
			self._PSU.setCurrent(self._PSU.IMAX,wait_stable=False)
			logging.info('Heater turning on...')
			self.turn_on()
			
			logging.info('...done.')
		
		except Exception as e:
			logging.error(traceback.format_exc())
			exit()
		
		# connect / configure T sensor:
		try:
			logging.info('Trying to configure T sensor...')
			self._TSENS = TSENS(TSENS_port , romcode = '')
			logging.info('...done.')

		except Exception as e:
			logging.error(traceback.format_exc())
			exit()
		
		# set heater resistance:
		self._heater_R = resistance
		

	def read_temp(self):
		# read T sensor and return result

		temp,unit = self._TSENS.temperature()
		if unit != 'deg.C':
			raise ValueError('T value has wrong unit (' + unit + ').')
		return temp
        

	def update(self, power, dt):
	
		# set heater power:
		if power < 0:
			# PID wants active cooling, but can't...
			power = 0.0
		voltage = np.sqrt(power*self._heater_R)
		voltage = min( voltage, self._PSU.VMAX )
		logging.info('Set PSU voltage to ' + str(voltage) + ' V')
		self._PSU.setVoltage(voltage,wait_stable=False)
		
		# read T sensor (for next PID iteration):
		T = self.read_temp()
		return T


	def turn_on(self):
	
		# turn on PSU / heater power:
		self._PSU.turnOn()

	def turn_off(self):
	
		# turn off PSU / heater power:
		self._PSU.turnOff()



### MAIN // PID CONTROLLER

logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s: %(message)s')

logging.debug ('**** SHOULD READ CONFIG FILE HERE... ****')




T_target = 35		# Target temperature of the heater (°C)




# init heaterblock object:
heater = heaterblock( PSU_port = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0010-if00-port0',
                      PSU_type = 'VOLTCRAFT',
                      TSENS_port =  '/dev/serial/by-id/usb-FTDI_TTL232R-3V3_FTBZLSUL-if00-port0',	
                      resistance = 9
                    )

# Init and configure PID controller:
# Determine the PID paramters: https://en.wikipedia.org/wiki/PID_controller#Manual_tuning
### pid = PID(Kp=300, Ki=10.0, Kd=100.0)
pid = PID(Kp=300, Ki=5.0, Kd=0.0)


pid.output_limits = (0, heater.max_power)
pid.setpoint = T_target

# time parameters
start_time = time.time()
last_time  = start_time

# data for plotting:
setpoint, y, x = [], [], []

T = heater.read_temp()

# PID controller loop:
try:
	while time.time() - start_time < 1000: 
	       	
		#Setting the time variable dt
		current_time = time.time()
		dt = (current_time - last_time)

		# determine heating power for next step:
		power = pid(T)
		
		logging.info('PID setpoint T = ' + str(pid.setpoint))
		logging.info('Heaterblock  T = ' + str(T))
		logging.info('PSU power    P = ' + str(power))
		
		# update heater block (set power, get temperature):
		T = heater.update(power, dt)
		
		#Visualize Output Results
		x += [current_time - start_time]
		y += [T]
		setpoint += [pid.setpoint]
		
		#Used for initial value assignment of variable temp
		#if current_time - start_time > 0:
		#    pid.setpoint = 100

		last_time = current_time


	# Visualization of Output Results
	### plt.plot(x, setpoint, label='target')
	### plt.plot(x, y, label='PID')
	### plt.xlabel('time')
	### plt.ylabel('temperature')
	### plt.legend()
	### plt.show()

except:
	logging.warning('PID control loop exited early!')

finally:
	heater.turn_off()
	logging.info('Heater turned off.')
