"""
Python class for abstract power supply objects. for interfacing specific real-world power supplies
"""

import powersupply_PPS 

def _pps_debug(s):
	sys.stdout.write(s)
	sys.stdout.flush()

# PSU object:
#    .setVoltage(voltage)   set voltage
#    .setCurrent(current)   set current
#    .read()                read current voltage, current, and limiter mode (voltage or current limiter active)
#    .VMAX                  max. supported voltage (V)
#    .VMIN                  min. supported voltage (V)
#    .IMAX                  max. supported current (V)
#    .PMAX                  max. supported power (W)
#    .COMMANDSET            commandset type string (indicating Voltcraft/Mason, Korad/RND, SCPI, etc.)
#    .MODEL                 PSU model string

class PSU:
	"""
	Abstract power supply (PSU) class
	"""

	def __init__(self, port, commandset, label):
		'''
		PSU(port, type, label)
		port : serial port (string, example: port = '/dev/serial/by-id/XYZ_123_abc')
		commandset : specifies computer interface / command set (string).
			Voltcraft PPS / Mason: commandset = 'Voltcraft'
			Korad / RND: commandset = 'Korad'
			SCPI interface: commandset = 'SCPI'
		label: label or name to be used to describe / identify the PSU unit (string)
		'''

		commandset = commandset.upper()
		if commandset == 'VOLTCRAFT':
			print ('Connect to Voltcraft / Mason PPS')
		elif commandset == 'KORAD':
			print ('Connect to Korad / RND')
		elif commandset == 'SCPI':
			print ('Connect to SCPI')
		else:
			print ('Unknown commandset ' + commandset + '! Cannot continue...')


	########################################################################################################
	

	def setVoltage(self):
		"""
		PSU.setVoltage(value)
		
		Set PSU voltage.
		
		INPUT:
		value: voltage value (float)
		
		OUTPUT:
		(none)
		"""
		
		print ('Set voltage to ' + str(value) ' V...')

