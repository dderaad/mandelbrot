% Julia Sets
function p = Julia( fun , funprime, field , iter )
    % d(z) = psi(z)/|psi'(z)|
    %      = lim(k->inf) |z_k-z*|/|z_k'|
    p = field;
    zprime = ones(size(p));
    
    for k = 1:iter
        p = fun(p);
        zprime = funprime(p).*zprime;
    end
    
    zprime(abs(real(zprime))<eps|abs(imag(zprime))<eps) = 1;
    p = abs(p - field)./zprime;
end