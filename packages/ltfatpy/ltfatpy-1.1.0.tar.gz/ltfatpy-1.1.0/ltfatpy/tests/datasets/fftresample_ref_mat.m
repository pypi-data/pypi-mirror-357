function fftresample_ref_mat(filepath)
% Save the output of the fftresample function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/fftresample_ref.mat'];
disp(filename)

L_val = [7, 8, 9];
data_types = {'real', 'complex'};
inputs_names = {'f', 'L'};
nb_outputs = 1;

data = {};

for ind_type = 1:length(data_types)
    inputs={};
    outputs = cell(1, nb_outputs);
    if strcmp(data_types{ind_type}, 'real')
        inputs{1} = (0:5);
    elseif strcmp(data_types{ind_type}, 'complex')
        inputs{1} = (0:5) + i*(5:-1:0);
    end
    for ind_L = 1:length(L_val)
       inputs{2} = L_val(ind_L);
       [outputs{:}] = fftresample(inputs{:});
       data{end+1} = {inputs_names, inputs, outputs};
    end
end

save(filename, 'data', '-V6');

end
