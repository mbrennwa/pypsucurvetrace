"""
Python class to control RIDEN (RUIDEN) RDxxxx power supplies
"""

# Useful information about RIDEN Modbus registers and other details: https://github.com/ShayBox/Riden

import time
import minimalmodbus
from pypsucurvetrace.curvetrace_tools import get_logger

# set up logger:
logger = get_logger('powersupply_RIDEN')

# Python dictionary of known KORAD (RND) power supply models (Vmin,Vmax,Imax,Pmax,Vresolution,Iresolution,VoffsetMax,IoffsetMax,MaxSettleTime)

RIDEN_SPECS = {
		"RD6006":	    ( 0.0, 60.0,  6.0,  360,  0.001,  0.001,  0.0, 0.0, 0.3 ) , # not confirmed
		"RD6006P":	    ( 0.0, 60.0,  6.0,  360,  0.001,  0.0001, 0.0, 0.0, 1.5 ) , # confirmed working
		"RD6012":	    ( 0.0, 60.0, 12.0,  720,  0.001,  0.001,  0.0, 0.0, 0.3 ) , # not confirmed
		"RD6012P_6A":	( 0.0, 60.0,  6.0,  360,  0.001,  0.0001, 0.0, 0.0, 1.8 ) , # 6012P in low-current mode (0..6A at 0.1 mA resolution), confirmed working
		"RD6012P_12A":	( 0.0, 60.0, 12.0,  720,  0.001,  0.001,  0.0, 0.0, 1.8 ) , # 6012P in high-current mode (0..12A at 1 mA resolution), confirmed working
}

RIDEN_TIMEOUT = 1.0

MAX_COMM_ATTEMPTS = 10

def _RIDEN_debug(s):
	sys.stdout.write(s)
	sys.stdout.flush()

# RIDEN:
#    .output(state)
#    .voltage(voltage)
#    .current(current)
#    .reading()
#    .VMIN
#    .VMAX
#    .IMAX
#    .VRESSET
#    .IRESSET
#    .VRESREAD
#    .IRESREAD
#    .VOFFSETMAX
#    .VOFFSETMAX
#    .IOFFSETMAX
#    .MAXSETTLETIME
#    .READIDLETIME
#    .MODEL

class RIDEN(object):
	"""
	Class for RIDEN (RUIDEN) power supply
	"""

	def __init__(self, port, baud=115200, currentmode = 'LOW', debug=False):
		'''
		PSU(port)
		port : serial port (string, example: port = '/dev/serial/by-id/XYZ_123_abc')
		baud : baud rate of serial port (check the settings at the RD PSU unit)
		currentmode: use 'LOW' or 'HIGH' to configure PSU units to use low/high current modes (with corresponding current resolution) [only for units that support this, like the 6012P]
		debug: flag for debugging info (bool)
		'''
		
		self._debug = bool(debug)
		
		# open and configure ModBus/serial port:
		try:
		    self._instrument = minimalmodbus.Instrument(port=port, slaveaddress=1)
		    self._instrument.serial.baudrate = baud
		    self._instrument.serial.timeout = 1.0
		    time.sleep(0.2) # wait a bit unit the port is really ready
		except:
		    raise RuntimeError('Could not connect to RIDEN powersupply at ' + port)


		# determine model / type:
		try:
	        # OCP and OVP max values:
		    OCP_max = OVP_max = None
		    mdl = self._get_register(0)
		    if 60060 <= mdl <= 60064:
		        # RD6006
		        self.MODEL = 'RD6006'
		        OVP_max = 61.0
		        OCP_max = 6.1
		        logger.warning ( 'Operation of RIDEN ' + self.MODEL + ' with pypsucurvetrace is untested -- be careful!' )
                
		    elif mdl == 60065:
		        # RD6006P
		        self.MODEL = 'RD6006P'
		        OVP_max = 61.0
		        OCP_max = 6.1
                
		    elif 60120 <= mdl <= 60124:
		        # RD6012
		        self.MODEL = 'RD6012'
		        OVP_max = 61.0
		        OCP_max = 12.1
		        logger.warning ( 'Operation of RIDEN ' + self.MODEL + ' with pypsucurvetrace is untested -- be careful!' )
            
		    elif 60125 <= mdl <= 60129:
		        # RD6012P
		        if currentmode == 'LOW':
		            self.MODEL = 'RD6012P_6A'
		            self._set_register(20,0) # set low-current mode
		            OCP_max = 6.1
		        else:
		            self.MODEL = 'RD6012P_12A'
		            self._set_register(20,1) # set high-current mode
		            OCP_max = 12.1
		        OVP_max = 61.0

		                        
		    elif 60180 <= mdl <= 60189:
		        # RD6018
		        self.MODEL = 'RD6018'
		        logger.warning ( 'Operation of RIDEN ' + self.MODEL + ' with pypsucurvetrace is untested -- be careful!' )
		        OVP_max = 61.0
		        OCP_max = 18.1
            
		    else:
		        # unknown RD model:
		        logger.warning ( 'Unknown RIDEN model ID: ' + mdl )
		        self.MODEL = '<unknown>'

		    self.VMIN          = RIDEN_SPECS[self.MODEL][0]
		    self.VMAX          = RIDEN_SPECS[self.MODEL][1]
		    self.IMAX          = RIDEN_SPECS[self.MODEL][2]
		    self.PMAX          = RIDEN_SPECS[self.MODEL][3]
		    self.VRESSET       = RIDEN_SPECS[self.MODEL][4]
		    self.VRESREAD      = RIDEN_SPECS[self.MODEL][4]
		    self.IRESSET       = RIDEN_SPECS[self.MODEL][5]
		    self.IRESREAD      = RIDEN_SPECS[self.MODEL][5]
		    self.VOFFSETMAX    = RIDEN_SPECS[self.MODEL][6]
		    self.IOFFSETMAX    = RIDEN_SPECS[self.MODEL][7]
		    self.MAXSETTLETIME = RIDEN_SPECS[self.MODEL][8]
		    self.READIDLETIME  = self.MAXSETTLETIME/5
		    
		except KeyError:
		    raise RuntimeError('Unknown RIDEN powersupply type/model ' + self.MODEL)
		except:
		    raise RuntimeError('Could not determine RIDEN powersupply type/model')
		    
		# set over-voltage and over-current settings to max. values (to avoid them from unintended limiting):

		if ( OCP_max is None ) or ( OVP_max is None ):
		    logger.warning( 'Cannot adjust OVP and OCP limits of the ' + self.MODEL + ' power supply.' )
		else:
		    logger.info ( 'Adjusting OVP to ' + str(OVP_max) + ' V and and OCP to ' + str(OCP_max) + ' A.' )
		    R = [82, 86, 90, 94, 98, 102, 106, 110, 114, 118] # OVP registers (OCP are +1)
		    mul_U = self._voltage_multiplier()
		    mul_I = self._current_multiplier()
		    for r in R:
		       self._set_register(r, OVP_max*mul_U)
		       self._set_register(r+1, OCP_max*mul_I)


	def _set_register(self, register, value):
	    k = 1
	    while k <= MAX_COMM_ATTEMPTS:
	        try:
        	    self._instrument.write_register(register, int(value))
        	    break # break from the loop if communication was successful
        	except:
        	    k += 1
        	    pass # keep trying
	    if k > MAX_COMM_ATTEMPTS:
	        raise RuntimeError('Communication with RIDEN ' + self.MODEL + ' at ' + self._instrument.serial.port + ' failed.')
            

	def _get_register(self, register):
	    value = None
	    k = 1
	    while k <= MAX_COMM_ATTEMPTS:
	        try:
        	    value = self._instrument.read_register(register)
        	    break # break from the loop if communication was successful
	        except:
        	    k += 1
        	    pass # keep trying
	    if k > MAX_COMM_ATTEMPTS:
	        raise RuntimeError('Communication with RIDEN ' + self.MODEL + ' at ' + self._instrument.serial.port + ' failed.')
 
	    return value


	def _get_N_registers(self, register_start, N):
	    value = None
	    k = 1
	    while k <= MAX_COMM_ATTEMPTS:
	        try:
        	    values = self._instrument.read_registers(register_start, N)
        	    break # break from the loop if communication was successful
	        except:
        	    k += 1
        	    pass # keep trying
	    if k > MAX_COMM_ATTEMPTS:
	        raise RuntimeError('Communication with RIDEN ' + self.MODEL + ' at ' + self._instrument.serial.port + ' failed.')
 
	    return values


	def output(self, state):
		"""
		enable/disable the PS output
		"""
		state = int(bool(state))
		self._set_register(18, state)


	def voltage(self, voltage):
		"""
		set voltage: silently saturates at VMIN and VMAX
		"""
		if voltage > self.VMAX:
			voltage = self.VMAX
		if voltage < self.VMIN:
			voltage = self.VMIN
            
		self._set_register(8, round(voltage*self._voltage_multiplier()))
		
		## time.sleep(0.5)
		
		u = self.reading()
		

	def current(self, current):
		"""
		set current: silently saturates at IMIN and IMAX
		"""
        
		if current > self.IMAX:
			current = self.IMAX
		if current < 0.0:
			current = 0.0
		
		self._set_register(9, round(current*self._current_multiplier()))


	def reading(self):
		"""
		read applied output voltage and current and if PS is in "CV" or "CC" mode
		"""
		
		# read voltage and current registers:
		V_mult = self._voltage_multiplier()
		I_mult = self._current_multiplier()
		u = self._get_N_registers(10,2)
		V = u[0] / V_mult
		I = u[1] / I_mult
        
		# check register 17 (CV or CC?)
		if self._get_register(17) == 1:
		    S = 'CC'
		else:
		    S = 'CV'

		return (V, I, S)


	def _voltage_multiplier(self):
		"""
		return multiplier for voltage register value
		"""
		
		multi = 1.0 / float(RIDEN_SPECS[self.MODEL][4])

		return multi
		

	def _current_multiplier(self):
		"""
		return multiplier for current register value
		"""
		
		multi = 1.0 / float(RIDEN_SPECS[self.MODEL][5])
            
		return multi
		
		
	def _current_multiplier_nadanixdabum(self):
		"""
		return multiplier for current register value
		"""
		
		if 'RIDEN6012P' in self.MODEL:
		    if self._get_register(20) == 0:
		        multi = 10000.0
		    else:
		        multi = 1000.0
		        
		else:
		    multi = 1.0 / float(RIDEN_SPECS[self.MODEL][5])
            
		return multi
