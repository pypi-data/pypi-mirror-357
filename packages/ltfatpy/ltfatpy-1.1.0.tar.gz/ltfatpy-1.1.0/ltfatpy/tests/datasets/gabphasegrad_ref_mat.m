function gabphasegrad_ref_mat(filepath)
% Save the output of the gabphasegrad function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/gabphasegrad_ref.mat'];
disp(filename)

data = {};

method = 'dgt';
nb_outputs = 3;
outputs = cell(1, nb_outputs);

inputs_names = {'method', 'f', 'g', 'a', 'M'};
inputs = {method, (0:3).', 'gauss', 2, 3};
[outputs{:}] = gabphasegrad(inputs{:});
data{end+1} = {inputs_names, inputs, outputs};

inputs = {method, [(0:3).', (0:3).'], 'gauss', 2, 3};
[outputs{:}] = gabphasegrad(inputs{:});
data{end+1} = {inputs_names, inputs, outputs};

inputs_names = {'method', 'f', 'g', 'a', 'M', 'minlvl'};
inputs = {method, (0:3).', 'gauss', 2, 3, 0.1};
[outputs{:}] = gabphasegrad(inputs{1:5}, [], inputs{end});
data{end+1} = {inputs_names, inputs, outputs};

inputs_names = {'method', 'f', 'g', 'a', 'M'};
inputs = {method, (0:3).', (4:7)', 2, 3};
[outputs{:}] = gabphasegrad(inputs{:});
data{end+1} = {inputs_names, inputs, outputs};

method = 'phase';
nb_outputs = 2;
outputs = cell(1, nb_outputs);

inputs_names = {'method', 'cphase', 'a'};
inputs = {method, [0., 1., 2.; 3., 4., 5.; 6., 7., 8.], 2};
[outputs{:}] = gabphasegrad(inputs{:});
data{end+1} = {inputs_names, inputs, outputs};

inputs = {method, repmat([0., 1., 2.; 3., 4., 5.; 6., 7., 8.], 1, 1, 2), 2};
[outputs{:}] = gabphasegrad(inputs{:});
data{end+1} = {inputs_names, inputs, outputs};

method = 'abs';
nb_outputs = 2;
outputs = cell(1, nb_outputs);

inputs_names = {'method', 's', 'g', 'a'};
inputs = {method, [0., 1., 2.; 3., 4., 5.; 6., 7., 8.], 'gauss', 2};
[outputs{:}] = gabphasegrad(inputs{:});
data{end+1} = {inputs_names, inputs, outputs};

inputs = {method, repmat([0., 1., 2.; 3., 4., 5.; 6., 7., 8.], 1, 1, 2), ...
          'gauss', 2};
[outputs{:}] = gabphasegrad(inputs{:});
data{end+1} = {inputs_names, inputs, outputs};

inputs_names = {'method', 's', 'g', 'a', 'difforder'};
inputs = {method, [0., 1., 2.; 3., 4., 5.; 6., 7., 8.], 'gauss', 2, 2};
[outputs{:}] = gabphasegrad(inputs{:});
data{end+1} = {inputs_names, inputs, outputs};

save(filename, 'data', '-V6');

end
