# This file is part of pypsucurvetrace, a toolbox for I/V curve tracing of electronic parts using programmable power supplies.
#
# pypsucurvetrace is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pypsucurvetrace is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pypsucurvetrace.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import configparser
import datetime
import numpy as np
import time
import logging
import matplotlib.pyplot as plt
import multiprocessing
from pathlib import Path

import pypsucurvetrace.powersupply as powersupply
import pypsucurvetrace.heaterblock as heaterblock
from pypsucurvetrace.curvetrace_tools import error_and_exit, say_hello, printit, connect_PSU, configure_test_PSU, configure_idle_PSU, do_idle, start_new_logfile, format_PSU_reading, get_logger
from pypsucurvetrace.plot_curves import curve_plotter


# set up logger:
logger = get_logger('curvetrace')


if __name__ == "__main__":
    ctrace()


def cleanup_exit(PSU1, PSU2, HEATER, queue, plt_proc):
###################
# cleanup at exit #
###################

	# Try hard to turn off all PSUs to avoid unwanted/unattended powering of the DUT or heater block.

	for p in [PSU1, PSU2]:
		try:
			if p.CONNECTED:
				p.turnOff()
		except:
			logger.warning('Could not turn off PSU ' + p.LABEL + '!')
			pass

	try:
		HEATER.turn_off()
	except Exception as e:
		logger.warning('Could not turn off heater: ' + repr(e))
		pass
	try:
		HEATER.terminate_controller_thread()
	except Exception as e:
		logger.warning('Could not terminate heaterblock controller thread: ' + repr(e))
		pass

	# stop curve-plotter process and wait for the process to finish
	queue.put( None )
	queue.close()
	queue.join_thread()
	plt_proc.join()


def ctrace():
    ################
    # main program #
    ################

    # parse input arguments (if any):
    parser = argparse.ArgumentParser(description='curvetrace (pypsucurvetrace) is a Python program for I-V curve tracing of electronic parts using programmable power supplies.')
    parser.add_argument('-c', '--config', help='path to configuration file with DUT test parameters')
    parser.add_argument('-b', '--batch', action='store_true', help='batch mode (loop of repeated test tuns)')
    parser.add_argument('-q', '--quick', action='store_true', help='quick mode (pre-heating only, no curve tracing)')
    args = parser.parse_args()

    # Say Hello:
    say_hello('curvetrace', 'I-V curve tracing of electronic parts using programmable power supplies')

    # read PSU config file:
    cfgfile = 'pypsucurvetrace_config.txt'
    cfgfile = Path.home() / cfgfile
    if not cfgfile.is_file():
        error_and_exit(logger, 'Could not find config file ' + str(cfgfile) + '.')
    configTESTER = configparser.ConfigParser()
    configTESTER.read(cfgfile)

    # check for batch mode:
    batch_mode = False
    if args.batch:
	    logger.info('Running in batch mode (loop of repeated test tuns)...')
	    batch_mode = True

    # check for quick mode:
    quick_mode = False
    if args.quick:
	    logger.info('Running in quick mode (pre-heating only, no curve tracing)...')
	    quick_mode = True

    # read DUT test config file (if any):
    configDUT = []
    if args.config:
	    logger.info('Reading DUT configuration in file ' + args.config + '...')
	    configDUT = configparser.ConfigParser()
	    configDUT.read(args.config)
	    
    # connect to PSUs:
    try:
        PSU1 = connect_PSU(configTESTER, 'PSU1', logger);
    except Exception as e:
        error_and_exit(logger, 'Could not connect to PSU1', e)
    try:
        PSU2 = connect_PSU(configTESTER, 'PSU2', logger);
    except Exception as e:
        error_and_exit(logger, 'Could not connect to PSU1', e)

    # set up heaterblock:
    HEATER = heaterblock.heater( config=configTESTER, target_temperature=0.0, DUT_PSU1=PSU1, DUT_PSU2=PSU2 )
    HEATER.turn_off()

    logfile, samplename, basename, step = start_new_logfile(logger, batch_mode)

    # configure voltage values / current and power limits:
    if 'PSU1' in configDUT:
	    PSU1 = configure_test_PSU (PSU1, logger, configDUT['PSU1'])
    else:
	    PSU1 = configure_test_PSU (PSU1, logger)
    if 'PSU2' in configDUT:
	    PSU2 = configure_test_PSU (PSU2, logger, configDUT['PSU2'])
    else:
	    PSU2 = configure_test_PSU (PSU2, logger)

    # check if at least one of the power supplies is configured:	
    if not PSU1.CONFIGURED:
	    if not PSU2.CONFIGURED:
		    error_and_exit(logger, 'No power supply configured.')

    # determine R2CONTROL (opitonal, may be missing in DUT config file):
    R2CONTROL = None
    try:
	    R2CONTROL = float(configDUT['EXTRA']['R2CONTROL'])
    except:
	    pass

    # set up temperature control (optional, may be missing in DUT config file):
    TEMP_val = None
    TEMP_tol = None
    try:
	    TEMP_val = float(configDUT['EXTRA']['T_TARGET'])
	    TEMP_tol = float(configDUT['EXTRA']['T_TOL'])
    except:
	    pass
    HEATER.set_target_temperature(TEMP_val, TEMP_tol)

    # set up repeats:
    if 'EXTRA' in configDUT:
	    N_rep = int(configDUT['EXTRA']['NREP'])
    else:
	    try:
		    N_rep = int(input('\nOPTIONAL: Number of repeats per reading [default=1]: '))
	    except ValueError:
		    logger.info('  Using default: single reading.')
		    N_rep = 1
    if N_rep <= 0:
	    raise ValueError('Number of repeats must be positive.')

    # set up idle time between readings:
    if 'EXTRA' in configDUT:
	    T_idle    = float(configDUT['EXTRA']['IDLESECS'])
    else:
	    try:
		    T_idle = float(input('\nOPTIONAL: idle time between readings (s) [default=0]: '))
	    except ValueError:
		    logger.info('  Using default: no idle time.')
		    T_idle = 0.0
    if T_idle < 0:
	    raise ValueError('Idle time must not be negative.')

    # set up pre-heat time between readings:
    if 'EXTRA' in configDUT:
	    T_preheat    = float(configDUT['EXTRA']['PREHEATSECS'])
    else:
	    try:
		    T_preheat = float(input('\nOPTIONAL: pre-heat time before starting the test (s) [default=0]: '))
	    except ValueError:
		    logger.info('  Using default: no pre-heating.')
		    T_preheat = 0.0
    if T_preheat < 0:
	    raise ValueError('Pre-heat time must not be negative.')

    # set up idle conditions (for pre-heat or idle between readings)
    if (T_idle > 0.0) or (T_preheat > 0.0):
	    if PSU1.CONFIGURED:
		    if 'PSU1' in configDUT:
			    PSU1 = configure_idle_PSU (PSU1,configDUT['PSU1'])
		    else:
			    PSU1 = configure_idle_PSU (PSU1,None)
	    if PSU2.CONFIGURED:
		    if 'PSU2' in configDUT:
			    PSU2 = configure_idle_PSU (PSU2,configDUT['PSU2'])
		    else:
			    PSU2 = configure_idle_PSU (PSU2,None)

	    if PSU1.CONNECTED and PSU2.CONNECTED:
		    if (not PSU1.TEST_VIDLE_MAX == PSU1.TEST_VIDLE_MIN) and (not PSU2.TEST_VIDLE_MAX == PSU2.TEST_VIDLE_MIN):
			    error_and_exit(logger, 'Both PSUs are configured with variable idle voltages. This cannot work.')

    # check voltage / power / current limits (and fix where possible and necessary):
    logger.info('Checking voltage / current settings...')
    for p in [PSU1,PSU2]:
	    if p.CONNECTED:
		    if p.TEST_VSTART < p.VMIN:
			    logger.info('  ' + p.LABEL + ': Adjusting start voltage to min. value possible with the power supply (' + str(p.VMIN) + ' V).')
			    p.TEST_VSTART = p.VMIN
		    if p.TEST_VSTART > p.VMAX:
			    logger.info('  ' + p.LABEL + ': Adjusting start voltage to max. value possible with the power supply (' + str(p.VMAX) + ' V).')
			    p.TEST_VSTART = p.VMAX
		    if p.TEST_VEND < p.VMIN:
			    logger.info('  ' + p.LABEL + ': Adjusting end voltage to min. value possible with the power supply (' + str(p.VMIN) + ' V).')
			    p.TEST_VEND = p.VMIN
		    if p.TEST_VEND > p.VMAX:
			    logger.info('  ' + p.LABEL + ': Adjusting end voltage to max. value possible with the power supply (' + str(p.VMAX) + ' V).')
			    p.TEST_VEND = p.VMAX
		    if p.TEST_VEND == p.TEST_VSTART:
			    # logger.info('  ' + p.LABEL + ': Same start and end voltage, test will run at fixed voltage (' + str(p.TEST_VSTART) + ' V).')
			    p.TEST_VSTEP = 0
		    if abs(p.TEST_VEND-p.TEST_VSTART) < p.VRESSET:
			    logger.info('  ' + p.LABEL + ': Test voltage range is less than voltage setting resolution of the PSU. Test will run at fixed voltage (' + str(p.TEST_VSTART) + ' V).')
			    p.TEST_VSTEP = 0
			    p.TEST_VEND = p.TEST_VSTART
		    if p.TEST_VSTEP > 0.0:
			    if p.TEST_VSTEP > abs(p.TEST_VEND-p.TEST_VSTART):
				    p.TEST_VSTEP = abs(p.TEST_VEND-p.TEST_VSTART)
				    logger.info('  ' + p.LABEL + ': Voltage step size exceeds test voltage range. Adjusting step size to ' + str(p.TEST_VSTEP) + ' V.')
			    if p.TEST_VSTEP < p.VRESSET:
				    logger.info('  ' + p.LABEL + ': Voltage step size is less than PSU resolution of voltage setting. Adjusting step size to ' + str(p.VRESSET) + ' V.')
				    p.TEST_VSTEP = p.VRESSET
			    if p.TEST_VSTEP/p.VRESSET < p.VRESSET:
				    logger.info('  ' + p.LABEL + ': Voltage step size is less than PSU resolution of voltage setting. Adjusting step size to ' + str(p.VRESSET) + ' V.')
				    p.TEST_VSTEP = p.VRESSET
			    if not ( p.TEST_VSTEP / p.VRESSET == round(p.TEST_VSTEP / p.VRESSET) ):
				    u = p.TEST_VSTEP
				    p.TEST_VSTEP = round(p.TEST_VSTEP / p.VRESSET) * p.VRESSET
				    logger.info('  ' + p.LABEL + ': Voltage step size (' + str(u) + ' V) is not consistent with PSU resolution of voltage setting. Adjusting step size to ' + str(p.TEST_VSTEP) + ' V.')
		    if p.TEST_ILIMIT > p.IMAX:
			    logger.info('  ' + p.LABEL + ': Adjusting current limit to max. value possible with the power supply (' + str(p.IMAX) + ' A).')
			    p.TEST_ILIMIT = p.IMAX
		    if p.TEST_PLIMIT > p.PMAX:
			    logger.info('  ' + p.LABEL + ': Adjusting power limit to max. value possible with the power supply (' + str(p.PMAX) + ' W).')
			    p.TEST_PLIMIT = p.PMAX
		    if (T_idle > 0.0) or (T_preheat > 0.0):
			    if p.TEST_PIDLELIMIT > p.PMAX:
				    logger.info('  ' + p.LABEL + ': Adjusting idle power limit to max. value possible with the power supply (' + str(p.PMAX) + ' W).')
				    p.TEST_PIDLELIMIT = p.PMAX
			    if p.TEST_VIDLE > p.VMAX:
				    logger.info('  ' + p.LABEL + ': Adjusting idle voltage to max. value possible with the power supply (' + str(p.VMAX) + ' V).')
				    p.TEST_VIDLE = p.VMAX
			    if p.TEST_VIDLE < p.VMIN:
				    logger.info('  ' + p.LABEL + ': Adjusting idle voltage to min. value possible with the power supply (' + str(p.VMIN) + ' V).')
				    p.TEST_VIDLE = p.VMIN
			    if p.TEST_VIDLE_MAX > p.VMAX:
				    logger.info('  ' + p.LABEL + ': Adjusting max.-idle voltage to max. value possible with the power supply (' + str(p.VMAX) + ' V).')
				    p.TEST_VIDLE_MAX = p.VMAX
			    if p.TEST_VIDLE_MAX < p.VMIN:
				    logger.info('  ' + p.LABEL + ': Adjusting max.-idle voltage to min. value possible with the power supply (' + str(p.VMIN) + ' V).')
				    p.TEST_VIDLE_MAX = p.VMIN
			    if p.TEST_VIDLE_MIN > p.VMAX:
				    logger.info('  ' + p.LABEL + ': Adjusting min.-idle voltage to max. value possible with the power supply (' + str(p.VMAX) + ' V).')
				    p.TEST_VIDLE_MIN = p.VMAX
			    if p.TEST_VIDLE_MIN < p.VMIN:
				    logger.info('  ' + p.LABEL + ': Adjusting min.-idle voltage to min. value possible with the power supply (' + str(p.VMIN) + ' V).')
				    p.TEST_VIDLE_MIN = p.VMIN
			    if p.TEST_VIDLE_MIN > p.TEST_VIDLE_MAX:
				    logger.info('  ' + p.LABEL + ': Adjusting min.-idle voltage to ' + str(p.TEST_VIDLE) + ' V).')
				    p.TEST_VIDLE_MIN = p.TEST_VIDLE
			    if p.TEST_VIDLE_MAX < p.TEST_VIDLE_MIN:
				    logger.info('  ' + p.LABEL + ': Adjusting max.-idle voltage to ' + str(p.TEST_VIDLE) + ' V).')
				    p.TEST_VIDLE_MAX = p.TEST_VIDLE
			    if p.TEST_IIDLE > p.IMAX:
				    logger.info('  ' + p.LABEL + ': Adjusting idle current to max. value possible with the power supply (' + str(p.IMAX) + ' V).')
				    p.TEST_IIDLE = p.IMIN
			    if p.TEST_VIDLE * p.TEST_IIDLE > p.PMAX:
				    p.TEST_IIDLE = p.PMAX / p.TEST_VIDLE
				    logger.info('  ' + p.LABEL + ': Idle current limit is higher than PSU power limit (' + str(p.PMAX) + ' W). Adjusting idle current limit to ' + str(p.TEST_IIDLE) + ' A.' )

    # Print summary of test setup:
    print('\nTest setup:')
    for p in [PSU1, PSU2]:
	    
	    if not p.CONNECTED:
		    print ('* ' + p.LABEL + ': Not connected')
		    print ('* ' + p.LABEL + ': Test parameters not configured')
	    else:
		    print ('* ' + p.LABEL + ':')
		    for k in range(len(p._PSU)):
			    if len(p._PSU) == 1:
				    print ('  - Type: ' + str(p._PSU[k].COMMANDSET) + ' / ' + p._PSU[k].MODEL)
			    else:
				    print ('  - Type (unit '+str(k+1)+'): ' + str(p._PSU[k].COMMANDSET) + ' / ' + p._PSU[k].MODEL)

		    if p.TEST_VSTEP == 0:
			    print ('  - voltage output = ' + str(p.TEST_VSTART) + ' V (fixed)')
		    else:
			    print ('  - voltage output = ' + str(p.TEST_VSTART) + ' V ... ' + str(p.TEST_VEND) + ' V (' + str(p.TEST_VSTEP) + ' V steps)')
		    print ('  - current limit = ' + str(p.TEST_ILIMIT) + ' A')
		    print ('  - power limit = ' + str(p.TEST_PLIMIT) + ' W')
		    if p.TEST_POLARITY == 1:
			    print ('  - polarity: normal')
		    else:
			    print ('  - polarity: inverted')

    print ('* Repeats per reading = ' + str(N_rep))
    if T_idle == 0.0:
	    print ('* No idle time between measurements')
    else:
	    print ('* Idle time between measurements: ' + str(T_idle) + ' s')
    if T_preheat == 0.0:
	    print ('* No pre-heating before measurements')
    else:
	    print ('* Pre-heat time before measurements (at idle conditions): ' + str(T_preheat) + ' seconds')
    if (T_idle > 0.0) or (T_preheat > 0.0):
	    for p in [PSU1, PSU2]:
		    if p.CONNECTED == False:
			    print ('* ' + p.LABEL + ' Idle / pre-heat conditions not configured')
		    else:
			    if p.TEST_VIDLE_MAX == p.TEST_VIDLE_MIN:
				    print ('* ' + p.LABEL + ' idle / pre-heat voltage = ' + str(p.TEST_VIDLE) + ' V (fixed value)')
			    else:
				    print ('* ' + p.LABEL + ' idle / pre-heat voltage range = ' + str(p.TEST_VIDLE_MIN) + ' V ... ' + str(p.TEST_VIDLE_MAX) + ' V.')
			    print ('* ' + p.LABEL + ' idle / pre-heat current = ' + str(p.TEST_IIDLE) + ' A')
			    print ('* ' + p.LABEL + ' max. idle / pre-heat power = ' + str(p.TEST_PIDLELIMIT) + ' W')

    print ('* Heaterblock temperature (current) = ' + str(HEATER.get_temperature_string()))
    print ('* Heaterblock temperature (target)  = ' + str(HEATER.get_target_temperature_string()))

    R2CTL_txt = '* R2CONTROL = '
    u = 'NOT SPECIFIED'
    if R2CONTROL is not None:
	    try:
		    u = str(R2CONTROL) + ' Ohm'
	    except:
		    R2CONTROL = None
    R2CTL_txt = R2CTL_txt + ' ' + u
    print (R2CTL_txt)

    # set up plotting environment
    plt.ion()
    plt.show()

    # set up separate process for data plotting:
    queue = multiprocessing.Queue() # queue for data exchange with the plotting process
    plt_proc = multiprocessing.Process(target=curve_plotter, args=(queue,)) # plotting process
    plt_proc.start() # start the plotting process

    # set function to calculate the "average" value:
    AVGFUNCTION = 'MEAN'
    # AVGFUNCTION = 'MEDIAN'

    # determine voltage step values:
    V_steps = []

    for p in [PSU1,PSU2]:
	    if not p.CONFIGURED:
		    V_steps.append( [ 0 ] )
	    else:
		    if p.TEST_VSTEP == 0:
			    # V_steps.append( np.linspace(p.TEST_VSTART,p.TEST_VSTART,1) )
			    V_steps.append( [ p.TEST_VSTART ] )
		    else:
			    if p.TEST_VSTART <= p.TEST_VEND:
				    u = np.arange( p.TEST_VSTART , p.TEST_VEND+PSU1.TEST_VSTEP ,  p.TEST_VSTEP )
				    u = [i for i in u if (i >= p.TEST_VSTART) and (i <= p.TEST_VEND) ] # filter out "outliers" that may happen with large VSTEPs
			    else:
				    u = np.arange( p.TEST_VSTART , p.TEST_VEND-PSU1.TEST_VSTEP , -p.TEST_VSTEP )
				    u = [i for i in u if (i >= p.TEST_VEND) and (i <= p.TEST_VSTART) ] # filter out "outliers" that may happen with large VSTEPs
			    V_steps.append(u)

    try:

	    # keep start values for idle voltages as configured (for later):
	    Uc_ini_1 = Uc_ini_2 = None
	    if PSU1.CONFIGURED: Uc_ini_1 = PSU1.TEST_VIDLE
	    if PSU2.CONFIGURED: Uc_ini_2 = PSU2.TEST_VIDLE

	    # run the test/measurements (loop until done):
	    do_run = True
	    while do_run:

		    # Ask if okay to start the test
		    input ('\nReady for testing of ' + samplename + '? Press ENTER to start testing or CTRL+C to abort...')

		    # Print header / column labels:
		    printit('* Sample: ' + samplename,logfile,'%', terminal_output=False)
		    printit('* Date / time: ' + str(datetime.datetime.now()),logfile,'%', terminal_output=False)
		    printit (R2CTL_txt,logfile,'%', terminal_output=False)
		    if quick_mode:
			    printit ('* Running in quick mode (pre-heating only, no curve tracing)',logfile,'%', terminal_output=False)
		    else:
			    printit ('Column 1:  PSU1 nominal voltage setting (V)',logfile,'%', terminal_output=False)
			    printit ('Column 2:  PSU1 nominal current setting (A)',logfile,'%', terminal_output=False)
			    printit ('Column 3:  PSU1 voltage measurement (V)',logfile,'%', terminal_output=False)
			    printit ('Column 4:  PSU1 current measurement (I)',logfile,'%', terminal_output=False)
			    printit ('Column 5:  PSU1 limiter flag',logfile,'%', terminal_output=False)
			    printit ('Column 6:  PSU2 nominal voltage setting (V)',logfile,'%', terminal_output=False)
			    printit ('Column 7:  PSU2 nominal current setting (A)',logfile,'%', terminal_output=False)
			    printit ('Column 8:  PSU2 voltage measurement (V)',logfile,'%', terminal_output=False)
			    printit ('Column 9:  PSU2 current measurement (I)',logfile,'%', terminal_output=False)
			    printit ('Column 10: PSU2 limiter flag',logfile,'%', terminal_output=False)
			    printit ('Column 11: Heaterblock temperature (°C)',logfile,'%', terminal_output=False)
		    print ('\n')

		    # Make sure the heater is turned on (if possible/configured):
		    HEATER.turn_on()

		    # if heaterblock is configured and turned on:
		    # make sure the heaterblock temperature is within tolerance before configuring the measurement,
		    HEATER.wait_for_stable_T(DUT_PSU_allowed_turn_off=None, terminal_output=True)
		    
		    # turn on PSU outputs:
		    for p in [PSU1, PSU2]:
			    if p.CONFIGURED:
				    p.setCurrent(0,False)
				    p.setVoltage(p.VMIN,False)
				    p.turnOn()

		    # DUT break-in / pre-heat
		    if T_preheat > 0.0:
			    
			    logger.info('DUT break-in / pre-heat...')

			    # set idle conditions:
			    if TEMP_val != None:
				    do_TEMP_wait = True
			    else:
				    do_TEMP_wait = False
			    
			    # do idle/preheat:
			    do_idle(PSU1, PSU2, HEATER, T_preheat, file=logfile, wait_for_TEMP=do_TEMP_wait)

		    if not quick_mode:
			    logger.info('Curve tracing started...')

			    for V2 in V_steps[1]:
			    # outer loop (V2)

				    # get rid of numerical imprecisions (truncate values to voltage resolution of PSU):
				    # V2 = round(V2/PSU2.VRESSET) * PSU2.VRESSET

				    limit = 0 # number of CC events at a given step
				    limit_max = 2 # max. number of CC events before breaking from the loop


				    if PSU2.CONFIGURED:

					    # Determine PSU2 current limit (based on DUT limits):
					    if V2 > 0.0:
						    I2LIM = min (PSU2.TEST_ILIMIT,PSU2.TEST_PLIMIT/V2)
					    else:
						    I2LIM = PSU2.TEST_ILIMIT

					    # Check if current limit is within power capability of PSU2 (and adjust if necessary):
					    if (V2*I2LIM) > PSU2.PMAX:
						    I2LIM = PSU2.PMAX / V2
					    
					    # set PSU2 voltage + current:
					    PSU2.setCurrent(I2LIM,False)
					    PSU2.setVoltage(V2,True)

				    for V1 in V_steps[0]:
				    # inner loop (V1)

					    # get rid of numerical imprecisions (truncate values to voltage resolution of PSU):
					    # V1 = round(V1/PSU1.VRESSET) * PSU1.VRESSET

					    # init measurement values		
					    V1MEAS = []
					    I1MEAS = []
					    LIMIT1 = 0
					    V2MEAS = []
					    I2MEAS = []
					    LIMIT2 = 0
					    T_HB   = []

					    # measurement loop:
					    for i in range(N_rep):

						    # if heaterblock is configured and turned on:
						    # make sure the heaterblock temperature is within tolerance before doing the measurement,
						    # allow turning off the DUT to prevent (excessive) heat input from DUT to heaterblock
						    HEATER.wait_for_stable_T(DUT_PSU_allowed_turn_off=PSU1, terminal_output=True)
						    

						    # idle (if configured)
						    if T_idle > 0.0:
						        do_idle(PSU1,PSU2,HEATER,T_idle)
						        
						        # return to required PSU2 output:
						        if PSU2.CONFIGURED:
						            PSU2.setCurrent(I2LIM,False)
						            PSU2.setVoltage(V2,True)

						    # Determine PSU1 current limit:
						    if V1 > 0.0:
							    I1LIM = min (PSU1.TEST_ILIMIT,PSU1.TEST_PLIMIT/V1)
						    else:
							    I1LIM = PSU1.TEST_ILIMIT

						    # Check if current limit is within power capability of PSU1 (and adjust if necessary):
						    if (V1*I1LIM) > PSU1.PMAX:
							    I1LIM = PSU1.PMAX / V1

						    # set up PSU1 measurement conditions:
						    if PSU1.CONFIGURED:
							    PSU1.setCurrent(I1LIM,False) # set current limit at PSU1
							    PSU1.setVoltage(V1,True) # set voltage at PSU1

						    # read PSU output voltages and currents:
						    r = []
						    for p in [PSU1, PSU2]:
							    if p.CONFIGURED:
								    r.append(p.read(p.NSTABLEREADINGS))
							    else:
								    r.append([0.0,0.0,'NONE'])
						    
						    V1MEAS.append(r[0][0])
						    I1MEAS.append(r[0][1])
						    V2MEAS.append(r[1][0])
						    I2MEAS.append(r[1][1])
						    if r[0][2] == 'CC':
							    LIMIT1 = LIMIT1 + 1
						    if r[1][2] == 'CC':
							    LIMIT2 = LIMIT2 + 1

						    # Determine heaterblock temperature:
						    T_HB.append(HEATER.get_temperature())

					    # Determine median or mean of repeated readings:
					    if AVGFUNCTION == 'MEDIAN':
						    V1MEAS = np.median(V1MEAS)
						    I1MEAS = np.median(I1MEAS)
						    V2MEAS = np.median(V2MEAS)
						    I2MEAS = np.median(I2MEAS)
						    try:
							    T_HB   = np.median(T_HB)
						    except:
							    T_HB = None
							    pass
					    else:
						    V1MEAS = np.mean(V1MEAS)
						    I1MEAS = np.mean(I1MEAS)
						    V2MEAS = np.mean(V2MEAS)
						    I2MEAS = np.mean(I2MEAS)
						    try:
							    T_HB   = np.mean(T_HB)
						    except:
							    T_HB = None
							    pass
						    
					    # Check current limits (some PSUs are not very careful with this):
					    if I1MEAS > I1LIM:
						    LIMIT1 = 1
					    if I2MEAS > I2LIM:
						    LIMIT2 = 1

					    # Parse limiter flags:
					    if LIMIT1 > 0:
						    LIMIT1 = 1
					    else:
						    LIMIT1 = 0
					    if LIMIT2 > 0:
						    LIMIT2 = 1
					    else:
						    LIMIT2 = 0

					    # Check if current / power limit has been reached:
					    if (LIMIT1 == 0) and (LIMIT2 == 0):
						    limit = 0 # reset counter
					    else:
						    limit = limit + 1
						    if limit >= limit_max:
							    break # break out of the inner loop (V1 steps) and continue with the next V2 step

					    # send data to curve plotter thread:
					    u = [ V1*PSU1.TEST_POLARITY, I1LIM*PSU1.TEST_POLARITY, V1MEAS*PSU1.TEST_POLARITY, I1MEAS*PSU1.TEST_POLARITY, LIMIT1, V2*PSU2.TEST_POLARITY, I2LIM*PSU2.TEST_POLARITY, V2MEAS*PSU2.TEST_POLARITY, I2MEAS*PSU2.TEST_POLARITY, LIMIT2, T_HB ]
					    queue.put(u)
					    
					    # Print results to terminal:
					    try:
						    T_HB = "{:.2f}".format(T_HB)
					    except:
						    T_HB = "NA"
						    pass
					    
					    t =  format_PSU_reading(V1*PSU1.TEST_POLARITY, PSU1.VRESSET)      + ' ' + \
					         format_PSU_reading(I1LIM*PSU1.TEST_POLARITY, PSU1.IRESSET)   + ' ' + \
					         format_PSU_reading(V1MEAS*PSU1.TEST_POLARITY, PSU1.VRESREAD) + ' ' + \
					         format_PSU_reading(I1MEAS*PSU1.TEST_POLARITY, PSU1.IRESREAD) + ' ' + \
					         "{:1d}".format(LIMIT1)				          + ' ' + \
					         format_PSU_reading(V2*PSU2.TEST_POLARITY, PSU2.VRESSET)      + ' ' + \
					         format_PSU_reading(I2LIM*PSU2.TEST_POLARITY, PSU2.IRESSET)   + ' ' + \
					         format_PSU_reading(V2MEAS*PSU2.TEST_POLARITY, PSU2.VRESREAD) + ' ' + \
					         format_PSU_reading(I2MEAS*PSU2.TEST_POLARITY, PSU2.IRESREAD) + ' ' + \
					         "{:1d}".format(LIMIT2)                                       + ' ' + \
					         T_HB
					    printit(t, logfile )

			    logger.info('Curve tracing completed.')
			    
		    # Turn off PSUs:
		    for p in [PSU1, PSU2]:
			    if p.CONNECTED:
				    p.turnOff()
	    
		    if batch_mode:
		    
			    # prepare next step and file:
			    logfile, samplename, _, step = start_new_logfile(logger, batch_mode, basename, step+1)
			    
			    # reset initial values for idle conditions:
			    if PSU1.CONFIGURED: PSU1.TEST_VIDLE = Uc_ini_1
			    if PSU2.CONFIGURED: PSU2.TEST_VIDLE = Uc_ini_2
			    
			    # tell curve plotter to start new set of curves:
			    queue.put([])
			    
		    else:
			    do_run = False

    except KeyboardInterrupt:
	    logger.info('Caught keyboard interrupt, exiting...')
	    
    except Exception as e:
	    logger.warning('Oooops, something went wrong during testing: ' + repr(e))

    finally:
	    cleanup_exit(PSU1, PSU2, HEATER, queue, plt_proc)
