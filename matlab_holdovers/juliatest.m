close all;

% Julia test
i = sqrt(-1);
dR = 7.5e-4;
dI = dR;
ra = -2:dR:2; 
ia = i*(-2:dI:2).';
C = repmat(ra,length(ia),1)+repmat(ia,1,length(ra));

colormap(hot)

c =  -0.75+0.11*i;
F = @(z)z.^2+c;
f = @(z)2*z;

p = Julia(F, f, C, 75);
p(isnan(p)) = inf;
p(isinf(p)) = 0;
%imagesc(ra, imag(ia), abs(p))
%axis equal
%figure
contour(ra, imag(ia), abs(p), [eps eps], 'k')
axis square
