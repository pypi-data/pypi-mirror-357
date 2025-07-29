function phaselock_ref_mat(filepath)
% Save the output of the phaselock function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/phaselock_ref.mat'];
disp(filename)

data = {};

inputs_names = {'c', 'a'};
inputs = {ones(3), 1};
nb_outputs = 1;
outputs = cell(1, nb_outputs);
[outputs{:}] = phaselock(inputs{:});
data{end+1} = {inputs_names, inputs, outputs};

inputs = {ones(3, 3, 2), 1};
[outputs{:}] = phaselock(inputs{:});
data{end+1} = {inputs_names, inputs, outputs};

save(filename, 'data', '-V6');

end
