import time
import matplotlib.pyplot as plt
from simple_pid import PID

# heater class (dummy):
class heater:

	def __init__(self, T_ini, T_ambient, C_heat):
		self.temp   = T_ini  # initial temperature (°C)
		self.temp_amb = T_ambient  # ambient air temperature (°C)
		self.C_heat = C_heat # heat capacity of the heater (J/K)

	def read_temp(self):
		# read T sensor and return result
		time.sleep(0.1)
		return self.temp
        
	def update(self, power, dt):
	
		## dt = 10 * dt # speed up time (for dummy purposes)

		# read T sensor:
		T = self.read_temp()

		# heat loss due to cooling:
		T -= 0.5 * (T-self.temp_amb) * dt / self.C_heat

		# heat input:
		if power > 0:
			T += power * dt / self.C_heat

		# set new T value (dummy):
		self.temp = T

		return T



### MAIN

T0       = 25		# Initial temperature of the heater (°C)
T_target = 30		# Target temperature of the heater (°C)
P_max    = 36*12	# Max heating power (Watt)

# init heater object:
heater = heater(T_ini=T0, T_ambient=10, C_heat=1460)

# init PID controller:
## pid = PID(Kp=1, Ki=0.01, Kd=0.1)

# Determine the PID paramters: https://en.wikipedia.org/wiki/PID_controller#Manual_tuning
pid = PID(Kp=20000, Ki=0.35, Kd=0.0)


pid.output_limits = (0, P_max)
pid.setpoint = T_target

# time parameters
start_time = time.time()
last_time  = start_time

# data for plotting:
setpoint, y, x = [], [], []

T = T0

while time.time() - start_time < 30: 
       	
	#Setting the time variable dt
	current_time = time.time()
	dt = (current_time - last_time)

	# determine heating power for next step:
	power = pid(T)
        
	print(power)
	print(T-pid.setpoint)
	print("\n")
        
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
plt.plot(x, setpoint, label='target')
plt.plot(x, y, label='PID')
plt.xlabel('time')
plt.ylabel('temperature')
plt.legend()
plt.show()
