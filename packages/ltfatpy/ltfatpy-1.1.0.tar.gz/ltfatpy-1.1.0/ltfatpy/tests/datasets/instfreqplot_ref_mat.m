function instfreqplot_ref_mat(filepath)
% Save the output of the instfreqplot function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/instfreqplot_ref.mat'];
disp(filename)

data = {};

nb_outputs = 1;
outputs = cell(1, nb_outputs);

f = [1+3*i, 2+2*i, 3+1*i];
wlen = 2;
inputs_names = {'f', 'display', 'wlen'};
inputs = {f, '_bool_False_', wlen};
% the 'nodisplay' option is not implemented for instfreqplot, so we have to
% delete the generated figure
[outputs{:}] = instfreqplot(f, 'wlen', wlen);
delete(gcf);
data{end+1} = {inputs_names, inputs, outputs};

f = (1:3).';
inputs_names = {'f', 'display'};
inputs = {f, '_bool_False_'};
% the 'nodisplay' option is not implemented for instfreqplot, so we have to
% delete the generated figure
[outputs{:}] = instfreqplot(f);
delete(gcf);
data{end+1} = {inputs_names, inputs, outputs};

inputs_names = {'f', 'display', 'nf'};
inputs = {f, '_bool_False_', '_bool_True_'};
[outputs{:}] = instfreqplot(f, 'nf');
delete(gcf);
data{end+1} = {inputs_names, inputs, outputs};

thr = 0.5;
inputs_names = {'f', 'display', 'thr'};
inputs = {f, '_bool_False_', thr};
[outputs{:}] = instfreqplot(f, 'thr', thr);
delete(gcf);
data{end+1} = {inputs_names, inputs, outputs};

thr = 0.5;
inputs_names = {'f', 'display', 'thr'};
inputs = {f, '_bool_False_', thr};
[outputs{:}] = instfreqplot(f, 'thr', thr);
delete(gcf);
data{end+1} = {inputs_names, inputs, outputs};

climsym = 1.5;
inputs_names = {'f', 'display', 'climsym'};
inputs = {f, '_bool_False_', climsym};
[outputs{:}] = instfreqplot(f, 'climsym', climsym);
delete(gcf);
data{end+1} = {inputs_names, inputs, outputs};

f = (1:8).';
fmax = length(f) * 0.2;
inputs_names = {'f', 'display', 'fmax'};
inputs = {f, '_bool_False_', fmax};
[outputs{:}] = instfreqplot(f, 'fmax', fmax);
delete(gcf);
data{end+1} = {inputs_names, inputs, outputs};

f = (1:8).';
fs = 1.;
fmax = 0.2;
inputs_names = {'f', 'display', 'fs', 'fmax'};
inputs = {f, '_bool_False_', fs, fmax};
[outputs{:}] = instfreqplot(f, fs, 'fmax', fmax);
delete(gcf);
data{end+1} = {inputs_names, inputs, outputs};

methods = {'dgt', 'phase', 'abs'};
rand ("seed", 47)
f = rand(13, 1);
for ind_method = 1:length(methods)
    method = methods{ind_method};
    inputs_names = {'f', 'display', 'method'};
    inputs = {f, '_bool_False_', method};
    [outputs{:}] = instfreqplot(f, method);
    delete(gcf);
    data{end+1} = {inputs_names, inputs, outputs};
end


save(filename, 'data', '-V6');

end
