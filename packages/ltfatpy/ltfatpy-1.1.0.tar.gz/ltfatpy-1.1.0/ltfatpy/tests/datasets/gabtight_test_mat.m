function gabtight_test_mat( filepath )
% Generate some windows and the corresponding tight gabor window

if nargin < 1
    filepath = BaseFolder.get_BasePath();
end;

Lr  = [24, 35, 35, 24,144,108,144,135,77,77];
ar  = [ 6,  5,  5,  4,  9,  9, 12,  9, 7, 7];
Mr  = [ 8,  7,  7,  6, 16, 12, 24,  9,11,11];

filename=[filepath 'gabtight_signal_ex.mat'];
disp(filename)
ind = 1;

for ii=1:length(Lr)
    L=Lr(ii);
    M=Mr(ii);
    a=ar(ii);
    for R=1:3
        for wintype = 1:2
            switch wintype
                case 1
                    g=randn(L,R);
                    rname='REAL ';
                case 2
                    g=tester_crand(L,R);
                    rname='CMPLX';
            end;            
            fprintf('L=%d, M=%d, a=%d, R=%d, rname=%s\n',L,M,a,R,rname);
            gt = gabtight(g,a,M,L);
            Data{ind}.L = L;
            Data{ind}.M = M;
            Data{ind}.a = a;
            Data{ind}.rname = rname;
            Data{ind}.g = g;
            Data{ind}.gt = gt;
            ind = ind + 1;
        end;
    end;
end;

save(filename,'Data');

end

