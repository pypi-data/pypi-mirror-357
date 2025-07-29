function groupthresh_ref_mat(filepath)
% Save the output of the groupthresh function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/groupthresh_ref.mat'];
disp(filename)

inputs_names = {'xi', 'lamb', 'group_type', 'thresh_type'};
xi = [0., 0.2, 0.4; 0.6, 0.8, 1.];
lambs = [0.7, 2.];
thresh_types = {'hard', 'wiener', 'soft'};
group_types = {'group', 'elite'};

nb_outputs = 1;
outputs = cell(1, nb_outputs);

data = {};

for ind = 1:length(lambs)
    lamb = lambs(ind);
    group_type = group_types{ind};
    for ind_thresh_type = 1:length(thresh_types)
        thresh_type = thresh_types{ind_thresh_type};
        inputs = {xi, lamb, group_type, thresh_type};
        [outputs{:}] = groupthresh(inputs{:});
        data{end+1} = {inputs_names, inputs, outputs};
    end
end

lamb = 0.7;
group_type = 'group';
thresh_type = 'hard';
dim = 0;

inputs_names = {'xi', 'lamb', 'group_type', 'thresh_type', 'dim'};
inputs = {xi, lamb, group_type, thresh_type, dim};
[outputs{:}] = groupthresh(xi, lamb, dim+1, group_type, thresh_type);
data{end+1} = {inputs_names, inputs, outputs};

save(filename, 'data', '-V6');

end
