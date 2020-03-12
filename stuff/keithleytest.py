import pyvisa
import time

rm = pyvisa.ResourceManager()
# rm.list_resources()
inst = rm.open_resource('USB0::1510::8832::4315095::0::INSTR')
print(inst.query("*IDN?"))	# read and print instrument identification
inst.write("*RST")		# reset instrument 

inst.write(":SOURCE:VOLTAGE:SLEW:RISING 1000")	# SET VOLTAGE SLEW RATE TO 1000 V / SEC (RISING)
inst.write(":SOURCE:VOLTAGE:SLEW:FALLING 1000")	# SET VOLTAGE SLEW RATE TO 1000 V / SEC (FALLING)

inst.write(":OUTPUT:STATE ON")	# turn on output
inst.write(":VOLTAGE 15")	# set voltage source to 15 V
inst.write(":CURRENT 0.25")	# set current source to 0.25 A

time.sleep(1)			# wait a moment

print(inst.query(":READ[1]?"))	# read and print voltage and current from PSU

inst.close()

