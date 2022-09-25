from re import search
from scipy.interpolate import NearestNDInterpolator
import numpy as np
from enum import Enum
from collections import namedtuple
from scipy.spatial.distance import cdist
from pykrige.ok import OrdinaryKriging

InterpContent = namedtuple('InterpContent','value display_str interp_func')

def nearest_interp(scan_pts, scan_vals, search_x, search_y):
    interpolator = NearestNDInterpolator(x=scan_pts[:, :2], y=scan_vals)
    
    x, y = np.meshgrid(search_x, search_y, indexing='ij')
    z = interpolator(x, y)
    return z

def weighted_average(scan_pts, scan_vals, search_x, search_y):
    x, y = np.meshgrid(search_x, search_y, indexing='ij')
    grid_pts = np.vstack((x.reshape(-1), y.reshape(-1))).T
    dist_mat = cdist(grid_pts, scan_pts[:, :2])
    1 / dist_mat
    z_vals = np.sum(((1/dist_mat)*scan_vals), axis=1) / (np.sum((1/dist_mat), axis=1))
    z_vals = np.reshape(z_vals, x.shape)
    return z_vals

def krigging(scan_pts, scan_vals, search_x, search_y):
    search_x = search_x.astype(np.float64)
    search_y = search_y.astype(np.float64)


    # print('hello')

    zvalues, sigmasq = OrdinaryKriging(scan_pts[:, 0], scan_pts[:, 1], scan_vals).execute(
        style='grid',
        xpoints=search_x,
        ypoints=search_y
    )
    
    return zvalues.T

class InterpType(Enum):
    NEAREST=InterpContent(0, 'Nearest', nearest_interp)
    WEIGHTED_AVERAGE=InterpContent(1, "Weighted Average", weighted_average)
    KRIGGINGG=InterpContent(2, "Krigging", krigging)

