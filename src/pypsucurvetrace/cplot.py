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

import sys
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
### import tempfile

from pypsucurvetrace.read_datafile import read_datafile
from pypsucurvetrace.plot_curves import plot_curves
from pypsucurvetrace.curvetrace_tools import say_hello, get_logger

# set up logger:
logger = get_logger('curveplot')


if __name__ == "__main__":
    cplot()


def cplot():
    ################
    # main program #
    ################

    # input arguments:
    parser = argparse.ArgumentParser(description='curveplot is a Python program for plotting of pypsucurvetrace data.')
    parser.add_argument('datafiles', nargs='+', help='Names (and paths) of pypsucurvetrace data files. A list of multiple files can be used for an overlay plot. Files can also be specified using wildcards.')

    # plot type:
    parser.add_argument('--type', help='Plot type. Format: <X><Y><C>, where X is the x-axis parameter, Y is the y-axis parameter, and C is the curves parameter; parameters are U1, I1, U2, I2. Example: -type U1I1U2. Default (if not format is not specified): type = U1I1U2')

    # BJT option:
    parser.add_argument('--bjtvbe', help='BJT VBE-on voltage for conversion of PSU U2 voltage to base current using R2CONTROL from the data file: Ibase = (U2-BJTVBE)/R2CONTROL')

    # size of plot figure:
    parser.add_argument('--width', type=float, help='Width of the figure')
    parser.add_argument('--height', type=float, help='Height of the figure')

    # data limits:
    parser.add_argument('--xlimit', type=float, help='Max. x-axis value')
    parser.add_argument('--ylimit', type=float, help='Max. y-axis value')
    parser.add_argument('--xylimit', type=float, help='Max. x*y value')
    parser.add_argument('--xscale', help='x-axis multiplier prefix (G, M, k, m, mu, n, p, f)')
    parser.add_argument('--yscale', help='y-axis multiplier prefix (G, M, k, m, mu, n, p, f)')
    parser.add_argument('--cscale', help='curves multiplier prefix (G, M, k, m, mu, n, p, f)')

    parser.add_argument('--noclabels', action='store_true', help = 'plot without curve labels')

    # axis direction for "negative" parts:
    parser.add_argument('--xreverseneg', action='store_true', help='Do not reverse x-axis direction for negative DUTs')
    parser.add_argument('--yreverseneg', action='store_true', help='Do not reverse y-axis direction for negative DUTs')

    # log scale:
    parser.add_argument('--xlog', action='store_true', help='x-axis log scale')
    parser.add_argument('--ylog', action='store_true', help='y-axis log scale')

    # x/y data offset values:
    parser.add_argument('--xoffset', type=float, help='x-axis data offset')
    parser.add_argument('--yoffset', type=float, help='y-axis data offset')

    # plot absolute x/y values:
    parser.add_argument('--xabs', action='store_true', help='absolute x-axis values')
    parser.add_argument('--yabs', action='store_true', help='absolute y-axis values')
    
    # title / labels:
    parser.add_argument('--title', help='Plot title (see also --saveXYZ and --pairs options)')
    parser.add_argument('--xlabel', help='x-axis label')
    parser.add_argument('--ylabel', help='y-axis label')

    # line formats:
    parser.add_argument('--linecolor', help='Color of curves (any of the Matplotlib color specs)')
    parser.add_argument('--linestyle', help='Line style of curves (solid, dashed, dashdot, dotted)')
    parser.add_argument('--linewidth', type=float, help='Line width of curves and plot frame')
    parser.add_argument('--dotmarker', help='Symbol to use for data-point')

    # grid:
    parser.add_argument('--gridcolor', help='Grid line color')
    parser.add_argument('--nogrid', action='store_true', help='Turn off grid lines')

    # fonts:
    parser.add_argument('--builtinfontname', help='Name of built-in font (RoutedGothic, NationalPark, FreeSans)')
    parser.add_argument('--fontname', help='System font name (this may need clearing of the matplotlib font cache after installing new fonts to your system)')
    parser.add_argument('--fontsize', type=float, help='Font size')

    # logo / branding on/off:
    parser.add_argument('--nobranding', action='store_true', help='Hide pypsucurvetrace label')

    # matching tools:
    parser.add_argument('--pairs', action='store_true', help='Plot overlays of all dataset pairs in datafiles list (useful for parts matching). The plot title is determined from the datafile names.')
    parser.add_argument('--maxdeltaU2', type=float, help='Skip --pairs plotting if the Uc values from the prehead/idle are different by more than the specified value (ignored if used without --pairs)')

    # program flow:
    parser.add_argument('--savepdf', action='store_true', help='Save plot to PDF file. The filename is determined from the --title (if set) or from the datafile name(s). WARNING: existing files with the same name will be overwritten!')
    parser.add_argument('--savesvg', action='store_true', help='Save plot to SVG file (see also --savepdf)')
    parser.add_argument('--savepng', action='store_true', help='Save plot to PNG file (see also --savepdf)')
    parser.add_argument('--nodisplay', action='store_true', help='Do not show the figure(s) on screen, only save to file (this requires at lease one of the --saveXYZ options to be set)')

    # do not show a "hello" message
    parser.add_argument('--nohello', action='store_true', help='Do not print the hello / about message (useful when the output needs further processing).')

    # parse args:
    args = parser.parse_args()

    # Say Hello:
    if not args.nohello:
         say_hello('curveplot', 'Plotting of pypsucurvetrace data')

    # determine data file(s):
    datafiles = args.datafiles

    # matching:
    pairs = False
    maxdeltaU2 = None
    if args.pairs:
	    if len(datafiles) == 1:
		    logger.warning('Specified --pairs option with a single datafile, ignoring --pairs.')
	    else:
		    pairs = True
	    if args.maxdeltaU2:
		    maxdeltaU2 = args.maxdeltaU2
		    
    # program flow:
    savefig = False
    savePDF = False
    saveSVG = False
    savePNG = False
    if args.savepdf:
	    savefig = True
	    savePDF = True
    if args.savesvg:
	    savefig = True
	    saveSVG = True
    if args.savepng:
	    savefig = True
	    savePNG = True
    dodisplay = True
    if args.nodisplay:
	    if savefig:
		    dodisplay = False
	    else:
		    logger.warning('--saveXYZ not set, ignoring --nodisplay!')

    # determine plot type:
    plot_type = 'U1I1U2' # default
    if args.type:
	    plot_type = args.type.upper()

    # determine figure size:
    width = 10 # default
    height = 7 # default
    if args.width:
	    width = args.width
    if args.height:
	    height = args.height

    # determine data limits and scales:
    xlimit  = None # default
    ylimit  = None # default
    xylimit = None # default
    xscale  = None
    yscale  = None
    cscale  = None
    xreverseneg = True
    yreverseneg = True
    xlog = False
    ylog = False
    xabs = False
    yabs = False
    if args.xlimit:
	    xlimit = args.xlimit
    if args.ylimit:
	    ylimit = args.ylimit
    if args.xylimit:
	    xylimit = args.xylimit
    if args.xscale:
	    xscale = args.xscale
    if args.yscale:
	    yscale = args.yscale
    if args.cscale:
	    cscale = args.cscale
    if args.xreverseneg:
	    xreverseneg = False
    if args.yreverseneg:
	    yreverseneg = False
    if args.xlog:
	    xlog = True
    if args.ylog:
	    ylog = True
    if args.xabs:
	    xabs = True
    if args.yabs:
	    yabs = True

    # determine data x&y offsets:
    xoffset = 0.0 # default
    yoffset = 0.0 # default
    if args.xoffset:
	    xoffset = args.xoffset
    if args.yoffset:
	    yoffset = args.yoffset

    noclabels = False
    if args.noclabels:
	    noclabels = True

    # determine axis labels and plot title:
    xlabel = None # default
    ylabel = None # default
    title  = None # default
    if args.title:
	    title = args.title
    if args.xlabel:
	    xlabel = args.xlabel
    if args.ylabel:
	    ylabel = args.ylabel

    # determine line width:
    linewidth = 2.0 # default
    if args.linewidth:
	    linewidth = args.linewidth

    # determine line color:
    if len(datafiles) == 1:
	    linecolor = ('k',) # default
    else:
	    linecolor = plt.cm.rainbow(np.linspace(0, 1, len(datafiles)))

    if args.linecolor:
	    linecolor = (args.linecolor,)
    if args.linestyle:
	    linestyle = (args.linestyle,)
    if len(linecolor) < len(datafiles):
	    logger.warning('No linecolors specified, will use the same linecolor for all datafiles!')
	    u = tuple( )
	    for i in range(len(datafiles)):
		    u += (linecolor[0],)
	    linecolor = u 

    # determine line style:
    linestyle = ('solid',) # default
    if len(linestyle) < len(datafiles):
	    logger.warning('No linestyles specified, will use the same linestyle for all datafiles!')
	    u = tuple( )
	    for i in range(len(datafiles)):
		    u += (linestyle[0],)
	    linestyle = u 

    # marker dot symbol:
    dotmarker = None # default
    if args.dotmarker:
	    dotmarker = args.dotmarker
	    
    if len(linestyle) < len(datafiles):
	    logger.warning('No linestyles specified, will use the same linestyle for all datafiles!')
	    u = tuple( )
	    for i in range(len(datafiles)):
		    u += (linestyle[0],)
	    linestyle = u 

    # grid lines:
    grid_on = True
    gridcolor = 'lightgray'
    if args.nogrid:
	    grid_on = False
    if args.gridcolor:
	    gridcolor = args.gridcolor
	    
    # PyPSU branding label:
    nobranding = False
    if args.nobranding:
	    nobranding = True

    # BJT Vbe-on value:
    BJT_VBE = None # default
    if args.bjtvbe:
	    BJT_VBE = float(args.bjtvbe)

    # load data from files:
    data = label = preheat = ls = lc = tuple( )

    for i in range(len(datafiles)):
	    try:
		    d, l, p, r2ctl = read_datafile(datafiles[i])
		    
		    if len(d.rawdata) == 0:
			    logger.warning('datafile ' + datafiles[i] + ' contains no curve data. Skipping this file...')
		    else:
			    data    += (d,)
			    label   += (l,)
			    preheat += (p,)
			    ls      += (linestyle[i],)
			    lc      += (linecolor[i],)
	    except:
		    # could not read file (maybe the file does not exist, may happen if the datafiles list was created by some iterator loop that did not know enough)
		    logger.warning('Could not load data from ' + datafiles[i] + '. Skipping this file...')
		    continue # skip to next file
		    
    linestyle = ls
    linecolor = lc

    if len(data) == 0:
	    logger.info('No curve data for plotting.')
	    
    else:
	    # determine font size and name:
	    builtinfontname = None # built-in font name, default
	    fontname = None # system font name, default
	    fontsize = None # default
	    if args.builtinfontname:
		    builtinfontname = args.builtinfontname
	    if args.fontname:
		    fontname = args.fontname
	    if args.fontsize:
		    fontsize = args.fontsize

	    if pairs:
		    datapairs = tuple( )
		    for i in range(0,len(data)-1):
			    for j in range(i+1,len(data)):
				    do_add = False
				    if args.maxdeltaU2 is None:
					    do_add = True
				    else:
					    if abs(preheat[i].U2-preheat[j].U2) <= maxdeltaU2:
						    do_add = True
				    if do_add:
					    datapairs += ( ( data[i], data[j], ), )
		    datapairs = list(datapairs)
		    linecolor = [ 'r', 'b' ]
		    linestyle = [ 'solid', 'solid' ]
		    Nplots = len(datapairs)
	    else:
		    Nplots = 1

	    # matplotlib figure:
	    fig = plt.figure(figsize=(width, height))

	    # loop to deal with all plots:
	    for i in range(Nplots):
		    if pairs:
			    data = datapairs[i]
			    title = Path(data[0].datafile).stem + ' (red) vs. ' + Path(data[1].datafile).stem + ' (blue)'
		    
		    # plot title:
		    if title is None:
			    title = ''
			    for i in range(len(label)):
				    if i == 0:
					    title = label[0]
				    else:
					    title += ', ' + label[i]

		    # plot data:
		    try:
			    plot_curves( data      = data,
				         bjt_r2 = r2ctl,
				         bjt_vbe = BJT_VBE,
				         xlimit    = xlimit,
				         ylimit    = ylimit,
				         xylimit   = xylimit,
				         plot_type = plot_type,
				         linecolor = linecolor,
				         linestyle = linestyle,
				         linewidth = linewidth,
				         gridcolor = gridcolor,
				         dotmarker = dotmarker,
				         grid_on   = grid_on,
				         nobranding = nobranding,
				         title     = title,
				         xlabel    = xlabel,
				         ylabel    = ylabel,
				         xscale    = xscale,
				         yscale    = yscale,
				         cscale    = cscale,
				         noclabels = noclabels,
				         x_reverse_neg = xreverseneg,
				         y_reverse_neg = yreverseneg,
				         xlog      = xlog,
				         ylog      = ylog,
				         xoffset   = xoffset,
				         yoffset   = yoffset,
				         xabs      = xabs,
				         yabs      = yabs,
				         fontsize  = fontsize,
				         fontname  = fontname,
				         builtinfontname = builtinfontname)
		    except:
			    # plot failed for some reason, skip this plot and try the next one
			    continue
			    
		    if savefig:
		    
			    # determine filename:
			    if title is not None:
				    figname = title
			    else:
				    figname = ''
				    for dd in data:
					    figname += Path(dd.datafile).stem
			    specialChars = " %/,;.:\\*" 
			    for c in specialChars:
				    figname = figname.replace(c, '_')
			    for k in range(len(specialChars)):
				    figname = figname.replace('__', '_')
				    
			    if len(figname) > os.pathconf('/', 'PC_NAME_MAX')-4:
				    figname = figname[0:os.pathconf('/', 'PC_NAME_MAX')-4]
			    
			    # save figure file(s):		
			    if Nplots > 1:
				    nn = ' ' + str(i+1) + '/' + str(Nplots) + ' '
			    else:
				    nn = ' '
			    meta = {'Creator': 'pypsucurvetrace', 'Title': title}
			    f = tuple( )
			    if savePDF:
				    f += ( figname+'.pdf', )
			    if saveSVG:
				    f += ( figname+'.svg', )
			    if savePNG:
				    f += ( figname+'.png', )
			    for ff in f:

				    logger.info('Saving figure' + nn + 'to file ' + ff + '...')
				    fig.savefig(ff, metadata=meta)

		    if dodisplay:

			    if i < Nplots-1:
				    print('Close plot window for next plot...')
			    else:
				    print('Close plot window to exit.')

			    # Show the plot:
			    plt.show()
			    
		    # clear the figure (for the next plot in the loop)
		    plt.clf()
	    
	    # cleanup: close the plot after all plots are done
	    plt.close(fig)
