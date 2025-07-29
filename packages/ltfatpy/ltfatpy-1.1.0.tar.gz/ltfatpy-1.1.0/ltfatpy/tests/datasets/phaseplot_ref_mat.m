function phaseplot_ref_mat(filepath)
% Save the output of the phaseplot function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/phaseplot_ref.mat'];
disp(filename)

data = {};

f = (1:3).';
inputs_names = {'f', 'display'};
inputs = {f, '_bool_False_'};
nb_outputs = 1;
outputs = cell(1, nb_outputs);
[outputs{:}] = phaseplot(f, 'nodisplay');
data{end+1} = {inputs_names, inputs, outputs};

thr = 0.3;
inputs_names = {'f', 'display', 'thr'};
inputs = {f, '_bool_False_', thr};
[outputs{:}] = phaseplot(f, 'nodisplay', 'thr', thr);
delete(gcf);
data{end+1} = {inputs_names, inputs, outputs};

f = [1+3*i, 2+2*i, 3+1*i];
wlen = 2;
inputs_names = {'f', 'display', 'wlen'};
inputs = {f, '_bool_False_', wlen};
[outputs{:}] = phaseplot(f, 'nodisplay', 'wlen', wlen);
delete(gcf);
data{end+1} = {inputs_names, inputs, outputs};

f = (1:3).';
inputs_names = {'f', 'display', 'nf'};
inputs = {f, '_bool_False_', '_bool_True_'};
[outputs{:}] = phaseplot(f, 'nodisplay', 'nf');
data{end+1} = {inputs_names, inputs, outputs};

f = (1:8).';
fmax = length(f) * 0.2;
inputs_names = {'f', 'display', 'fmax'};
inputs = {f, '_bool_False_', fmax};
[outputs{:}] = phaseplot(f, 'nodisplay', 'fmax', fmax);
data{end+1} = {inputs_names, inputs, outputs};

f = (1:8).';
fs = 1.;
fmax = 0.2;
inputs_names = {'f', 'display', 'fs', 'fmax'};
inputs = {f, '_bool_False_', fs, fmax};
[outputs{:}] = phaseplot(f, fs, 'nodisplay', 'fmax', fmax);
data{end+1} = {inputs_names, inputs, outputs};

save(filename, 'data', '-V6');

end
