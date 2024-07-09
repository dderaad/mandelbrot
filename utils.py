import numpy as np
from numba import types
from dash import html
import matplotlib.colors as colors
#import colorsys

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


"""
Turns raw text written in 'standard' format and returns a list of html objects
representing prettier text.
TODO: investigate dcc.Markdown
"""
def format_html(text):
    children = []
    for line in text.split('\n'):
        children.append(line)
        children.append(html.Br())

    return children


#http://www.mrob.com/pub/muency/color.html
# TODO: fix this
def mandelbrot_to_colorspace(continuous_dwell, lt_grid, iter_grid, gradient, max_iter, resolution, h=[0, 1], s=[0, 1], v=[0, 1], big=100000):
    dwell = np.floor(continuous_dwell)
    distance_estimate = np.abs(np.log(np.pow(continuous_dwell, 2))) * np.abs(continuous_dwell) / (np.abs(gradient) + 1/big)
    final_radius = continuous_dwell - dwell
    final_angle = np.angle(continuous_dwell).astype(np.float64)
    dscale = np.log2(distance_estimate / resolution)
    
    val = dscale.copy()
    dscale_mask = dscale > 0
    val[dscale_mask] = 1.0
    dscale_mask = dscale > -8
    val[dscale_mask] = (8 + val[dscale_mask]) / 8
    
    
    # Maps P to an angle and radius on the color wheel:
    P = np.log1p(dwell - np.min(dwell)) / np.log(big)
    
    P_mask = P<0.5
    P[P_mask]  = 1.0 - 1.5*P[P_mask]
    P[~P_mask] = -0.5 + 1.5*P[~P_mask]
    angles = P.copy()
    angles[P_mask]  = 1 - P[P_mask]
    angles[~P_mask] = P[~P_mask]
    radii = np.sqrt(P)

    val[dwell%2==1]   *= 17/20
    radii[dwell%2==1] *= 2/3

    angles[final_angle > np.pi] += 0.02
    angles += 0.0001 * final_radius

    hue = angles * 10
    hue = hue - np.floor(hue)
    sat = radii - np.floor(radii)

    image = np.dstack([hue, sat, val])
    
    rgb_image = colors.hsv_to_rgb(normalize_colors(image, h, s, v)) 
    #rgb_image = np.array([colorsys.hls_to_rgb(pixel[0], pixel[1], pixel[2]) for pixel in zip(hls_image[:,:,0].flatten(), hls_image[:,:,1].flatten(), hls_image[:,:,2].flatten())]).reshape(hls_image.shape)

    white_mask = dwell>=np.max(dwell)*0.65
    rgb_image[white_mask] = np.array([1, 1, 1])

    return rgb_image


def to_flat_colorspace(image):
    return ['rgb({},{},{})'.format(r, g, b) for row in image for (r, g, b) in row]


def normalize_colors(arr, a, b, c):
    # Ensure the input is a 3D array
    if arr.ndim != 3:
        raise ValueError("Input array must be 3-dimensional")
    
    # Find the min and max values along the (0, 1) axes for each channel
    min_vals = arr.min(axis=(0, 1), keepdims=True)
    max_vals = arr.max(axis=(0, 1), keepdims=True)
    
    # Normalize the array
    norm_arr = (arr - min_vals) / (max_vals - min_vals)

    # Scale to the target range
    target_max = np.array(
        [[[
        a[1], 
        b[1], 
        c[1]
        ]]]
        )
    target_min = np.array(
        [[[
        a[0], 
        b[0], 
        c[0]
        ]]]
        )
    norm_arr = norm_arr * (target_max - target_min) + target_min
    
    return norm_arr


if __name__ == "__main__":
    C, _, _ = generate_grid()
    mandelbrot_to_colorspace(np.abs(C).astype(np.float64), 100*np.ones_like(C).astype(np.float64), None, None, None, 100)
