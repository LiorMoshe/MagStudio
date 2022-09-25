import numpy as np
from collections import namedtuple
import math

"""
A Scenario contains all the relevant data for a magnetic simulation.
- Scan Points in the Simulation
- Range of the interpolated grid.
- List of all the simulated magnetic objects.

TODO - Make sure there is a rule of thumb - interpolate minimal bounding box.
Make sure there is no hard extrapolating happening.
"""

DEFAULT_EARTH_FIELD = 4.5e6


GridRange = namedtuple('GridRange', 'x_min x_max y_min y_max')

class Scenario():
    
    
    def __init__(self, scan_pts) -> None:
        self.scan_pts = scan_pts
        
        # FIXME - Currently set a fixed height of 0.
        self.scan_pts = np.hstack((self.scan_pts, np.zeros((self.scan_pts.shape[0], 1))))
        
        self.grid_range = GridRange(x_min=math.floor(self.scan_pts[:, 0].min()-1),
                                    x_max=math.ceil(self.scan_pts[:, 0].max()+1),
                                    y_min=math.floor(self.scan_pts[:, 1].min()-1),
                                    y_max=math.ceil(self.scan_pts[:, 1].max()+1))
        self.mag_objects = {}
        

        self.search_x = np.arange(self.grid_range.x_min, self.grid_range.x_max)
        self.search_y = np.arange(self.grid_range.y_min, self.grid_range.y_max)
        
        
        # By default simulate field of strength 4.5e6
        self.sim_field = np.ones(self.scan_pts.shape[0]) * DEFAULT_EARTH_FIELD
        self.min_field = self.sim_field.min()
        self.max_field = self.sim_field.max()
        
        # Event that will be executed once the magnetic field is updated (mainly for the sliders)
        self.on_field_update = None 
        self.hidden_objects_map = {}
        
    
    
    def set_field_update_listener(self, on_field_update):
        self.on_field_update = on_field_update
    
    def add_mag_object(self, mag_object):
        self.mag_objects[mag_object.obj_id] = mag_object
        self.hidden_objects_map[mag_object.obj_id] = False
        self.sim_field += mag_object.get_inflicted_field(self.scan_pts)
        self.update_boundaries()
    
    def reevaluate_mag_field(self):
        self.sim_field = np.ones(self.scan_pts.shape[0]) * DEFAULT_EARTH_FIELD
        for mag_obj in self.mag_objects.values():
            self.sim_field += mag_obj.get_inflicted_field(self.scan_pts)
        
    
    def update_boundaries(self):
        self.min_field = self.sim_field.min()
        self.max_field = self.sim_field.max()
        self.on_field_update(self.min_field, self.max_field)
    
    def delete_mag_object(self, obj_id):
        """
        Remove the magnetic object with the given id.
        Args:
            obj_id (_type_): _description_

        Returns:
            _type_: _description_
        """
        if obj_id not in self.mag_objects:
            return

        self.sim_field -= self.mag_objects[obj_id].get_inflicted_field(self.scan_pts)
        del self.mag_objects[obj_id]
        del self.hidden_objects_map[obj_id]
    
    def update_mag_props(self, mag_props, obj_id):
        self.sim_field -= self.mag_objects[obj_id].get_inflicted_field(self.scan_pts)
        self.mag_objects[obj_id].update_mag_props(mag_props)
        self.sim_field += self.mag_objects[obj_id].get_inflicted_field(self.scan_pts)
    
    def toggle_hidden_object(self, obj_id):
        if obj_id not in self.hidden_objects_map:
            return
        
        self.hidden_objects_map[obj_id] = not self.hidden_objects_map[obj_id]
        factor = 1 if not self.hidden_objects_map[obj_id] else -1
        self.sim_field += factor * self.mag_objects[obj_id].get_inflicted_field(self.scan_pts)
    
    def get_sohograma_input(self, z_min, z_max):
        return {
            "grid_range": self.grid_range._asdict(),
            "scan_pts": self.scan_pts.tolist(),
            "scan_vals": self.sim_field.tolist(),
            "z_min": z_min,
            "z_max": z_max
        }
        
    @property
    def raw_signal(self):
        return self.sim_field
    
    @property
    def grid_shape(self):
        return (len(self.search_x), len(self.search_y))
    
    def clean(self):
        self.mag_objects = {}
        self.sim_field = np.ones(self.scan_pts.shape[0]) * DEFAULT_EARTH_FIELD
