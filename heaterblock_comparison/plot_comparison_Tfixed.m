clear all; close all;

graphics_toolkit ('fltk')

h30 = plot_curves_V1I1V2 ('IRFP150_T30_15V.dat'); hold on
h50 = plot_curves_V1I1V2 ('IRFP150_T50_15V.dat');
h70 = plot_curves_V1I1V2 ('IRFP150_T70_15V.dat'); hold off

lw = 2;

set(h30,'linewidth',lw, 'marker','none', 'color','k');
set(h50,'linewidth',lw, 'marker','none', 'color','b');
set(h70,'linewidth',lw, 'marker','none', 'color','r');

legend('off');

grid on

axis([0 15 0 12]);
t = title("IRFP150 at 30\\circ  C (black), 50\\circ  C (blue), and 70\\circ  C (red)\n\nV_{GS} steps = 0.2 V", 'fontsize',22 );
xlabel('Drain-Source Voltage (V)'); ylabel('Drain Current (A)');
h = 10; v = 10;
set( gca , 'linewidth',lw , 'position',[0.15 0.2 0.8 0.65] )
set( gcf , 'paperposition',[0 0 h v] , 'papersize',[h v])
print('IRFP150_heaterblock.pdf')
print('IRFP150_heaterblock.png')
