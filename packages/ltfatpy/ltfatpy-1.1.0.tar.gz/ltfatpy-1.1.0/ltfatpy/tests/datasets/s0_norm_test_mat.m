function s0_norm_test( filepath )
% Generates signals and associated S0-norms


if nargin < 1
    filepath = BaseFolder.get_BasePath();
end;

filename=[filepath 's0_norm_test.mat'];
disp(filename)
ind = 1;

for i=1:10
    gl = randi([10 50])
    R = randi([1 4])
    fprintf('gl=%d, R=%d\n',gl,R);
    for jj=1:2
        if jj == 1
            %Complex case
            g=tester_crand(gl,R);
        else
            %Real case
            g=randn(gl,R);
        end;
        if R == 1
            d = 1
        else
            d = randi([1 2])
        end;
        if randi([1 2]) == 1
            r = 'rel';
        else
            r = 'norel'
        end;
        s0 = s0norm(g, 'dim', d, r);
        Data{ind}.gl = gl;
        Data{ind}.R = R;
        Data{ind}.dim = d;
        Data{ind}.rel = r;    
        Data{ind}.g = g;
        Data{ind}.s0 = s0;
        Data{ind}.s0shape = size(s0);
        ind = ind + 1;
    end;
end;

save(filename,'Data');

end

