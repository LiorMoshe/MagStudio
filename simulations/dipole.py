import numpy as np
from yaml import scan

# Vacuum permeability constant.
MU_0 = 1.256637e-6

# Approximation of the direction of earth's magnetic field.
EARTH_FIELD = np.array([0, 1, -1])

EARTH_SCALAR_FIELD = 4.5e-6


def sim_dipole(scan_pts, dipole_loc, dipole_moment):
    """_summary_
    Simulate a single dipole according to the magnetic dipole equation 
    (see https://en.wikipedia.org/wiki/Magnetic_dipole).
    Args:
        scan_pts (np.array): (n,3) array of the locations in which we'll simulate the dipole.
        dipole_loc (np.array): Location of the dipole.
    
    Returns:
        Array of magnetic field values (in nanoteslas) at each of the given scan points.
    """
    # Initial field without any magnetic anomaly.
    field_vals = []
    for i, pt in enumerate(scan_pts):
        r = pt - dipole_loc
        abs_r = np.linalg.norm(r)
        norm_r = r / abs_r
        
        const_val = MU_0 / (4 * np.pi * (abs_r ** 3))
        
        mag_vec = (3 * norm_r * (np.sum(dipole_moment * norm_r))-dipole_moment) * const_val
        mag_vec += dipole_moment * 1e-9
        field_val = np.linalg.norm(mag_vec) * 1e9
        field_vals.append(field_val)
    
    return np.array(field_vals)
