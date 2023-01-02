"""
Function to plot PyPSUcurvetrace data
"""

# imports:
import numpy as np
import matplotlib.pyplot as plt
import logging
from queue import Empty

from lib.read_datafile import measurement_data

# set up logger:
logger = logging.getLogger('plot_curves')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


###############
# plot curves #
###############

def plot_curves( data,			# measurement_data object (or tuple of measurement_data objects)
                 plot_type='U1I1U2',    # type of curve plot
                 bjt_r2 = None,         # R2CONTROL value for BJT U2 conversion
                 bjt_vbe = None,        # BJT VBE-on voltage
                 exclude_CC = True,     # exclude data with current limiter on
                 x_reverse_neg = True,  # reverse x axis for "negative" DUTs
                 y_reverse_neg = True,  # reverse y axis for "negative" DUTs
                 linecolor = 'k',       # line color of the curves (or tuple of line colors)
                 linestyle = '-',       # line style of the curves (or tuple of line colors)
                 linewidth = 2.0,       # line width of the curves (or tuple of line colors)
                 grid_on = True,        # use grid lines
                 gridcolor = 'gray',    # color of the grid lines
                 fontname = None,       # name of the font used in the plot
                 fontsize = None,       # size of the font used in the plot (base value)
                 title=None,            # plot title
                 xlabel=None,           # x-axis label
                 ylabel=None,           # y-axis label
                 xlimit=None,           # x-axis data limit (absolute value)
                 xylimit=None,          # x*y data limit (absolute value)
                 ylimit=None,           # y-axis data limit (absolute value)
                 xscale=None,           # x-axis multiplier prefix (G, M, k, m, µ, n, p, f)
                 yscale=None,           # y-axis multiplier prefix (G, M, k, m, µ, n, p, f)
                 cscale=None,           # curve multiplier prefix (G, M, k, m, µ, n, p, f)
                 nobranding=False       # do not add PyPSUcurvetrace "branding" to the plot
                ):

	if type(data) is not tuple:
		data = (data,)
	if type(linecolor) is not tuple:
		linecolor = tuple(linecolor)
	if type(linestyle) is not tuple:
		linestyle = tuple(linestyle)

	if len(linecolor) != len(data):
		logger.error('ERROR: number of linecolors (' + str(len(linecolor)) + ') does not match number of datafiles (' + str(len(data)) + ') !')
		return

	if len(linestyle) != len(data):
		logger.error('ERROR: number of linestyles (' + str(len(linestyle)) + ') does not match number of datafiles (' + str(len(data)) + ') !')
		return

	# data scaling
	if xscale == 'mu':
		xscale = 'µ'
	if yscale == 'mu':
		yscale = 'µ'
	sc = { 'G': 9, 'M': 6, 'k': 3, 'm': -3, 'µ': -6, 'n': -9, 'p': -12, 'f': -15 }
	try:
		xsc = float(10**sc[xscale])
		xunitprfix = xscale
	except:
		xsc = 1.0
		xunitprfix = ''		
	try:
		ysc = float(10**sc[yscale])
		yunitprfix = yscale
	except:
		ysc = 1.0
		yunitprfix = ''
	try:
		csc = float(10**sc[cscale])
		cunitprfix = cscale
	except:
		csc = 1.0
		cunitprfix = ''
	try:
		xlimit = xlimit / xsc
	except:
		pass
	try:
		ylimit = ylimit / ysc
	except:
		pass
	try:
		xylimit = abs(xylimit) / xsc / ysc
	except:
		pass

	# parse data for plot:
	X = Y = C = tuple( ) # init empty tuples
	
	if plot_type == 'U1I1U2': # Plot type: X = U1, Y = I1, C = U2
	
		for i in range(len(data)):
			# append tuple elements:
			X += (data[i].get_U1_meas(exclude_CC)/xsc,) # measured U1 value
			Y += (data[i].get_I1_meas(exclude_CC)/ysc,) # measured I1 value
			u = data[i].get_U2_set(exclude_CC) # U2 set value
			if bjt_vbe is not None:
			    if bjt_r2 is not None:
			        try:
			            u = (u-bjt_vbe) / bjt_r2
			        except:
			            print('could not convert PSU-U2 to BJT base current.')
			C += (u/csc,)

		if xlabel is None:
			xlabel = 'U1'
		if ylabel is None:
			ylabel = 'I1'
		xunit = xunitprfix + 'V'
		yunit = yunitprfix + 'A'
		if bjt_vbe is not None:
		    if bjt_r2 is not None:
		        cunit = 'A'
		else:
		    cunit = 'V'
		cunit = cunitprfix + cunit
		
	else:
		logger.error('Plot type ' + plot_type + ' not supported.')
		return

	# prepare fonts:
	if fontname is None:
		fontname = 'Sans'
	if fontsize is None:
		fs_base = 18
	else:
		fs_base = fontsize
	fs_small = 0.7*fs_base
	plt.rc('font', size=fs_base)
	plt.rc('font', family=fontname)
	
	# prepare line formats:
	lw_base = linewidth
	lw_thin = 0.5*lw_base
	plt.rc('lines', dash_joinstyle='round')
	plt.rc('lines', dash_capstyle='round')
	plt.rc('lines', solid_joinstyle='round')
	plt.rc('lines', solid_capstyle='round')
	
	# init tuples to deal with curve labels:
	s = xl = yl = dx = dy = xx = yy = tuple( )
	
	has_curve_labels = False
	
	# plot curves, loop over all data files:
	for i in reversed(range(len(data))):
	
		XX = X[i]
		YY = Y[i]
		CC = C[i]
		C0 = np.unique(CC)
		
		# loop over all curve lines:
		for k in range(len(C0)):
			
			kk = np.where(CC == C0[k])[0]
			
			if len(kk) < 2:
				if data[i].datafile is not None:
					# warn only if plotting data from file (not during live plotting)
					logger.warning('Not enough data for plotting curve at ' + str(C0[k]) + ' ' + cunit + ' (' + data[i].datafile + ')' + '. Skipping...')
				continue # skip to next curve
			
			x = XX[kk]
			y = YY[kk]
			
			if xlimit is not None:
				kk = np.where(abs(x) < abs(xlimit))[0]
				if not kk.any():
					continue # skip this curve, continue to the next curve
				if kk[-1] < len(x)-1:
					xlimit = np.sign(x[kk[-1]]) * abs(xlimit) # make sure polarity is right
					yend = np.interp(xlimit, x[[kk[-1],kk[-1]+1]], y[[kk[-1],kk[-1]+1]])
					x = np.append(x[kk], xlimit)
					y = np.append(y[kk], yend)
					
			if ylimit is not None:
				kk = np.where(abs(y) < abs(ylimit))[0]
				if not kk.any():
					continue # skip this curve, continue to the next curve
				if kk[-1] < len(y)-1:
					ylimit = np.sign(y[kk[-1]]) * abs(ylimit) # make sure polarity is right
					xend = np.interp(ylimit, y[[kk[-1],kk[-1]+1]], x[[kk[-1],kk[-1]+1]])
					x = np.append(x[kk], xend)
					y = np.append(y[kk], ylimit)
					
			if xylimit is not None:
				kk = np.where(abs(x*y) < xylimit)[0]
				if not kk.any():
					continue # skip this curve, continue to the next curve
				if kk[-1]+1 < len(y):
					xi  = np.linspace(x[kk[-1]],x[kk[-1]+1],1000);
					yi  = np.linspace(y[kk[-1]],y[kk[-1]+1],1000);
					xyi = xi*yi
					k0 = np.argmin(abs(xyi-xylimit))
					x = x[kk]
					y = y[kk]
					if xi[k0] != x[-1]:
						x = np.append(x, xi[k0])
						y = np.append(y, yi[k0])
			
			plt.plot(x, y, color=linecolor[i], linestyle=linestyle[i], linewidth=lw_base)
			
			# determine curve label things (only for first datafile):
			if i > 0:
				has_curve_labels = False
			else:

				# determine label string:
				s += (f'{round(10000000.0*C0[k])/10000000.0} ' + cunit, )
				
				# last curve point for label coordinates:
				xl += (x[-1],)
				yl += (y[-1],)

				# curve slope:
				dx += (x[-1] - x[-2], )
				dy += (y[-1] - y[-2], )
				
				has_curve_labels = True
	
	# format the plot (once all data plotting is done, so that coordinate systems do not changed anymore)

	ax = plt.gca() # get plot axes

	if has_curve_labels:
		
		# add curve labels (after plotting all curves, otherwise coordinate scaling gets screwed up):
		for i in range(len(s)):
		
			# draw label centered on endpoint of each curve:
			lbl = plt.text( xl[i], yl[i], s[i],
					fontsize=fs_small,
					bbox={'facecolor':'white','alpha':1,'edgecolor':'none','pad':0.0},
					ha='center', va='center'
				      )
			
			# determine size of the text label:
			plt.gcf().canvas.draw() # need to actually draw the label to get the dimensions
			b = lbl.get_window_extent().transformed(plt.gca().transData.inverted())
			w = 1.5 * b.width
			h = 1.5 * b.height
					
			# extrapolate curve line and determine new label position (xl,yl)
			if dx[i] == 0:
				# curve is vertical
				x = xl[i]
				y = yl[i] + np.sign(dy[i])*h/2
			elif abs(dy[i]/dx[i]) >= h/w:
				# curve is steeper than diagonals of text box
				x = xl[i] + np.sign(dx[i]) * dx[i]/dy[i] * h/2
				y = yl[i] + np.sign(dy[i]) * h/2
			else:
				# curve is flatter than diagonals of text box
				x = xl[i] + np.sign(dx[i]) * w/2
				y = yl[i] + np.sign(dy[i]) * dy[i]/dx[i] * w/2
			
			# move the text label to the new position to avoid overlap with the curve data:
			lbl.set_position((x, y))
			
			# keep track of x and y extent of text labels:
			xx += (x-w/2, x+w/1.5, )
			yy += (y-h/2, y+h/1.5, )
		
		# make sure text labels are within axes ranges:
		r = ax.get_xlim()
		ax.set_xlim([ min([min(xx), r[0]]), max([max(xx), r[1]]) ])
		r = ax.get_ylim()
		ax.set_ylim([ min([min(yy), r[0]]), max([max(yy), r[1]]) ])
		
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
	if grid_on:
		plt.grid(True, color=gridcolor, linewidth=lw_thin) 
		ax.tick_params(axis="x",length=0)
		ax.tick_params(axis="y",length=0)
	else:
		plt.grid(False) 
	
	for axis in ['top','bottom','left','right']:
		ax.spines[axis].set_linewidth(lw_base)
		ax.spines[axis].set_capstyle('round')
	
	if not nobranding:
		r = ax.get_ylim()
		ax.set_ylim([r[0], r[0]+1.08*(r[1]-r[0])])
		plt.text( 0.98, 0.98,'PyPSUcurvetrace',
			  fontsize=fs_small,
			  bbox={'facecolor':'white','alpha':1,'edgecolor':'none','pad':1},
			  horizontalalignment='right', verticalalignment='top',
			  transform = ax.transAxes
			)
			
			
#########################
# curve plotter process #
#########################

def curve_plotter(queue):

	d1 = measurement_data(datafile=None) # init empty datafile objects
	d2 = measurement_data(datafile=None) # init empty datafile objects

	# set up plotting environment
	# fig = plt.figure()
	# plt.ion()
	# plt.show()

	while True:
		
		# get new data from the queue:
		try:
			queue_empty = False
			y = queue.get(block=False)
		except Empty:
			queue_empty = True
		
		if not queue_empty:
			# process new data:
			if y is None:
				# terminate the process:
				break
				
			if len(y) == 0:
				# move foreground to background, clear foreground:
				d2 = d1
				d1 = measurement_data(datafile=None) # init empty datafile objects
			
			else:
				# add new data:
				d1.add_data(y)

				# plot curves:			
				plt.clf()
				plot_curves((d1,d2), linecolor = ('r','gray',), linestyle = ('-', '-',) )
		
		# run the figure event loop to deal with updating the plot and stuff:
		plt.pause(0.1) 
		
	# close figure:
	plt.close()


