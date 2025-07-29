function comp_dst_test_mat(filepath)
% Generate some signals and the associated dst and save them into mat file

if nargin < 1
    filepath = BaseFolder.get_BasePath()
end;

Lr  = [24, 35, 35, 24,144,108,144,135,77,77];

filename=[filepath 'comp_dst_signal_ex.mat'];
disp(filename)
ind = 1;

for ii=1:length(Lr);
    
    L=Lr(ii);
    
    for rtype=1:2
        for dst_type=1:4
            for W=1:3
                if rtype==1
                    rname='REAL';
                    fprintf('TYPE=%s;L=%d;W=%d;DST_TYPE=%d;\n',rname,L,W,dst_type);
                    
                    f=tester_rand(L,W);
                    cc = comp_dst(f,dst_type);
                    
                else
                    rname='CMPLX';
                    fprintf('TYPE=%s;L=%d;W=%d;DST_TYPE=%d;\n',rname,L,W,dst_type);
                    f=tester_crand(L,W);
                    cc = comp_dst(f,dst_type);
                end;
                Data{ind}.dst_type = dst_type;
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