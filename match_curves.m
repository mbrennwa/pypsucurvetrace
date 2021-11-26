function delta = match_curves_V1V2_I1 (f)

% function delta = match_curves_V1V2_I1 (f)

% check input:
if ~iscellstr(f)
	error ('Input needs to be cell string of data file names.')
end
if length(f) < 2
	error ('Input needs at least two data files.')
end

% load data and combine into single data set:
N = length(f);
x = {};
for i = 1:N
	x{i} = load(f{i});
	
	% remove values with current limiter on:
	k = find (x{i}(:,5) == 0); x{i} = x{i}(k,:);
end

% determine squared residuals between curves:
delta = repmat (NA, N, N);

for i = 1:N for j = i:N
	delta(i,j) = ...squared residual between x{i} and x{j}...
end end
