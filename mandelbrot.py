import numpy as np
from numba import jit, njit, types, prange, get_num_threads, vectorize, cuda
from utils import *
import math


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
# DONE: Improve time complexity by splitting the grid amongst cores
@njit(parallel=True, fastmath=True)
def quadratic_map(grid, iter, escape_radius=2):
    grid_shape = grid.shape
    grid = grid.flatten()
    
    # We split the computation evenly between the cores:
    ncores = get_num_threads()
    section_length = grid.shape[0] // ncores

    # 'long-term' grid, which contains the long-term (at least, 
    # until iter iterations) behavior of the Mandelbrot set
    lt_grid = np.zeros_like(grid, dtype=types.complex128)
    # iteration grid that stores the number of iterations
    iter_grid = np.zeros_like(grid, dtype=types.complex128)
    
    if cuda:
        for j in range(iter):
            
            cuda_quadratic_map(abs_lt_grid)

    else:
        for i in prange(ncores):
            start, end = i*section_length, (i+1)*section_length

            # The threshold is the minimum magnitude for a number in C
            # before its orbit escapes

            for j in range(iter):
                mask = np.abs(lt_grid[start:end])<=escape_radius
                lt_grid[start:end][mask] = np.power(lt_grid[start:end][mask], 2) + grid[start:end][mask]
                iter_grid[start:end][mask] = j

    lt_grid = lt_grid.reshape(grid_shape)
    iter_grid = iter_grid.reshape(grid_shape)


    return lt_grid, iter_grid


# A version of the quadratic map for CUDA graphics cards
# The escape radius is the minimum magnitude for a number in C
# before its orbit escapes the Mandelbrot set. If a number escapes,
# iteration is halted for that number.
# This function is optimized for CUDA-compatible graphics cards.
@guvectorize([(
            types.c16[:], 
            types.c16[:], 
            types.c16[:], 
            types.float64,
            types.float64,
            )], 
            target='cuda')
def cuda_quadratic_map(longterm_grid, 
                       iteration_grid, 
                       initial_grid, 
                       threshold, 
                       current_iteration):
    abs_lt_grid = math.pow(longterm_grid.real, types.float64(2)) + \
        math.pow(longterm_grid.imag, types.float64(2))
    mask = abs_lt_grid<=threshold
    longterm_grid[mask] = np.power(longterm_grid[mask], 2) + initial_grid[mask]
    # Only iterate counts for numbers not exceeding the threshold (escape radius)
    iteration_grid[mask] = current_iteration



if __name__ == "__main__":
    
    C, real_line, imag_line = generate_grid()
    Mb = smoothed_mandelbrot(C, 100)