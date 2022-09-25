from fatiando.gravmag.transform import reduce_to_pole
import numpy as np

EARTH_INC=45
EARTH_DEC=90

def rtp(search_x, search_y, scan_vals):
    xvals, yvals = np.meshgrid(search_x, search_y, indexing='ij')
    rtp_vals = reduce_to_pole(x=xvals.reshape(-1), y=yvals.reshape(-1), data=scan_vals.reshape(-1), 
                   shape=scan_vals.shape, inc=EARTH_INC, dec=EARTH_DEC,
                   sinc=EARTH_INC, sdec=EARTH_DEC)
    rtp_vals = np.reshape(rtp_vals, scan_vals.shape)
    return rtp_vals