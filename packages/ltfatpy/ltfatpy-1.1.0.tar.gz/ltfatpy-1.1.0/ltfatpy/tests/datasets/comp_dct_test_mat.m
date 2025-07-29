function comp_dct_test_mat(filepath)
% Generate some signals and the associated dct and save them into mat file

if nargin < 1
    filepath = BaseFolder.get_BasePath()
end;

Lr  = [24, 35, 35, 24,144,108,144,135,77,77];

filename=[filepath 'comp_dct_signal_ex.mat'];
disp(filename)
ind = 1;

for ii=1:length(Lr);
    
    L=Lr(ii);
    
    for rtype=1:2
        for dct_type=1:4
            for W=1:3
                if rtype==1
                    rname='REAL';
                    fprintf('TYPE=%s;L=%d;W=%d;DCT_TYPE=%d;\n',rname,L,W,dct_type);
                    
                    f=tester_rand(L,W);
                    cc = comp_dct(f,dct_type);
                    
                else
                    rname='CMPLX';
                    fprintf('TYPE=%s;L=%d;W=%d;DCT_TYPE=%d;\n',rname,L,W,dct_type);
                    f=tester_crand(L,W);
                    cc = comp_dct(f,dct_type);
                end;
                Data{ind}.dct_type = dct_type;
                Data{ind}.L = L;
                Data{ind}.W = W;
                Data{ind}.rtype = rtype;
                Data{ind}.rname = rname;
                Data{ind}.f = f;
                Data{ind}.cc = cc;
                ind = ind + 1;
            end;
        end;
    end;
end
save(filename,'Data');
end