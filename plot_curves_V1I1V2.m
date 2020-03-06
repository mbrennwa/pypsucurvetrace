function h = plot_curves_V1I1V2 (f)

% function h = plot_curves_V1I1V2 (f)
%
% GNU Octave m-file to plot curves from curvetrace data in file(s) f:
% - x-axis: PSU-1 voltage (V1)
% - y-axis: PSU-1 current (I1)
% - one curve for each nominal PSU-2 voltage (V2)
% - if more than one data file is given as input, the data from all files is combined into a single data set before plotting
%
% INPUT:
% f: string or cell string with the name(s) of the data file(s)
%
% EXAMPLE (plot 2SJ79 curves and save to PDF file):
%
% >> graphics_toolkit ('fltk')
% >> h = plot_curves_V1I1V2('examples/data/2SJ79.dat');
% >> set(h(:),'marker','none','linewidth',1.5); grid('on')
% >> legend('boxoff')
% >> l = get( get( gcf,'children' )(1) , 'string'); l = strrep( l , 'V_2','V_{GS}' ); l = strrep( l , ' V','.0 V' ); l = strrep( l , '.5.0','.0' ); set( get(gcf,'children')(1) , 'string',l , 'position',[0.85 0.1 0.1 0.8] )
% >> title ('2SJ79 FET'); xlabel('Drain-Source Voltage (V)'); ylabel('Drain Current (mA)');
% >> v = get(gca,'yticklabel'); for i = 1:length(v) v{i} = num2str(1000*str2num(v{i})); end
% >> set( gca , 'yticklabel',v , 'linewidth',1.5 , 'position',[0.1 0.1 0.7 0.8] )
% >> set( gcf , 'paperposition',[0 0 10 6] , 'papersize',[10 6])
% >> print('2SJ79.pdf')


% check input:
if ~iscellstr(f)
	f = {f};
end

% load data and combine into single data set:
x = [];
for i = 1:length(f)
	x = [ x ; load(f{i}) ];
end

% remove values with current limiter on:
k = find (x(:,5) == 0); x = x(k,:);

% find V2 values:
V2 = unique(x(:,6));

h = [];
for i = 1:length(V2)
	k = find (x(:,6) == V2(i));
	[u,j] = sort(abs(x(k,3)));
	V     = x(k,3)(j);
	I     = x(k,4)(j);
	if ~any(V == 0)
		V = [0;V];
		I = [0;I];
	end
	h = [ h plot(V,I,sprintf('-;V_2 = %.3g V;',V2(i)),'marker','.','markersize',12) ];
	hold on
end
hold off

if(mean(x(:,3) < 0 ))
	set (gca,'xdir','reverse')
end

if(mean(x(:,4) < 0 ))
	set (gca,'ydir','reverse')
end

title (f)
xlabel ('V_1 (V)')
ylabel ('I_1 (A)')
legend('location','northeastoutside');
