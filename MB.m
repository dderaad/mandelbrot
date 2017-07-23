function [i] = MB(z, c, i)
  iter_max = 100;
  % f(z) = z^2 + c
  zn =  z.^2 + c;
  I = ones(size(zn));
  mask = (abs(zn) >= 2);
  I(mask) = 0;
  i = i + I;
  if ~any(iter_max-i==0)
    i = MB(zn, c, i);
  end