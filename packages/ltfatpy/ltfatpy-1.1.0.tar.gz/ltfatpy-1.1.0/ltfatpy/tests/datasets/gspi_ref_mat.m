function gspi_ref_mat(filepath)
% Save the output of the gspi function into a .mat file

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/gspi_ref.mat'];
disp(filename)

inputs_names = {};
inputs = {};
nb_outputs = 2;
outputs = cell(1, nb_outputs);
[outputs{:}] = gspi(inputs{:});

data = {{inputs_names, inputs, outputs}};

save(filename, 'data', '-V6');

end