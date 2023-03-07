#!/usr/bin/env python3

import sys
sys.path.append( '../../src' )

from numpy import meshgrid, linspace, nan, where, copy
from scipy.interpolate import griddata

import matplotlib.pyplot as plt

from pypsucurvetrace.read_datafile import read_datafile

def u2_surface(U1, I1, U2, u1, i1):
    # determine the 2D surface representing the function u2 = f(u1,i1) at the grid points defined by (u1,i1)
    uu1, ii1 = meshgrid(u1,i1)
    uu2 = griddata((U1, I1), U2, (uu1, ii1), method='linear')
    return uu1, ii1, uu2


# read data files:
d1, l1, p1, r1 = read_datafile('curvematch_plot_DUT1.dat')
d2, l2, p2, r2 = read_datafile('curvematch_plot_DUT2.dat')

# get curve data:
cU1_1 = d1.get_U1_meas(exclude_CC = True)
cI1_1 = d1.get_I1_meas(exclude_CC = True)
cU2_1 = d1.get_U2_set(exclude_CC = True)
cU1_2 = d2.get_U1_meas(exclude_CC = True)
cI1_2 = d2.get_I1_meas(exclude_CC = True)
cU2_2 = d2.get_U2_set(exclude_CC = True)

# determine u1 and i1 interpolation grid coordinates:
u1 = linspace(5.0, 30.0, num=200, endpoint=True)
i1 = linspace(0.5, 1.8,  num=200, endpoint=True)

# calculate x2 = f(u1,i1) surfaces (interpolation):
uu1_1, ii1_1, uu2_1 = u2_surface(cU1_1, cI1_1, cU2_1, u1, i1)
uu1_2, ii1_2, uu2_2 = u2_surface(cU1_2, cI1_2, cU2_2, u1, i1)

uu2_delta = uu2_2-uu2_1

up  = where(uu2_delta >= 0)
dwn = where(uu2_delta <= 0)

uu2_1_up  = copy(uu2_1)
uu2_1_dwn = copy(uu2_1)
uu2_2_up  = copy(uu2_2)
uu2_2_dwn = copy(uu2_2)
uu2_1_up[up] = nan
uu2_1_dwn[dwn] = nan
uu2_2_up[dwn] = nan
uu2_2_dwn[up] = nan

# plot surfaces:
fig = plt.figure(figsize=(6,5))
ax = fig.add_subplot(111, projection='3d')

alph = 0.7
col1 = [1,0,0]
col2 = [0,0,1]

surf1_up  = ax.plot_surface(uu1_1, ii1_1, uu2_1_up, color=col1, alpha=alph)
surf1_dwn = ax.plot_surface(uu1_1, ii1_1, uu2_1_dwn, color=col1, alpha=alph, linewidth=0, antialiased=True)
surf2_up  = ax.plot_surface(uu1_2, ii1_2, uu2_2_up, color=col2, alpha=alph, linewidth=0, antialiased=True)
surf2_dwn = ax.plot_surface(uu1_2, ii1_2, uu2_2_dwn, color=col2, alpha=alph, linewidth=0, antialiased=True)

ax.view_init(180+20, 40)

ax.set_xlabel('Drain-Source Voltage $U_1$ (V)')
ax.set_ylabel('Drain Current $I_1$ (A)')
ax.set_zlabel('Gate Voltage $U_2$ (V)')

fig.savefig('curvematch_surfaces.png', dpi=200, bbox_inches="tight", pad_inches=0.3)

plt.show()

