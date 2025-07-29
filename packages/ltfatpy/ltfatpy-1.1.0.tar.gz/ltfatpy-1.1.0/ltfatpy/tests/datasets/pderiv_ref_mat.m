function pderiv_ref_mat(filepath)
% Save the output of the pderiv function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/pderiv_ref.mat'];
disp(filename)

difforders = [2, 4, inf];

inputs_names = {'f', 'difforder'};
nb_outputs = 1;

f = [0:5].';
data = {};
dim = 1;
for ind_difforder = 1:length(difforders)
    difforder =difforders(ind_difforder);
    outputs = cell(1, nb_outputs);
    [outputs{:}] = pderiv(f, dim, difforder);
    inputs = {f, difforder};
    data{end+1} = {inputs_names, inputs, outputs};
end

save(filename, 'data', '-V6');

end
