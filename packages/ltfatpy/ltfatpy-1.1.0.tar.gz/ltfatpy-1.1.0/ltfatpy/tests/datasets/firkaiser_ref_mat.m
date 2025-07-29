function firkaiser_ref_mat(filepath)
% Save the output of the firkaiser function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/firkaiser_ref.mat'];
disp(filename)


inputs_names = {'L', 'beta', 'centering', 'stype'};
nb_outputs = 1;
outputs = cell(1, nb_outputs);

data = {};

beta = 0.5;
centerings = {'wp', 'hp'};
stypes = {'normal', 'derived'};

L_val = [6, 8];
for ind_L = 1:length(L_val)
    L = L_val(ind_L);
    for ind_centering = 1:length(centerings)
        centering = centerings{ind_centering};
        for ind_stype = 1:length(stypes) 
            stype = stypes{ind_stype};
            inputs = {L, beta, centering, stype};
            [outputs{:}] = firkaiser(inputs{:});
            data{end+1} = {inputs_names, inputs, outputs};
         end
     end
end

stype = 'normal';
L_val = [1, 7];
for ind_L = 1:length(L_val)
    L = L_val(ind_L);
    for ind_centering = 1:length(centerings)
        centering = centerings{ind_centering};
        inputs = {L, beta, centering, stype};
        [outputs{:}] = firkaiser(inputs{:});
        data{end+1} = {inputs_names, inputs, outputs};
     end
end
 
save(filename, 'data', '-V6');

end
