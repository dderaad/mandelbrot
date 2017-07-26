% z^2 + c
function p = MB_loop( c, iter )
    z = 0;
    for n = 1:iter
        z = z.^2+c;
    end
    p = z;
end