import numpy as np
from numba import njit, types, prange, get_num_threads
from utils import *


# Creates a smoothed version of the coarser quadratic map
def smoothed_mandelbrot(grid, iter, escape_radius=2):
    lt_grid, iter_grid = quadratic_map(grid, iter, escape_radius)
    lt_grid[np.abs(lt_grid) <= 1] = 1 + 1e-10
    log22 = lambda x: np.log2(np.log2(x)) # Iterated log
    Mb = iter_grid + log22(np.abs(lt_grid)) - log22(escape_radius)

    return Mb


# Iterates grid points in the complex plane iter times under the quadratic map
# Assumes that points will escape once their modulus exceeds the escape radius,
# and stops computing them in further iterations
# Returns "long term" behavior of the grid after iter iterations
#   and the number of iterations spent on a particular grid point
# TODO: Improve time complexity by splitting the grid amongst cores
@njit(parallel=False, fastmath=True)
def quadratic_map(grid, iter, escape_radius=2):
    grid_shape = grid.shape
    grid = grid.flatten()
    
    # We split the computation evenly between the cores:
    ncores = get_num_threads()
    section_length = grid.shape[0] // ncores

    #for i in prange(ncores):
    section = grid#[(i*section_length):((i+1)*section_length)]
    # 'long-term' grid, which contains the long-term (at least, 
    # until iter iterations) behavior of the Mandelbrot set
    lt_grid = np.zeros_like(section, dtype=types.complex128)
    # iteration grid that stores the number of iterations
    iter_grid = np.zeros_like(section, dtype=types.complex128)

    # The threshold is the minimum magnitude for a number in C
    # before its orbit escapes

    for j in range(iter):
        mask = np.abs(lt_grid)<=escape_radius
        lt_grid[mask] = np.power(lt_grid[mask], 2) + section[mask]
        iter_grid[mask] = j

    lt_grid = lt_grid.reshape(grid_shape)
    iter_grid = iter_grid.reshape(grid_shape)


    return lt_grid, iter_grid

if __name__ == "__main__":
    C, real_line, imag_line = generate_grid()
    Mb = smoothed_mandelbrot(C, 100)