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
                 linestyle = '-',
                 exclude_CC = True,
                 x_reverse_neg = True,
                 y_reverse_neg = True,
                 title=None,
                 xlabel='X DATA',
                 ylabel='Y DATA',
                 xlimit=None,
                 ylimit=None):

	# parse data for plot:
	if plot_type == 'U1I1U2':
		print('Plot type: X = U1, Y = I1, C = U2')
		X = data.get_U1_meas(exclude_CC) # measured U1 value
		Y = data.get_I1_meas(exclude_CC) # measured I1 value
		C = data.get_U2_set(exclude_CC)  # U2 set value
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
		
		if xlimit is not None:
			kk = np.where(abs(x) < abs(xlimit))[0]
			if kk[-1] < len(x)-1:
				yend = np.interp(xlimit, x[[kk[-1],kk[-1]+1]], y[[kk[-1],kk[-1]+1]])
				x = np.append(x[kk], xlimit)
				y = np.append(y[kk], yend)
		if ylimit is not None:
			kk = np.where(abs(y) < abs(ylimit))[0]
			if kk[-1] < len(y)-1:
				xend = np.interp(ylimit, y[[kk[-1],kk[-1]+1]], x[[kk[-1],kk[-1]+1]])
				x = np.append(x[kk], xend)
				y = np.append(y[kk], ylimit)
		
		plt.plot(x, y, color=linecolor, linestyle=linestyle)
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
	plt.xlabel(xlabel + ' ('+xunit+')')
	plt.ylabel(ylabel + ' ('+yunit+')')
	plt.grid()
