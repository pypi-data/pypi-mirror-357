function gabframediag_test_mat( filepath )
% Generate some windows and the corresponding diagonal of gabor frame
% operator

if nargin < 1
    filepath = BaseFolder.get_BasePath();
end;

Lr  = [24, 35, 35, 24,144,108,144,135,77,77];
ar  = [ 6,  5,  5,  4,  9,  9, 12,  9, 7, 7];
Mr  = [ 8,  7,  7,  6, 16, 12, 24,  9,11,11];
glr = [16, 14, 21, 12, 48, 12, 24, 18,22,11];

filename=[filepath 'gabframediag_signal_ex.mat'];
disp(filename)
ind = 1;

for ii=1:length(Lr)
    L=Lr(ii);
    M=Mr(ii);
    a=ar(ii);
    gl=glr(ii);
    fprintf('L=%d, M=%d, a=%d, gl=%d\n',L,M,a,gl);
    for jj=1:2
        if jj == 1
            %Complex case
            g=tester_crand(gl,1);
        else
            %Real case
            g=randn(L,1);
        end;
        diag = gabframediag(g, a, M, L);
        Data{ind}.L = L;
        Data{ind}.M = M;
        Data{ind}.a = a;
        Data{ind}.gl = gl;    
        Data{ind}.g = g;
        Data{ind}.diag = diag;
        ind = ind + 1;
    end;
end;

save(filename,'Data');

end

