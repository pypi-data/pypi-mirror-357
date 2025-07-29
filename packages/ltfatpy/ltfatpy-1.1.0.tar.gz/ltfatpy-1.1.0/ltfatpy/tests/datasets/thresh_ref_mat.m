function thresh_ref_mat(filepath)
% Save the output of the thresh function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/thresh_ref.mat'];
disp(filename)

inputs_names = {'xi', 'lamb', 'thresh_type'};
xi = [0., 0.1, 0.4; 0.5, 0.8, 1.];
lambs = {0.5, [0.4, 0., 0.2; 0.6, 1., 1.], [0.4; 0.6; 0.; 1.; 0.2; 1.]};
thresh_types = {'hard', 'wiener', 'soft'};

nb_outputs = 2;
outputs = cell(1, nb_outputs);

data = {};

for ind_lamb = 1:length(lambs)
    lamb = lambs{ind_lamb};
    for ind_thresh_type = 1:length(thresh_types)
        thresh_type = thresh_types{ind_thresh_type};
        inputs = {xi, lamb, thresh_type};
        [outputs{:}] = thresh(inputs{:});
        data{end+1} = {inputs_names, inputs, outputs};
    end
end

save(filename, 'data', '-V6');

end
