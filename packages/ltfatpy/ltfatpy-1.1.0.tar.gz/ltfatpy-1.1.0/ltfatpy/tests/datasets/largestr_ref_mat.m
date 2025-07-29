function largestr_ref_mat(filepath)
% Save the output of the largestr function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/largestr_ref.mat'];
disp(filename)

inputs_names = {'xi', 'p', 'thresh_type'};
xi = [0., 0.1, 0.4; 0.5, 0.8, 1.];
p = 0.5;
thresh_types = {'hard', 'wiener', 'soft'};

nb_outputs = 2;
outputs = cell(1, nb_outputs);

data = {};

for ind_thresh_type = 1:length(thresh_types)
    thresh_type = thresh_types{ind_thresh_type};
    inputs = {xi, p, thresh_type};
    [outputs{:}] = largestr(inputs{:});
    data{end+1} = {inputs_names, inputs, outputs};
end

save(filename, 'data', '-V6');

end
