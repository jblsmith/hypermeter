% Requires  MiningSuite, github version
% http://olivierlar.github.io/miningsuite/

load hey_ya_detection_function
s = sig.Signal(detecfunc(:,2),'Srate',100);
p0 = sig.peaks(s,'Contrast',.01,'Order','Abscissa');
d0 = get(p0,'PeakPos');
dp0 = d0.content{1};
ddp0 = dp0(2) - dp0(1);
p = sig.peaks(s,'Threshold',.33,'Order','Abscissa');
d = get(p,'PeakPos');
v = get(p,'PeakVal');
dp = d.content{1};
dv = v.content{1};
ddp = diff(dp);
sequ = [];
i = 1;
oldr = [];
while i <= length(ddp)
    r = round(ddp(i)/ddp0);
    
    if i > 1 && i < length(ddp) && r == oldr && dv(i+1) < dv(i)
        r2 = round(ddp(i+1)/ddp0);
        if r2 < r
            r = r + r2;
            ddp(i+1) = [];
            dv(i+1) = [];
        end
    end
    %sequ(end+1:end+r) = 1:r;
    sequ(end+1) = r;
    i = i + 1;
    oldr = r;
end

figure,plot(sequ,'*')

%%

load love_is_all_ddf
s = sig.Signal(ddf(:,2),'Srate',100);
p0 = sig.peaks(s,'Contrast',.01,'Order','Abscissa');
d0 = get(p0,'PeakPos');
dp0 = d0.content{1};
ddp0 = dp0(2) - dp0(1);
p = sig.peaks(s,'Threshold',.2,'Order','Abscissa','Normalize',0);
d = get(p,'PeakPos');
v = get(p,'PeakVal');
dp = d.content{1};
dv = v.content{1};
ddp = diff(dp);
sequ = [];
i = 1;
oldr = [];
while i <= length(ddp)
    r = round(ddp(i)/ddp0);
    sequ(end+1) = r;
    i = i + 1;
    oldr = r;
end

figure,plot(sequ,'*')