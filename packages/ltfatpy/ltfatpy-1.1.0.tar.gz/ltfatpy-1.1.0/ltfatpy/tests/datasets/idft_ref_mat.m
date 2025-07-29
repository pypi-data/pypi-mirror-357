function idft_ref_mat(filepath)
% Save the output of the idft function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/idft_ref.mat'];
disp(filename)

inputs_names = {'c', 'N', 'dim'};
sizes = {[8; 1], [13; 1], [16; 7; 9]};
N_val = {[7; 8; 9; 16], [8; 13; 16; 17], [6; 7; 16; 19]};
nb_outputs = 1;
outputs = cell(1, nb_outputs);
data = {};
inputs={};

for ind = 1:length(sizes)
    size = sizes{ind};
    inputs{1} = rand(size)+i*rand(size);
    for ind_N = 1:length(N_val{ind})
        inputs{2} = N_val{ind}(ind_N);    
        for dim = 1:(length(size)-1)
            inputs{3} = dim;
            [outputs{:}] = idft(inputs{:});
            inputs{3} = dim-1; % needed because Python dimensions start at 0
            data{end+1} = {inputs_names, inputs, outputs};
        end
    end
end



save(filename, 'data', '-V6');

end
