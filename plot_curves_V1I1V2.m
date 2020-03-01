function plot_curves_V1I1V2 (f)

% GNU Octave m-file to plot curves:
% x-axis: PSU-1 voltage (V1)
% y-axis: PSU-1 current (I1)
% one curve for each nominal PSU-2 voltage (V2)


x = load(f);
k = find (x(:,5) == 0); x = x(k,:); % remove values with current limiter on

VG = unique(x(:,6));

for i = 1:length(VG)
	k = find (x(:,6) == VG(i));
	V = [0 ; x(k,3)];
	I = [0 ; x(k,4)];
	plot (V,I,sprintf('-;V_2 = %.3g V;',VG(i)),'marker','.','markersize',12);
	hold on
end
hold off

if(median(x(:,3) < 0 ))
	set (gca,'xdir','reverse')
end

if(median(x(:,4) < 0 ))
	set (gca,'ydir','reverse')
end

xlabel ('V_1 (V)')
ylabel ('I_2 (A)')
legend('location','northeastoutside');
