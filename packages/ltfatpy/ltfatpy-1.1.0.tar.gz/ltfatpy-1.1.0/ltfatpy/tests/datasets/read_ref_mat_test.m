function read_ref_mat_test(filepath)
% Save the some known reference data to test read_ref_mat

if nargin < 1
    filepath = pwd();
end

filename=[filepath, '/read_ref_mat_test.mat'];
disp(filename)

data = {{{'fun', 'dim', 'var'}, {'abs', 1, 1.3}, {[3., 2.2], 1.5}}, ...
        {{'fun', 'do_it'}, {'dgt', '_bool_True_'}, {[1.4, 1.2]}}};

save(filename, 'data', '-V6');

end
