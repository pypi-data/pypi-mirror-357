function sepdgt_test_mat(filepath)
% Generate some signals and the associated comp_sepdgt and save them into file

if nargin < 1
    filepath = BaseFolder.get_BasePath()
end;

Lr  = [24, 35, 35, 24,144,108,144,135,77,77];
ar  = [ 6,  5,  5,  4,  9,  9, 12,  9, 7, 7];
Mr  = [ 8,  7,  7,  6, 16, 12, 24,  9,11,11];
glr = [16, 14, 21, 12, 48, 12, 24, 18,22,11];

filename=[filepath 'sepdgt_signal_ex.mat'];
disp(filename)
ind = 1;
for phase=0:1
    pt = 'timeinv';
    if(phase == 0)
         pt = 'freqinv';
    end;
    for ii=1:length(Lr)
        L=Lr(ii);
        M=Mr(ii);
        a=ar(ii);
        gl=glr(ii);
        for rtype=1:2
            for W=1:3
                if rtype==1
                    rname='REAL';
                    f=tester_rand(L,W);
                    g=tester_rand(gl,1);
                    cc = comp_sepdgtreal(f,g,a,M,phase);
                    gd = gabdual(g,a,M);
                    frec = comp_isepdgtreal(cc,gd,L,a,M,phase);
                else
                    rname='CMPLX';
                    f=tester_crand(L,W);
                    g=tester_crand(gl,1);
                    cc = comp_sepdgt(f,g,a,M,phase);
                    gd = gabdual(g,a,M);
                    frec = comp_isepdgt(cc,gd,L,a,M,phase);
                end;
                Data{ind}.phase = pt;
                Data{ind}.L = L;
                Data{ind}.M = M;
                Data{ind}.a = a;
                Data{ind}.gl = gl;
                Data{ind}.rtype = rtype;
                Data{ind}.W = W;
                Data{ind}.rname = rname;
                Data{ind}.f = f;
                Data{ind}.g = g;
                Data{ind}.cc = cc;
                Data{ind}.gd = gd;
                Data{ind}.freq = frec;
                ind = ind + 1;
            end;
        end;
    end;
end
save(filename,'Data');




