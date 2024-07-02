import numpy as np
from numba import types

"""
Generates a complex grid and corresponding axes for the given bounds
The resolution refers to the number of evenly spaced points used in both
The y and x dimensions
"""
def generate_grid(re_bounds=(-3, 1.5), 
                  im_bounds=(-1.25, 1.25), 
                  resolution=1000):
    real_line = np.linspace(*re_bounds, resolution, dtype=np.float64)
    imag_line = np.linspace(*im_bounds, resolution, dtype=np.float64)
    real_plane, imag_plane = np.meshgrid(real_line, imag_line)
    C = real_plane + imag_plane * 1j

    return C, real_line, imag_line

