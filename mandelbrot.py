import numpy as np
from numba import njit, types

def smoothed_mandelbrot(grid, iter, escape_radius=2):
  lt_grid, iter_grid = quadratic_map(grid, iter, escape_radius)
  lt_grid[np.abs(lt_grid) <= 1] = 1 + 1e-10
  log22 = lambda x: np.log2(np.log2(x)) # Iterated log
  Mb = iter_grid + log22(np.abs(lt_grid)) - log22(escape_radius)

  return Mb

@njit(parallel=True)
def quadratic_map(grid, iter, escape_radius=2):
  grid_shape = grid.shape
  grid = grid.flatten()
  # 'long-term' grid, which contains the long-term (at least, 
  # until iter iterations) behavior of the Mandelbrot set
  lt_grid = np.zeros_like(grid, dtype=types.complex128)
  # iteration grid that stores the number of iterations
  iter_grid = np.zeros_like(grid, dtype=types.complex128)


  # The threshold is the minimum magnitude for a number in C
  # before its orbit escapes

  for i in range(iter):
    mask = np.abs(lt_grid)<=escape_radius
    lt_grid[mask] = np.power(lt_grid[mask], 2) + grid[mask]
    iter_grid[mask] = i

  lt_grid = lt_grid.reshape(grid_shape)
  iter_grid = iter_grid.reshape(grid_shape)


  return lt_grid, iter_grid