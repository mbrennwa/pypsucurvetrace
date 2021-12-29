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


###############
# plot curves #
###############

def plot_curves( data,
                 plot_type='U1I1U2',
                 exclude_CC = True,
                 x_reverse_neg = True,
                 y_reverse_neg = True,
                 linecolor = 'k',
                 linestyle = '-',
                 linewidth = 2.0,
                 gridcolor = 'gray',
                 grid_on = True,
                 fontname = None,
                 fontsize = None,
                 title=None,
                 xlabel='X DATA',
                 ylabel='Y DATA',
                 xlimit=None,
                 ylimit=None,
                 xscale=None,
                 yscale=None):

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

	# data scaling
	if xscale == 'mu':
		xscale = 'µ'
	if yscale == 'mu':
		yscale = 'µ'
	sc = { 'G': 9, 'M': 6, 'k': 3, 'm': -3, 'µ': -6, 'n': -9, 'p': -12, 'f': -15 }
	try:
		xsc = float(10**sc[xscale])
		xunit = xscale + xunit
	except:
		xsc = 1.0
	try:
		ysc = float(10**sc[yscale])
		yunit = yscale + yunit
	except:
		ysc = 1.0
	X = X / xsc
	Y = Y / ysc
	try:
		xlimit = xlimit / xsc
	except:
		pass
	try:
		ylimit = ylimit / ysc
	except:
		pass
		
	# prepare fonts:
	if fontname is None:
		fontname = 'Sans'
	if fontsize is None:
		fs_base = 18
	else:
		fs_base = fontsize
	fs_small = fs_small = 0.7*fs_base
	plt.rc('font', size=fs_base)
	plt.rc('font', family=fontname)
	
	# prepare line formats:
	lw_base = linewidth
	lw_thin = 0.5*lw_base
	plt.rc('lines', dash_joinstyle='round')
	plt.rc('lines', dash_capstyle='round')
	plt.rc('lines', solid_joinstyle='round')
	plt.rc('lines', solid_capstyle='round')
	
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
		
		plt.plot(x, y, color=linecolor, linestyle=linestyle, linewidth=lw_base)
		s = f'{CC[k]}'
		plt.text(x[-1], y[-1], s, fontsize=fs_small, bbox={'facecolor':'white','alpha':1,'edgecolor':'none','pad':1}, ha='center', va='center')

	# format the plot:
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
	ax = plt.gca()
	if grid_on:
		plt.grid(True, color=gridcolor, linewidth=lw_thin) 
		ax.tick_params(axis="x",length=0)
		ax.tick_params(axis="y",length=0)
	else:
		plt.grid(False) 
	

	for axis in ['top','bottom','left','right']:
		ax.spines[axis].set_linewidth(lw_base)
		ax.spines[axis].set_capstyle('round')
