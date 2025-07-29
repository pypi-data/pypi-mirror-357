function sgram_ref_mat(filepath)
% Save the output of the sgram function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/sgram_ref.mat'];
disp(filename)

data = {};

nb_outputs = 1;
outputs = cell(1, nb_outputs);

f = [1+3*i; 2+2*i; 3+1*i];
wlen = 2;
inputs_names = {'f', 'display', 'wlen'};
inputs = {f, '_bool_False_', wlen};
[outputs{:}] = sgram(f, 'nodisplay', 'wlen', wlen);
data{end+1} = {inputs_names, inputs, outputs};

f = (1:2).';
inputs_names = {'f', 'display'};
inputs = {f, '_bool_False_'};
[outputs{:}] = sgram(f, 'nodisplay');
data{end+1} = {inputs_names, inputs, outputs};

thr = 0.5;
inputs_names = {'f', 'display', 'thr'};
inputs = {f, '_bool_False_', thr};
[outputs{:}] = sgram(f, 'nodisplay', 'thr', thr);
data{end+1} = {inputs_names, inputs, outputs};

f = (1:3).';
inputs_names = {'f', 'display', 'nf'};
inputs = {f, '_bool_False_', '_bool_True_'};
[outputs{:}] = sgram(f, 'nodisplay', 'nf');
data{end+1} = {inputs_names, inputs, outputs};

f = (1:4).';
fmax = length(f) * 0.2;
inputs_names = {'f', 'display', 'fmax'};
inputs = {f, '_bool_False_', fmax};
[outputs{:}] = sgram(f, 'nodisplay', 'fmax', fmax);
data{end+1} = {inputs_names, inputs, outputs};

f = (1:4).';
fs = 1.;
fmax = 0.2;
inputs_names = {'f', 'display', 'fs', 'fmax'};
inputs = {f, '_bool_False_', fs, fmax};
[outputs{:}] = sgram(f, fs, 'nodisplay', 'fmax', fmax);
data{end+1} = {inputs_names, inputs, outputs};

save(filename, 'data', '-V6');

end
