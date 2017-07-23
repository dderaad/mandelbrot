%% Mandelbrot

% f(z) = z^2 + c
% Determine the divergence of f(f(f(...f(z)...)))
% If abs(f(z)) exceeds 2, it will diverge.

z0 = 0;
Re = -2:.025:1;
Im = (sqrt(-1)*(-1:.025:1)).';

pRe = repmat(Re, length(Im), 1);
pIm = repmat(Im, 1, length(Re));

pf = pRe + pIm;

i0 = zeros(size(pf));

pc = MB(z0, pf, i0);
colormap(hot(6))
imagesc(Re, imag(Im), -pc) 
