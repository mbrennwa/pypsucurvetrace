% GNU Octave m-file to plot curve traces

x = load('IRFP150_EXAMPLE.dat');
k = find (x(:,5) == 0); x = x(k,:); % remove values with current limiter on

VG = unique(x(:,6));

for i = 1:length(VG)
	k = find (x(:,6) == VG(i))
	V = [0 ; x(k,3)];
	I = [0 ; x(k,4)];
	plot (V,I,sprintf('-;V_{GS} = %.3g V;',VG(i)),'marker','.','markersize',12);
	hold on
end
hold off

xlabel ('V_{DS} (V)')
ylabel ('I_D (A)')
legend('location','northeastoutside');
