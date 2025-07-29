function ifftreal_ref_mat(filepath)
% Save the output of the ifftreal function into a .mat file for some example
% inputs

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/ifftreal_ref.mat'];
disp(filename)

% NOTE: ifftreal is buggy in LTFAT 2.1.0 for Octave
% For example:
% ifftreal(rand(8,1), 32, 1);
% crashes octave.
% It seems that the crash arises when N is too big compared to the length of the
% data along the dimension used to do the transform.
% So we are limited in the values that can be used as N in this test.
%
% In general it seems that values of N different from the one used to compute
% fftreal leads to wrong results for arrays having 2D or more.
% For example :
%>> ifftreal([1,2;3,4], 4, 1)
%ans =
%
%   2.25000   1.00000
%  -0.25000   1.00000
%  -0.75000   1.00000
%  -0.25000   1.00000
%
%>> ifftreal([1;3], 4, 1)
%ans =
%
%   1.75000
%   0.25000
%  -1.25000
%   0.25000
%
%>> ifftreal([2;4], 4, 1)
%ans =
%
%   2.50000
%   0.50000
%  -1.50000
%   0.50000
%
%>> a=rand(3)+i*rand(3);
%>> ifftreal(a(:,3), 2, 1)
%ans =
%
%   0.37296
%   0.34901
%
%>> ifftreal(a, 2, 1)
%ans =
%
%   0.805618   0.087949   0.491575
%  -0.115312  -0.022500   0.413780
  
inputs_names = {'c', 'N', 'dim'};
sizes = {[8; 1], [13; 1]};
nb_outputs = 1;
outputs = cell(1, nb_outputs);
data = {};
inputs={};

for ind = 1:length(sizes)
    size = sizes{ind};
    inputs{1} = rand(size)+i*rand(size);
    for ind_N = -3:3    
        for dim = 1:(length(size)-1)
            inputs{3} = dim;
            inputs{2} = (size(dim)-1)*2 + ind_N;
            [outputs{:}] = ifftreal(inputs{:});
            inputs{3} = dim-1; % needed because Python dimensions start at 0
            data{end+1} = {inputs_names, inputs, outputs};
        end
    end
end

save(filename, 'data', '-V6');

end
