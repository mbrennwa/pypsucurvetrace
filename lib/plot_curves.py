"""
Function to plot PyPSUcurvetrace data
"""

# imports:
# import traceback
# import time
# import math
# import datetime
# import configparser
# import argparse
import numpy as np
# import os.path
import matplotlib.pyplot as plt

FONTSIZE_NORMAL = 18
FONTSIZE_SMALL = 12
plt.rc('font', size=18)          # controls default text sizes

###############
# plot curves #
###############

def plot_curves( data,
                 plot_type='U1I1U2',
                 linecolor = 'k',
                 exclude_CC = True,
                 x_reverse_neg = True,
                 y_reverse_neg = True,
                 title=None,
                 xlabel='X DATA',
                 ylabel='Y DATA'):

	# filter data with current limiters off:
	if exclude_CC:
		k = np.where( data[:,4]+data[:,9] == 0)
		data = data[k]

	# number of measurement points:
	N = len(data[:,1])

	# parse data for plot:
	if plot_type == 'U1I1U2':
		print('Plot type: X = U1, Y = I1, C = U2')
		X = data[:,2] # measured U1 value
		Y = data[:,3] # measured I1 value
		C = data[:,5] # U2 set value
		if xlabel is None:
			xlabel = 'U1'
		if ylabel is None:
			ylabel = 'I1'
		xunit = 'V'
		yunit = 'A'
		
	else:
		print('Plot type ' + plot_type + ' not supported.')
		sys.exit()


	# plot every single curve:
	CC = np.unique(C)
	for k in range(len(CC)):
		kk = np.where(C == CC[k])
		x = X[kk]
		y = Y[kk]
		plt.plot(x, y,'r-')
		s = f'{CC[k]}'
		plt.text(x[-1], y[-1], s, fontsize=FONTSIZE_SMALL, bbox={'facecolor':'white','alpha':1,'edgecolor':'none','pad':1}, ha='center', va='center')

	if x_reverse_neg:
		r = plt.gca().axes.get_xlim()
		if abs(r[0]) > abs(r[1]):
			plt.gca().invert_xaxis()
	if y_reverse_neg:
		r = plt.gca().axes.get_ylim()
		if abs(r[0]) > abs(r[1]):
			plt.gca().invert_yaxis()
	
	plt.title(title)
	plt.xlabel(xlabel + '('+xunit+')')
	plt.ylabel(ylabel + '('+yunit+')')
	plt.grid()
