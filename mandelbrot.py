import numpy as np
from numba import njit, types, prange, get_num_threads
from utils import *


# Creates a smoothed version of the coarser quadratic map, 
# and returns the data as well as a co
# Inspired by http://www.mrob.com/pub/muency/representationfunction.html
def smoothed_mandelbrot(grid, iter, escape_radius=1000):
    lt_grid, iter_grid, gradient = quadratic_map(grid, iter, escape_radius)
    lt_grid[np.abs(lt_grid) <= 1] = 1 + 1e-10
    log22 = lambda x: np.log2(np.log2(x)) # Iterated log
    continuous_dwell = (iter_grid + log22(np.abs(lt_grid)) - log22(escape_radius)).astype(np.float64)

    return continuous_dwell, lt_grid, iter_grid, gradient


"""
Iterates grid points in the complex plane iter times under the quadratic map
Assumes that points will escape once their modulus exceeds the escape radius,
and stops computing them in further iterations
Returns "long term" behavior of the grid after iter iterations
  and the number of iterations spent on a particular grid point

DONE: Improve time complexity by splitting the grid amongst cores
"""
@njit(parallel=False, fastmath=True)
def quadratic_map(grid, iter, escape_radius):
    grid_shape = grid.shape
    grid = grid.flatten()
    
    # We split the computation evenly between the cores:
    ncores = get_num_threads() - 1 # -1 to prevent some crashes?
    section_length = grid.shape[0] // ncores

    # 'long-term' grid, which contains the long-term (at least, 
    # until iter iterations) behavior of the Mandelbrot set
    lt_grid = np.zeros_like(grid, dtype=types.complex128)
    # iteration grid that stores the number of iterations
    iter_grid = np.zeros_like(grid, dtype=types.int16)
    # gradient grid that stores the pointwise derivative
    gradient = grid.copy()

    for i in prange(ncores):
        start, end = i*section_length, (i+1)*section_length

        # The threshold is the minimum magnitude for a number in C
        # before its orbit escapes

        for j in range(iter):
            mask = np.abs(lt_grid[start:end])<=escape_radius
            gradient[start:end][mask] = 2 * lt_grid[start:end][mask] * gradient[start:end][mask] + 1
            lt_grid[start:end][mask] = np.power(lt_grid[start:end][mask], 2) + grid[start:end][mask]
            iter_grid[start:end][mask] = j
            

    lt_grid = lt_grid.reshape(grid_shape)
    iter_grid = iter_grid.reshape(grid_shape)
    gradient = gradient.reshape(grid_shape)


    return lt_grid, iter_grid, gradient

if __name__ == "__main__":
    C, real_line, imag_line = generate_grid()
    Mb = smoothed_mandelbrot(C, 100)