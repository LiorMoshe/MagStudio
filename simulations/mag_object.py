from fatiando.mesher import PolygonalPrism
from simulations.dipole import sim_dipole
import numpy as np
from fatiando.gravmag._polyprism_numpy import tf
from collections import namedtuple



"""
API for simulations of magnetic objects.
Objects we support:
- A dipole - No dimensions - super small.
- 3D Polygonal Prism.
A dipole will be represented by a single vertex.
"""

EARTH_FIELD_DIRECTION = np.array([0, 1, -1])

EARTH_INC = -45

EARTH_DEC = 90


# Contains all the magnetic properties which are configured by the user.
MagProps = namedtuple('MagProps', 'moment depth zdim')



class MagneticObject():
    
    ID = 1
    
    def __init__(self, vertices, moment, depth, z_dim) -> None:
        self.vertices = vertices
        self.moment = moment * EARTH_FIELD_DIRECTION
        
        self.depth = depth
        self.z_dim = z_dim
        self.obj_id = MagneticObject.ID
        MagneticObject.ID += 1
    
    def update_mag_props(self, mag_props):
        self.depth = mag_props.depth
        self.z_dim = mag_props.zdim
        self.moment = mag_props.moment * EARTH_FIELD_DIRECTION
    
    @property
    def scalar_moment(self):
        return self.moment[1]
        
    def get_inflicted_field(self, scan_pts):
        """
        Get the variations inflicted by this magnetic object at the given scan pts.
        Depends on the number of vertices:
        - Single vertex = dipole.
        - Several = Simulate via fatiando.
        Args:
            scan_pts (np.array): Locations of the scan points.
        """
        if len(self.vertices) == 1:
            return sim_dipole(scan_pts, np.array([self.vertices[0,0], self.vertices[0, 1], self.depth]), self.moment)
        else:
            return tf(xp=scan_pts[:, 0], yp=scan_pts[:, 1], zp=scan_pts[:, 2],
                     prisms=[PolygonalPrism(vertices=self.vertices[:, :2].tolist(), z1=self.depth, z2=self.depth-self.z_dim)], 
                     inc=EARTH_INC, dec=EARTH_DEC, pmag=self.moment)
        
    
    def __str__(self) -> str:
        prefix = 'dipole-' if len(self.vertices) == 1 else 'MagObj-'
        return prefix + str(self.obj_id)
        
    

