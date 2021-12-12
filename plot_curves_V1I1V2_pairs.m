function h = plot_curves_V1I1V2_pairs (filespath, save_PDF)

% function h = plot_curves_V1I1V2_pairs (filespath, save_PDF)
%
% GNU Octave m-file to plot curve pairs from data file in filespath, using plot_curves_V1I1V2(...)
%
% INPUT:
% filespath: path of directory containing the data files (string)
% save_PDF: graphics are saved to PDF file in current working directory (boolean). If save_PDF = false, the program will interactively ask before plotting the next pair of curves.
%
% EXAMPLE (plot THF51 curve pairs and save to PDF files):
%
% >> graphics_toolkit ('fltk')
% >> plot_curves_V1I1V2_pairs('path/to/THF51_curves/', true);

if ~exist('save_PDF', 'var')
	save_PDF = false;
	warning('Did not specify save_PDF, assuming save_PDF=false.')
end

if filespath(end) != filesep
	filespath = [ filespath filesep ];
end
files = glob([ filespath '*.dat' ]);

N = numel(files);
k = 0; NN = (N^2+N)/2;
lw = 2; fs = 12;

figure();
	
for i=1:N
for j=i+1:N
	k = k+1;
	disp(sprintf('%i of %i: Loading and plotting data from files %s and %s...', k, NN, files{i}, files{j}))
	
	h1 = plot_curves_V1I1V2 (files{i}); hold on
	h2 = plot_curves_V1I1V2 (files{j}); hold off
	legend off;
	grid on;
	set(h1,'color','b','marker','none','linewidth',lw);
	set(h2,'color','r','marker','none','linewidth',lw);
	set(gca, 'linewidth', lw, 'fontsize',fs);
	[~, name1] = fileparts (files{i});
	[~, name2] = fileparts (files{j});
	title(sprintf('Blue: %s\n Red: %s',strrep(name1,'_','-'),strrep(name2,'_','-')));
	if save_PDF
		f = sprintf('%s_%s.pdf',name1,name2);
		disp(sprintf('Saving plot to %s...',f))
		width = 8; height = 5; set(gcf,'PaperUnits','inches','PaperOrientation','landscape','PaperSize',[width,height],'PaperPosition',[0,0,width,height]);
		print(f);
	else
		if (i < N) & (j < N)
			input('Press ENTER to continue...');
		end
	end
end
end

disp('Done!')
