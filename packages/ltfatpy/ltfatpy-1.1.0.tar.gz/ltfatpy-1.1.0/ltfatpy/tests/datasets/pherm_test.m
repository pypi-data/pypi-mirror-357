function pherm_test( filepath )

if nargin < 1
    filepath = BaseFolder.get_BasePath()
end;


L = 100:20:400;
order = 0:5:50;
tfr = 0.1:0.1:1;
phase = {'accurate','fast'};
orthtype = {'noorth','polar','qr'};

filename=[filepath 'pherm_ref.mat'];
disp(filename)
ind = 1;

for l =L
    for dimorder = 1:1:5
        orderr = order(randperm(length(order)));
        o = orderr(1:dimorder)
        for t = tfr
            for p = 1:1:2
                for ort = 1:1:3
                    fprintf('L=%d, tfr=%d, phase=%s, orthtype=%s\n',l,t,phase{p},orthtype{ort});
                    [g,D] = pherm(l,o,t,phase{p},orthtype{ort});
                    data{ind} = {{'L','order','tfr','phase','orthtype'},{l,o,t,phase{p},orthtype{ort}},{g,D}};
                    ind = ind + 1;
                end;
            end;
            
        end;
    end;
end;

save(filename,'data');

end

