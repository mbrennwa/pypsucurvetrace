# PYTHON IMPORTS:
import pyvisa
import time

# INIT PYVISA CONNECTION TO INSTRUMENT:
rm = pyvisa.ResourceManager()
# rm.list_resources()
inst = rm.open_resource('USB0::1510::8832::4315095::0::INSTR')

# SET COMMUNICATION TIMEOUT TO 10 SECONDS:
inst.timeout = 10000

# READ AND PRINT INSTRUMENT IDENTIFICATION:
print( 'Instrument IDN: ' + inst.query("*IDN?"))

# RESET INSTRUMENT SETTINGS TO DEFAULTS:
inst.write("*RST")

print( 'Self test result: ' + inst.query("*TST?"))



# SET VOLTAGE SLEW RATE TO 1000 V / SEC (RISING AND FALLING):
inst.write(":SOURCE:VOLTAGE:SLEW:RISING 123")
inst.write(":SOURCE:VOLTAGE:SLEW:FALLING 456")

# READ VOLTAGE SLEW RATE SETTINGS (JUST TO SEE IF SETTINGS WERE APPLIED CORRECTLY):
print( 'Voltage slew rate (rising, V/s): ' + inst.query(":SOURCE:VOLTAGE:SLEW:RISING?"))
print( 'Voltage slew rate (falling, V/s): ' + inst.query(":SOURCE:VOLTAGE:SLEW:FALLING?"))

# TURN ON OUTPUT AND SET VOLTAGE AND CURRENT:
inst.write(":OUTPUT:STATE ON")
inst.write(":VOLTAGE 15")
inst.write(":CURRENT 0.25")

# READ BACK VOLTAGE AND CURRENT SETTINGS:
print( 'Voltage setting (V): ' + inst.query(":VOLTAGE?"))
print( 'Current setting (A): ' + inst.query(":CURRENT?"))

# WAIT A MOMENT FOR STABILISATION OF THE OUTPUT VOLTAGE / CURRENT VALUES:
time.sleep(1)

# print(inst.query(":READ?"))	# read and print voltage and current measured at PSU
# print(inst.query(":MEASURE:VOLTAGE:DC?"))
# print(inst.query(":MEAS:VOLT?"))
# print(inst.query(":SENSE?"))

inst.close()

