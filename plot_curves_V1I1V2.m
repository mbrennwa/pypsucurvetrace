function plot_curves_V1I1V2 (f)

% function plot_curves_V1I1V2 (f)
%
% GNU Octave m-file to plot curves from curvetrace data in file(s) f:
% - x-axis: PSU-1 voltage (V1)
% - y-axis: PSU-1 current (I1)
% - one curve for each nominal PSU-2 voltage (V2)
% - if more than one data file is given as input, the data from all files is combined into a single data set before plotting
%
% INPUT:
% f: string or cell string with the name(s) of the data file(s)

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
V2= unique(x(:,6));

for i = 1:length(V2)
	k = find (x(:,6) == V2(i));
	[V,j] = sort(x(k,3));
	I     = x(k,4)(j);
	if ~any(V == 0)
		[V,j] = sort([0;V])
		I = [0;V](j)
	end
	plot (V,I,sprintf('-;V_2 = %.3g V;',V2(i)),'marker','.','markersize',12);
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
