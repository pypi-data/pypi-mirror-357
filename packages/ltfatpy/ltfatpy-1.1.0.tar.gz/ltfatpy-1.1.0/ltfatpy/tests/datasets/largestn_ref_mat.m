function largestn_ref_mat(filepath)
% Save the output of the largestn function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/largestn_ref.mat'];
disp(filename)

inputs_names = {'xi', 'N', 'thresh_type'};
xi = [0., 0.1, 0.4; 0.5, 0.8, 1.];
N = 3;
thresh_types = {'hard', 'wiener', 'soft'};

nb_outputs = 2;
outputs = cell(1, nb_outputs);

data = {};

for ind_thresh_type = 1:length(thresh_types)
    thresh_type = thresh_types{ind_thresh_type};
    inputs = {xi, N, thresh_type};
    [outputs{:}] = largestn(inputs{:});
    data{end+1} = {inputs_names, inputs, outputs};
end

N = -1;
thresh_type = 'hard';
inputs = {xi, N, thresh_type};
[outputs{:}] = largestn(inputs{:});
data{end+1} = {inputs_names, inputs, outputs};

save(filename, 'data', '-V6');

end
