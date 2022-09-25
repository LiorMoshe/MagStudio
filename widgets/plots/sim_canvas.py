import matplotlib
matplotlib.use('Qt5Agg')


from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from transforms.rtp import rtp

from matplotlib.figure import Figure
from matplotlib.pyplot import Rectangle
from simulations.mag_object import MagneticObject
import numpy as np
from simulations.scenario import GridRange
from matplotlib.widgets import RectangleSelector
from enum import Enum
import matplotlib.gridspec as gridspec
from widgets.gps_to_signal_cursor import ExtendableCursor, bind_gps_to_signal

class SimMode(Enum):
    """
    Enum containing all the simulation options given to the user.
    """
    DIPOLE=0
    MAGOBJ=1


class SimulationCanvas(FigureCanvasQTAgg):

    def __init__(self):
        self.fig = Figure(figsize=(14, 14), dpi=100)
        self.gridspec = gridspec.GridSpec(ncols=4, nrows=2, figure=self.fig)
        self.scenario = None
        

        self.interp_ax = self.fig.add_subplot(self.gridspec[0, 1:3])
        self.signal_ax = self.fig.add_subplot(self.gridspec[1, :])
        self.grid_range = None
        
        # By default - simulate dipoles.
        self.mag_properties_query = None
        self.mag_obj_listener = None
        
        # If true allows the user to simulate objects using the cursor.
        self.sim_on = False
        
        # The simulation mode selected by the user.
        self.sim_mode = SimMode.DIPOLE
        
        # Selected magnetic object id.
        self.selected_id = None
        
        # Map each magnetic object to its plot.
        self.mag_obj_plots = {}
        
        self.initialize_cursor()
        
        # self.hover_sig_plt = self.signal_ax.axvline(color='black')
        self.hover_interp_plt = []
        
        # Holds gridded values of the interpolation.
        self.interp_data = None
        
        # True whether we wish to show the rtp instead of the regular intepolation.
        self.show_rtp = False
        
        # Selected interp type by the user.
        self.interp_type = None
        
        self.interp_contour = None
        
        super(SimulationCanvas, self).__init__(self.fig)
    
    def flip_rtp_mode(self):
        self.show_rtp = not self.show_rtp
    
    def set_interp_type(self, interp_type):
        self.interp_type = interp_type 
        
        if self.scenario is not None:
            self.update_interp_data()
            self.plot_data()
    
    def update_interp_data(self):
        if len(self.scenario.mag_objects) == 0:
            # Fill with empty grid.
            self.interp_data = np.ones((len(self.scenario.search_x), len(self.scenario.search_y))) \
                                * self.scenario.sim_field.min()
        else:
            self.interp_data = self.interp_type.value.interp_func(self.scenario.scan_pts, 
                self.scenario.raw_signal,
                self.scenario.search_x,
                self.scenario.search_y)
            
            if self.show_rtp:
                self.interp_data = rtp(self.scenario.search_x, self.scenario.search_y,
                self.interp_data)

   
    def initialize_cursor(self):
        self.sig_cursor = ExtendableCursor(self.signal_ax, useblit=True, color='black', linewidth=1, horizOn=False) 
        self.interp_cursor = ExtendableCursor(self.interp_ax, useblit=True, color='black', linewidth=1)     
        
        if self.scenario is not None:
            bind_gps_to_signal(self.interp_cursor, self.sig_cursor, self.scenario.raw_signal,
                        self.scenario.scan_pts[:, :2])


       
    def set_scenario(self, scenario):
        self.scenario = scenario
        self.interp_ax.set_xlim(self.scenario.search_x.min(), self.scenario.search_x.max())
        self.interp_ax.set_ylim(self.scenario.search_y.min(), self.scenario.search_y.max())

        self.plot_data()
        self.initialize_cursor()

        
    def set_mag_props_query(self, mag_props_query):
        self.mag_properties_query = mag_props_query
        
    def set_grid_range(self, grid_range):
        self.grid_range = grid_range
        self.interp_ax.set_xlim(grid_range.x_min-1, grid_range.x_max+1)
        self.interp_ax.set_ylim(grid_range.y_min-1, grid_range.y_max+1)
        self.draw()
    
    def set_selected_id(self, selected_id):
        # Update previously selected.
        if self.selected_id:
            self.remove_object_plot(self.selected_id)
            self.draw_mag_object(self.scenario.mag_objects[self.selected_id])
            
        self.selected_id = selected_id
        self.remove_object_plot(self.selected_id)
        self.draw_mag_object(self.scenario.mag_objects[selected_id], color='pink')
        self.draw()
        
    def remove_object_plot(self, obj_id):
        try:
            self.mag_obj_plots[self.selected_id].remove()
        except ValueError:
            # TODO - Add logs.
            return
    
    def update_mag_properties(self, mag_props, obj_id):
        """
        Update the magnetic properties of the object with the given obj_id
        Args:
            mag_props (_type_): _description_
            obj_id (_type_): _description_
        """
        if obj_id not in self.scenario.mag_objects:
            return
        
        self.scenario.update_mag_props(mag_props, obj_id)
        self.update_interp_data()
        self.scenario.update_boundaries()
        self.plot_data()
    
    def set_mag_object_listener(self, listener_func):
        """
        Set the listener which will be activated once we add a new magnetic object.
        """
        self.mag_obj_listener = listener_func
        
    def attach_dipole_cid(self):
        self.dipole_cid = self.fig.canvas.mpl_connect('button_press_event', self.simulate_dipole)
    
    def add_rect_object(self, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        rect = Rectangle( (min(x1,x2),min(y1,y2)), np.abs(x1-x2), np.abs(y1-y2) , fill=None)
        self.interp_ax.add_patch(rect)
        
        # Add the magnetic object.
        moment, depth, zdim = self.mag_properties_query()
        self.add_mag_object(
                MagneticObject(vertices=np.array([
                    [x1, y1],
                    [x1, y2],
                    [x2, y2],
                    [x2, y1]
                ]), moment=moment, depth=depth, z_dim=zdim))
        self.plot_data()
        self.draw()
    
    def attach_rectangle_selector(self):
        self.rect_selector = RectangleSelector(self.interp_ax, self.add_rect_object,
                       drawtype='box', useblit=False, button=[1, 3], 
                       minspanx=5, minspany=5, spancoords='pixels', 
                       interactive=True)
        
   
    def toggle_sim_mode(self):
        """
        Toggle the sim_on property.
        Once activated, all events listening to the user cursor will be turned on.
        """
        self.sim_on = not self.sim_on
        if self.sim_on:
            self.activate_sim_mode_listener(self.sim_mode)
        else:
            self.deactivate_sim_mode_listener(self.sim_mode)
    
    def toggle_hidden_object(self, obj_id):
        self.scenario.toggle_hidden_object(obj_id)
        self.update_interp_data()
        self.plot_data()
    
    def delete_mag_object(self, obj_id):
        """
        Delete the object with the given id from the scenario and replot the data.
        Args:
            obj_id (_type_): _description_
        """
        if obj_id == self.selected_id:
            self.selected_id = None
            
        self.scenario.delete_mag_object(obj_id)
        self.update_interp_data()
        self.plot_data()
        

    def flip_simulation_mode(self, i):
        """
        Flip the simulation mode selected.
        Args:
            i (_type_): _description_
        """
        prev_sim_mode = self.sim_mode
        self.sim_mode = SimMode(i)
        if not self.sim_on:
            return

        self.deactivate_sim_mode_listener(prev_sim_mode)
        self.activate_sim_mode_listener(self.sim_mode)
    
    def activate_sim_mode_listener(self, curr_sim_mode):
        if curr_sim_mode.value == SimMode.DIPOLE.value:
            self.attach_dipole_cid()
        else:
            self.attach_rectangle_selector()
    
    def deactivate_sim_mode_listener(self, curr_sim_mode):
        if curr_sim_mode.value == SimMode.DIPOLE.value:
            self.fig.canvas.mpl_disconnect(self.dipole_cid)
        else:
            self.rect_selector = None

            
    def add_mag_object(self, mag_object):
        if self.scenario is None:
            return
        
        self.scenario.add_mag_object(mag_object)
        
        # Update the interpolation.
        self.update_interp_data()
        
        if self.mag_obj_listener:
            self.mag_obj_listener(mag_object)
        
    def simulate_dipole(self, event):
        if event.inaxes == self.interp_ax:
            # Add a dipole in any clicked location.
            moment, depth, _ = self.mag_properties_query()
            print(f'Simulating dipole at: [{event.xdata}, {event.ydata}] M: {moment} d: {depth}')
            self.add_mag_object(MagneticObject(np.array([[event.xdata, event.ydata]]),
                                                                moment=moment, depth=depth, z_dim=0),
                                            )
            self.plot_data()
    
    def reset_state(self):
        self.scenario.clean()
        self.mag_obj_plots = {}
        self.sim_on = False
        self.selected_id = None
        self.sim_mode = SimMode.DIPOLE
        self.interp_data = None
        self.plot_data()
        
    def get_magnetic_object(self, obj_id):
        return self.scenario.mag_objects[obj_id]

    def plot_data(self):
        # Keep the same xlim and ylim
        prev_xlim = self.interp_ax.get_xlim()
        prev_ylim = self.interp_ax.get_ylim()
        
        self.interp_ax.clear()
        self.signal_ax.clear()
        raw_signal = self.scenario.raw_signal
        self.signal_ax.plot(raw_signal)
        
        if self.scenario is not None:
            self.interp_ax.scatter(self.scenario.scan_pts[:, 0], self.scenario.scan_pts[:, 1],
                                   c=raw_signal, alpha=0.5, zorder=10, cmap='seismic',)
            self.interp_ax.set_xlim(prev_xlim[0], prev_xlim[1])
            self.interp_ax.set_ylim(prev_ylim[0], prev_ylim[1])

        if self.interp_data is not None:
            self.interp_contour = self.interp_ax.contourf(self.scenario.search_x, self.scenario.search_y,
                                    self.interp_data.T, cmap='jet', levels=200,
                                    zorder=1)
 
        
        # Redraw the magnetic objects.
        self.draw_mag_objects()
        
        # FIXME - Why we need reinitialize the selector on each render?
        if self.sim_on and self.sim_mode == SimMode.MAGOBJ:
            self.attach_rectangle_selector()

        # self.initialize_cursor()
        self.draw()
    
    def update_clim(self, vmin, vmax):
        if self.interp_contour is not None:
            vmin = max(self.interp_data.min(), vmin)
            vmax = min(self.interp_data.max(), vmax)
            
            if vmax < vmin:
                vmin = vmax
            
            self.interp_contour.set_clim(vmin, vmax)
            self.draw()
        
    def draw_mag_objects(self):
        """
        Draw all the relevant magnetic objects.
        - Dipole - Single black dot.
        - Rectangle - Add a rectangle patch.
        """
        for obj_id, mag_obj in self.scenario.mag_objects.items():
            self.draw_mag_object(mag_obj, color='pink' if obj_id == self.selected_id else 'k')
                
    def draw_mag_object(self, mag_obj, color='k'):
        if self.scenario.hidden_objects_map[mag_obj.obj_id]:
            return
        
        if len(mag_obj.vertices) == 1:
            self.mag_obj_plots[mag_obj.obj_id] = self.interp_ax.scatter(
                            mag_obj.vertices[0, 0], mag_obj.vertices[0, 1], c=color, zorder=1e2)
        else:
            rect = np.vstack((mag_obj.vertices, mag_obj.vertices[0]))
            self.mag_obj_plots[mag_obj.obj_id] = self.interp_ax.plot(rect[:, 0], rect[:, 1], c=color,
                                                                     zorder=1e2)[0]

        