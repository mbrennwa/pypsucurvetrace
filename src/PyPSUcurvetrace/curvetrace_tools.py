"""
Helper functions for use with curvetrace programs
"""

import time
import math
import os.path

#############
# say hello #
#############

def say_hello(progname, purpose):
	print('\n')
	print('***** ' + progname + ' (PyPSUcurvetrace)')
	print('***** ' + purpose)
	print('***** Disclaimer: NO WARRANTIES OF ANY KIND! Users are advised to study the code in order to understand how this program works.')
	print('\n')


##########################################
# function to get number input from user #
##########################################

def __get_number(text,allowNegative = False,allowZero = True,typ='float'):
	input_ok = False
	while not input_ok:
		try:
			if typ.upper()=='FLOAT':
				val = float(input(text))
			elif typ.upper()=='INT':
				val = int(input(text))

			if not allowNegative:
				if val < 0.0:
					raise ValueError
			if not allowZero:
				if val == 0.0:
					raise ValueError

			input_ok = True

		except ValueError:
			print ('  Invalid input! Try again...')
	
	return val


#############################################################
# format PSU reading as string (according to PSU resolution #
#############################################################

def format_PSU_reading(value, resolution):
	
	# number of digits:
	digits = math.ceil(-math.log10(resolution)) # number of digits corresponding to PSU resolution
	
	# value string:	
	fmt = "{:." + str(digits) + "f}"
	s = fmt.format(value)
	return s


############################################
# start a new file for logging data output #
############################################

def start_new_logfile(do_batch=False, basename=None, step=None):

	samplename = None

	while samplename is None:

		# ask for sample name:
		while basename is None:
			if do_batch:
				basename = input('Enter batch base name / label: ')
			else:
				basename = input('Enter base name / label: ')
			if basename == '':
				print('Name must not be empty!')
				basename = None
		basename = basename.strip()

		# determine step number:
		if not do_batch:
			step = None
		else:
			if step is None:
				step = __get_number('Enter number of first step in batch: ', allowNegative=False, allowZero=False, typ='int')

		# determine sample name:
		samplename = basename
		if step != None:
			samplename = samplename + '_' + str(step)
		
		# name of data file:
		logfilename = samplename + '.dat'
		
		# check if data file exists:
		if os.path.exists(logfilename):
			u = 'Data / log file ' + logfilename + ' exists!'
			if do_batch:
				input (u + ' Try moving the file out of the way, then press ENTER...')
			else:
				print(u + ' Please try a different name...')
			samplename = None
			basename = None

	# start logfile:
	logfile = open(logfilename,'w')
	if logfile:
	    print('\nLogging output to ' + logfilename + '...')
	else:
	    print('Could not open log file!')
	    exit()
	    
	return logfile, samplename, basename, step


#############################################################
# function to print output both to console and to data file #
#############################################################

def printit(text,f='',comm='', terminal_output=True):
	if terminal_output:
		print(text)
	if f:
		if len(comm):
			text = comm + ' ' + text
		print(text,file=f)
		f.flush()
	return



def __convert_str_tuple(x):
	# convert string x = "(1,2,3)" to tuple of floats y = (1.0, 2.0, 3.0)
	return tuple(float(s) for s in x.strip("()").split(","))




###########################
# connect to power supply #
###########################

def connect_PSU(configTESTER,label):

	import PyPSUcurvetrace.powersupply as powersupply

	if not (label in configTESTER):
		# print(label + ' not specified in configuration file. Leaving ' + label + ' unconfigured.')
		P = powersupply.PSU(label=label) # init empty PSU object

	else:

		# read COMPORT field (mandatory):
		if 'COMPORT' in configTESTER[label]:
			port=configTESTER[label]['COMPORT']
		else:
			print ('No COMPORT field in the PSU configuration file! Cannot continue.')
			exit()

		# check if this is a single PSU unit, or a stack of serial connected PSUs:
		num_PSU = 1 # number of PSUs
		try:
			x = eval(port)
			if type(x) is tuple:
				num_PSU = len(x)
				port = x
		except:
			pass

		# read TYPE field (mandatory):
		if 'TYPE' in configTESTER[label]:
			commandset = configTESTER[label]['TYPE']
		else:
			print ('No TYPE field in the PSU configuration file! Cannot continue.')
			exit()
		if num_PSU > 1:
			try:
				x = eval(commandset)
				if type(x) is not tuple:
					raise ValueError
				commandset = x
			except ValueError:
				print("Could not parse TYPEs of stacked PSUs.")
				exit()
				
		# read "calibration curves" (polynomials), if specified:
		try:
			V_SET_CALPOLY = __convert_str_tuple(configTESTER[label]['V_SET_CALPOLY'])
		except:
			V_SET_CALPOLY = (0, 1)
			pass
		try:
			V_READ_CALPOLY = __convert_str_tuple(configTESTER[label]['V_READ_CALPOLY'])
		except:
			V_READ_CALPOLY = (0, 1)
			pass
		try:
			I_SET_CALPOLY = __convert_str_tuple(configTESTER[label]['I_SET_CALPOLY'])
		except:
			I_SET_CALPOLY = (0, 1)
			pass
		try:
			I_READ_CALPOLY = __convert_str_tuple(configTESTER[label]['I_READ_CALPOLY'])
		except:
			I_READ_CALPOLY = (0, 1)
			pass

		# connect to PSU(s):
		print ('Connecting to power supply ' + label + '...')
		P = powersupply.PSU(port, commandset, label, V_SET_CALPOLY, V_READ_CALPOLY, I_SET_CALPOLY, I_READ_CALPOLY)

		# set number of consistent readings for measurements (optional):
		if 'NUMSTABLEREAD' in configTESTER[label]:
			P.NSTABLEREADINGS = int(configTESTER[label]['NUMSTABLEREAD'])
		else:
			print ('Number of consistent measurement readings not configured! Using N = 1...')
			P.NSTABLEREADINGS = 1
			
		if P.CONNECTED:

			# make sure the PSU output is turned off:
			P.turnOff()

			# show summary
			for k in range(len(P._PSU)):
				if len(P._PSU) > 1:
					print ('* Command set (unit '+str(k+1)+'): ' + P._PSU[k].COMMANDSET)
					print ('* Model (unit '+str(k+1)+'): ' + P._PSU[k].MODEL)
				else:
					print ('* Command set: ' + P._PSU[k].COMMANDSET)
					print ('* Model: ' + P._PSU[k].MODEL)
			print ('* Min. voltage: ' + str(P.VMIN) + ' V')
			print ('* Max. voltage: ' + str(P.VMAX) + ' V')
			print ('* Max. current: ' + str(P.IMAX) + ' A')
			print ('* Max. power: ' + str(P.PMAX) + ' W')
			print ('* Voltage setting resolution: ' + str(P.VRESSET) + ' V')
			print ('* Current setting resolution: ' + str(P.IRESSET) + ' A')
			print ('* Voltage reading resolution: ' + str(P.VRESREAD) + ' V')
			print ('* Current reading resolution: ' + str(P.IRESREAD) + ' A')
			print ('* Number of consistent readings for measurements: ' + str(P.NSTABLEREADINGS))
			### print ('* Settle time: ' + str(PSU.settletime()) + ' s')

	return P



###############################
# configure PSU test settings #
###############################

def configure_test_PSU(PSU,configDUT = []):
	
	if not PSU.CONNECTED:
		print ('\n' + PSU.LABEL + ' is not connected (or connection is not configured).')
		PSU.CONFIGURED = False
	else:

		print ('\n' + 'Configuring ' + PSU.LABEL + ' test settings...')

		# take parameters from DUT config file where available, otherwise ask user:

		if 'VSTART' in configDUT:
			PSU.TEST_VSTART = float(configDUT['VSTART'])
		else:
			PSU.TEST_VSTART = __get_number('* ' + PSU.LABEL + ' start voltage (V): ',allowZero=True,allowNegative=False,typ='float')

		if 'VEND' in configDUT:
			PSU.TEST_VEND   = float(configDUT['VEND'])
		else:
			PSU.TEST_VEND   = __get_number('* ' + PSU.LABEL + ' end voltage (V): ',allowZero=True,allowNegative=False,typ='float')

		if PSU.TEST_VSTART == PSU.TEST_VEND:
			PSU.TEST_VSTEP = 0
		else:
			if 'VSTEP' in configDUT:
				PSU.TEST_VSTEP  = float(configDUT['VSTEP'])
			else:
				PSU.TEST_VSTEP      = __get_number('* ' + PSU.LABEL + ' voltage step size (V): ',allowZero=False,allowNegative=False,typ='float')

		if 'IMAX' in configDUT:
			PSU.TEST_ILIMIT = float(configDUT['IMAX'])
		else:
			PSU.TEST_ILIMIT = __get_number('* ' + PSU.LABEL + ' maximum allowed current (A): ',allowZero=False,allowNegative=False,typ='float')

		if 'PMAX' in configDUT:
			PSU.TEST_PLIMIT = float(configDUT['PMAX'])
		else:
			PSU.TEST_PLIMIT = __get_number('* ' + PSU.LABEL + ' maximum allowed power (W): ',allowZero=False,allowNegative=False,typ='float')
			
		if 'POLARITY' in configDUT:
			PSU.TEST_POLARITY = int(configDUT['POLARITY'])
		else:
			try:
				pol = (input('* OPTIONAL: ' + PSU.LABEL + ' polarity of outputs -- N: normal / I: inverted [default=N]: '))
			except ValueError:
				print ('  Using default: normal polarity.')
				pol = 'N'
			if pol.upper() == 'I':
				PSU.TEST_POLARITY = -1
			else:
				PSU.TEST_POLARITY = 1;
			
		PSU.CONFIGURED = True

	return PSU



###############################
# configure PSU idle settings #
###############################

def configure_idle_PSU(PSU,configDUT):
	
	if PSU.CONFIGURED:

		if configDUT:
			# take configuration from DUT config file:
			PSU.TEST_VIDLE = float(configDUT['VIDLE'])
			if not 'VIDLE_MIN' in configDUT:
				PSU.TEST_VIDLE_MIN = PSU.TEST_VIDLE # fixed idle voltage
			else:
				PSU.TEST_VIDLE_MIN = float(configDUT['VIDLE_MIN'])
			if not 'VIDLE_MAX' in configDUT:
				PSU.TEST_VIDLE_MAX = PSU.TEST_VIDLE # fixed idle voltage
			else:
				PSU.TEST_VIDLE_MAX = float(configDUT['VIDLE_MAX'])				
			if not 'PIDLEMAX' in configDUT:
				PSU.TEST_PIDLELIMIT = PSU.TEST_PLIMIT # use same power limit as for test conditions
			else:
				PSU.TEST_PIDLELIMIT = float(configDUT['PIDLEMAX'])
			if not 'IDLE_GM' in configDUT:
				PSU.TEST_IDLE_GM = None # unknown transconductance
			else:
				PSU.TEST_IDLE_GM = float(configDUT['IDLE_GM']) # unknown transconductance (delta-I1 / delta-U2 or delta-U2 / delta-I1 in A/V)
			PSU.TEST_IIDLE = float(configDUT['IIDLE'])

		else:
			print ('\n' + 'configure ' + PSU.LABEL + ' idle settings:')
			PSU.TEST_VIDLE = __get_number('* ' + PSU.LABEL + ' idle voltage (V): ',allowZero=True,allowNegative=False,typ='float')
			try:
				PSU.TEST_VIDLE_MIN = float(input('* OPTIONAL: ' + PSU.LABEL + ' idle voltage range, minimum value (V): '))
			except ValueError:
				PSU.TEST_VIDLE_MIN = PSU.TEST_VIDLE # fixed idle voltage
				PSU.TEST_VIDLE_MAX = PSU.TEST_VIDLE # fixed idle voltage
			try:
				PSU.TEST_VIDLE_MAX = float(input('* OPTIONAL: ' + PSU.LABEL + ' idle voltage range, maximum value (V): '))
			except ValueError:
				PSU.TEST_VIDLE_MAX = PSU.TEST_VIDLE # fixed idle voltage

			if PSU.TEST_VIDLE_MAX == PSU.TEST_VIDLE_MIN:
				PSU.TEST_IDLE_GM = None # unknown transconductance
			else:
				PSU.TEST_IDLE_GM = __get_number('* ' + PSU.LABEL + ' DUT transconductance at idle conditions (in A/V): ',allowZero=False,allowNegative=False,typ='float')
			PSU.TEST_IIDLE = __get_number('* ' + PSU.LABEL + ' idle current (A): ',allowZero=True,allowNegative=False,typ='float')


	return PSU


##########################
# do idle / DUT break-in #
##########################

def do_idle(PSU1, PSU2, HEATER, seconds, file=None, wait_for_TEMP=False):
	
	REG = None

	# do DUT break-in:
	if PSU1.CONFIGURED and PSU2.CONFIGURED:
		if not PSU1.TEST_VIDLE_MIN == PSU1.TEST_VIDLE_MAX:
			REG = PSU1
			FIX = PSU2
		elif not PSU2.TEST_VIDLE_MIN == PSU2.TEST_VIDLE_MAX:
			REG = PSU2
			FIX = PSU1

	if REG == None: # no regulation of idle bias, just fixed values:
		for p in [PSU1, PSU2]:
			if p.CONFIGURED:
				p.setCurrent(p.TEST_IIDLE,False)
				p.setVoltage(p.TEST_VIDLE,False) # don't check for stable voltage, since current limiter may upset the the voltage value
		# wait pre-heat time:
		time.sleep(seconds)

	else: # fixed output on FIX power supply and regulated output on REG power supply

		IFIXLIM = min (FIX.TEST_ILIMIT,FIX.TEST_PIDLELIMIT/FIX.TEST_VIDLE); # current limit set at fixed PSU
		
		# sleep time (seconds):
		dt = 0.0
		
		# Set output limits at the fixed PSU:
		FIX.setCurrent(IFIXLIM,False)
		FIX.setVoltage(FIX.TEST_VIDLE,True)

		# Set output at the regulating PSU:
		REG.setCurrent(REG.TEST_IIDLE,False) # current limit
		REG.setVoltage(REG.TEST_VIDLE,True) # set last-used idle setting

		# start idling:
		t0 = time.time()
		timenow = time.time()
		heater_delays = 0.0
		while timenow < t0+seconds+heater_delays:

			# wait for heaterblock to reach prescribed temperature (if configured/available/required):
			if wait_for_TEMP:
				heater_delays += HEATER.wait_for_stable_T(DUT_PSU_allowed_turn_off=None, terminal_output=True)

			# read and print voltages and currents at FIX and REG outputs:
			f = FIX.read()
			r = REG.read()

			Uf = f[0]
			If = f[1]

			Ur = r[0]
			Ir = r[1]
			
			T_HB = HEATER.get_temperature_string(do_read=False)

			# output string / line			
			t = "Idling ({:.1f}".format(time.time()-t0-heater_delays) + ' of ' + "{:.1f}".format(seconds) + ' s): ' + \
			    "U0 = " + format_PSU_reading(FIX.TEST_POLARITY*Uf, FIX.VRESREAD) + " V" + '  ' + \
			    "I0 = " + format_PSU_reading(FIX.TEST_POLARITY*If, FIX.IRESREAD) + " A" + '  ' + \
			    "Uc = " + format_PSU_reading(REG.TEST_POLARITY*Ur, REG.VRESREAD) + " V" + '  ' + \
			    "Ic = " + format_PSU_reading(REG.TEST_POLARITY*Ir, REG.IRESREAD) + " A" + '  ' + \
			    "T = " + T_HB + " °C"
			print (t, end="\r")

			if f[2] == "CC":
				If = IFIXLIM * (1+(FIX.TEST_VIDLE-Uf)/FIX.TEST_VIDLE)

			dIf = If-FIX.TEST_IIDLE  # deviation of the observed idle current from the target value
			if not dIf == 0.0:
				# determine the voltage changed needed for Ur voltage:
				dUr = 0.65 * dIf / REG.TEST_IDLE_GM
				
				if REG.TEST_VIDLE - dUr < REG.TEST_VIDLE_MIN:
					REG.TEST_VIDLE = REG.TEST_VIDLE_MIN
				elif REG.TEST_VIDLE - dUr > REG.TEST_VIDLE_MAX:
					REG.TEST_VIDLE = REG.TEST_VIDLE_MIN
				else:
					REG.TEST_VIDLE = REG.TEST_VIDLE - dUr
				REG.setVoltage(REG.TEST_VIDLE,True)

			time.sleep(dt)
			timenow = time.time()

		# Clear the terminal:
		print (' '*len(t), end="\r")

		# write idle / preheat conditions to file:
		if file is not None:
			t = '* OPERATING POINT AT END OF PREHEAT / IDLE: ' + \
			    "U0 = " + format_PSU_reading(FIX.TEST_POLARITY*Uf, FIX.VRESREAD) + " V" + '  ' + \
			    "I0 = " + format_PSU_reading(FIX.TEST_POLARITY*If, FIX.IRESREAD) + " A" + '  ' + \
			    "Uc = " + format_PSU_reading(REG.TEST_POLARITY*Ur, REG.VRESREAD) + " V" + '  ' + \
			    "Ic = " + format_PSU_reading(REG.TEST_POLARITY*Ir, REG.IRESREAD) + " A" + '  ' + \
			    "T = " + T_HB + " °C"
			printit(t, file , '%')
