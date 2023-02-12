# Code for the MAXIM DS1820 type temperature sensors.
# This is just a wrapper class for the pydigitemp package; you may need to install pydigitemp first. Your can run the following command to install pydigitemp: pip install https://github.com/neenar/pydigitemp/archive/master.zip
# 
# DISCLAIMER:
# This file is part of PyPSUcurvetrace, a toolbox for I/V curve tracing of electronic parts using programmable power supplies.
# 
# PyPSUcurvetrace is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PyPSUcurvetrace is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PyPSUcurvetrace.  If not, see <http://www.gnu.org/licenses/>.
# 
# Copyright 2021, Matthias Brennwald (mbrennwa@gmail.com)

try:
	import sys
	import time
	import logging
	from digitemp.master import UART_Adapter
	from digitemp.device import AddressableDevice
	from digitemp.device import DS18B20
except ImportError as e:
	print (e)
	raise
	
# set up logger:
logger = logging.getLogger('temperaturesensor_MAXIM')
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


# check Python version and print warning if we're running version < 3:
if ( sys.version_info[0] < 3 ):
	warnings.warn("temperaturesensor_MAXIM class is running on Python version < 3. Version 3.0 or newer is recommended!")


class temperaturesensor_MAXIM:
	"""
	class for MAXIM DS1820 type temperature sensors (wrapper class for pydigitemp package).
	"""


	########################################################################################################
	
	
	def __init__( self , serialport , romcode = ''):
		'''
		temperaturesensor_MAXIM.__init__( serialport , romcode)
		
		Initialize TEMPERATURESENSOR object (MAXIM), configure serial port / 1-wire bus for connection to DS18B20 temperature sensor chip
		
		INPUT:
		serialport: device name of the serial port for 1-wire connection to the temperature sensor, e.g. serialport = '/dev/ttyUSB3'
		romcode: ROM code of the temperature sensor chip (you can find the ROM code using the digitemp program or using the pydigitemp package). If there is only a single temperature sensor connected to the 1-wire bus on the given serial port, romcode can be left empty.
		
		OUTPUT:
		(none)
		'''
		
		try:

			# configure 1-wire bus for communication with MAXIM temperature sensor chip
			r = AddressableDevice(UART_Adapter(serialport)).get_connected_ROMs()

			if r is None:
				logger.error ( 'Couldn not find any 1-wire devices on ' + serialport )
			else:
				bus = UART_Adapter(serialport)
				if romcode == '':
					if len(r) == 1:
						self._sensor = DS18B20(bus)
						self._ROMcode = r[0]
					else:
						logger.error ( 'Too many 1-wire devices to choose from! Try again with specific ROM code...' )
						for i in range(1,len(r)):
							logger.info ( 'Device ' + i + ' ROM code: ' + r[i-1] +'\n' )
				else:
					self._sensor = DS18B20(bus, rom=romcode)
					self._ROMcode = romcode
				
				self._UART_locked = False

			if not hasattr(self,'_sensor'):
				self.warning( 'Could not initialize MAXIM DS1820 temperature sensor.' )


		except:
			self.error ('An error occured during configuration of the temperature sensor at serial interface ' + serialport + '. The temperature sensor cannot be used.')


	########################################################################################################


	def get_UART_lock(self):
		'''
		temperaturesensor_MAXIM.get_UART_lock()
		
		Lock UART port for exclusive access (important if different threads / processes are trying to use the port). Make sure to release the lock after using the port (see temperaturesensor_MAXIM.release_UART_lock()!
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		# wait until the serial port is unlocked:
		while self._UART_locked == True:
			time.sleep(0.01)
			
		# lock the port:
		self._UART_locked = True


	########################################################################################################


	def release_UART_lock(self):
		'''
		temperaturesensor_MAXIM.release_UART_lock()
		
		Release lock on UART port.
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		# release the lock:
		self._UART_locked = False
		
		# sleep to allow access to T sensor from others
		time.sleep(0.013)


	
	########################################################################################################
		

	def temperature(self):
		"""
		temp,unit = temperaturesensor_MAXIM.temperature()
		
		Read out current temperaure value.
		
		INPUT:
		(none)
		
		OUTPUT:
		temp: temperature value (float)
		unit: unit of temperature value (string)
		"""	

		temp = None;
		unit = '?';
		try:
			self.get_UART_lock()
			temp = self._sensor.get_temperature()
			self.release_UART_lock()
			unit = 'deg.C'
		except:
			self.release_UART_lock()
			self.warning( 'could not read sensor!' )

		return temp,unit


	########################################################################################################
	

	def warning(self,msg):
		'''
		temperaturesensor_MAXIM.warning(msg)
		
		Issue warning about issues related to operation of temperature sensor.
		
		INPUT:
		msg: warning message (string)
		
		OUTPUT:
		(none)
		'''
		
		logger.warning (msg)
		
		
	########################################################################################################
	

	def error(self,msg):
		'''
		temperaturesensor_MAXIM.error(msg)
		
		Issue error about issues related to operation of temperature sensor.
		
		INPUT:
		msg: warning message (string)
		
		OUTPUT:
		(none)
		'''
		
		raise Exception('ERROR from temperaturesensor_MAXIM: ' + msg)
