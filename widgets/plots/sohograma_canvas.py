import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib.widgets import Slider
from widgets.plots.percentile_filter import PercentileFilter
from scipy.spatial import ConvexHull
from simulations.dipole import sim_dipole


MIN_PERCENTILE = 80


class SohogramaCanvas(FigureCanvasQTAgg):
    
    
    def __init__(self, scenario, pt_cloud, interp_data, z_min, z_max) -> None:
        self.fig = Figure(figsize=(14, 14), dpi=100)
        self.z_min = z_min
        self.z_max = z_max
        
        super(SohogramaCanvas, self).__init__(self.fig)

        self.gridspec = gridspec.GridSpec(ncols=21, nrows=22, figure=self.fig)
        
        self.scenario = scenario
        self.pt_cloud = pt_cloud
        self.percentile_filter = PercentileFilter(self.scenario.search_x, 
                                                  self.scenario.search_y,
                                                  np.arange(z_min, z_max+1),
                                                  self.pt_cloud)
        self.interp_data = interp_data
        
        # Axis to present the 3d point cloud.
        self.pt_cloud_ax= self.fig.add_subplot(self.gridspec[:, 1:12], projection='3d')
        self.pt_cloud_ax.set_zlim(self.z_min, 0)
        
        self.filtered_cloud = None
        
        # Axis to show the area of each height layer.
        self.area_ax = self.fig.add_subplot(self.gridspec[:6, 13:])
        
        # Axis to show the simulated signal in comparison to the input signal.
        self.sig_ax =  self.fig.add_subplot(self.gridspec[7:13, 13:])
        
        # Axis to view the pt cloud overlayed in 2d view over the given layer.
        self.view_2d_ax =  self.fig.add_subplot(self.gridspec[14:20, 13:])
        
        # The optimal height will be the one with the largest area at the given percentile.
        self.optimal_height = None
        
        self.height_to_area = None
        self.shown_height_scatter = None
        
        
        self.height_slider_ax = self.fig.add_subplot(self.gridspec[21, 13:])
        self.height_slider = Slider(self.height_slider_ax, 'Height', self.z_min, self.z_max,
                                    valinit=self.z_max, valstep=1)
        
        self.percentile_slider_ax = self.fig.add_subplot(self.gridspec[:, 0])
        self.percentile_slider = Slider(self.percentile_slider_ax, 'Percentile', 
                                        self.percentile_filter.percentile_vals.min(), 
                                        self.percentile_filter.percentile_vals.max(),
                                     valstep=1,
                                    orientation="vertical", 
                                    valinit=self.percentile_filter.percentile_vals[-1])
        self.percentile_slider.on_changed(self.filter_cloud)
        
        self.height_slider.on_changed(self.height_changed)
        
        self.filter_cloud(self.percentile_filter.percentile_vals[-1])

        
        # self.height_changed(-5)
        
        # Connect click event.
        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)

        
        self.plot_data()
    
    def on_mouse_press(self, event):
        if event.inaxes == self.area_ax:
            
            # Check if its nearby any point.
            pt_press = np.array([event.xdata, event.ydata])
            dist_mat = np.linalg.norm(self.height_to_area - pt_press, axis=1)
            if dist_mat.min() > 0.5:
                return
            
            selected_idx = np.argmin(dist_mat)
            self.show_signal_comparison(self.height_to_area[selected_idx, 0])
        
    def filter_cloud(self, val):
        self.filtered_cloud = self.percentile_filter.get_pts_over_percentile(val)
        self.plot_3d_data()
        self.fill_area_plot()
        self.height_changed(self.height_slider.val)
        self.draw()
        
    def fill_area_plot(self):
        """
        FIXME - Assumes there is a single cluster. Find Solution to the case there are several.
        """
        distinct_heights = np.unique(self.filtered_cloud[:, 2])
        areas = []
        valid_heights = []
        
        for h in distinct_heights:
            rel_idxs = np.where(self.filtered_cloud[:, 2] == h)[0]
            rel_pts = self.filtered_cloud[rel_idxs, :2]
            
            try:
                curr_area = ConvexHull(rel_pts).area
                valid_heights.append(h)
                areas.append(curr_area)
            except Exception:
                continue
            
        # Update the optimal height.
        optimal_height_idx = np.argmax(np.array(areas))
        self.optimal_height = valid_heights[optimal_height_idx]
            
        self.area_ax.clear()
        self.area_ax.plot(valid_heights, areas, marker='*')
        self.height_to_area = np.vstack((np.array(valid_heights), np.array(areas))).T
        
        self.show_signal_comparison(self.optimal_height)
    
    def show_signal_comparison(self, desired_height):
        """
        Show the comparison between the normalized scan values and the normalized simulated signal.
        """
        if self.shown_height_scatter is not None:
            self.shown_height_scatter.remove()
        
        desired_idx = np.argmin(np.abs(self.height_to_area[:, 0] - desired_height))
        self.shown_height_scatter = self.area_ax.scatter(desired_height, self.height_to_area[desired_idx, 1], c='red')
        
        # Find the optimal dipole and get the simulative signal.
        h_idxs = np.where(self.filtered_cloud[:, 2] == desired_height)[0]
        rel_pts = self.filtered_cloud[h_idxs]
        opt_pt_idx = np.argmax(rel_pts[:, 3])
        opt_pt = rel_pts[opt_pt_idx]
        
        sim_vals = sim_dipole(self.scenario.scan_pts, opt_pt[:3], np.array([0, 1, -1]))
        # Get normalized original signal.
        copied_scan_vals = np.copy(self.scenario.raw_signal)
        copied_scan_vals -= 4.5e6
        
        
        self.sig_ax.clear()
        self.sig_ax.plot(copied_scan_vals, label='Original Signal', c='blue')
        
        
        self.sig_ax.plot(((sim_vals-sim_vals.min())/(sim_vals.max()-sim_vals.min())) * (copied_scan_vals.max()-copied_scan_vals.min())
                         + copied_scan_vals.min(), label='Simulative Signal', c='red')
        self.draw()

        
    
    def plot_3d_data(self):
        self.pt_cloud_ax.clear()
        scan_pts = self.scenario.scan_pts

        
        self.pt_cloud_ax.scatter(scan_pts[:, 0], scan_pts[:, 1],
                            np.zeros((scan_pts.shape[0])), c='red')

        if self.filtered_cloud is not None:
            self.pt_cloud_ax.scatter(self.filtered_cloud[:, 0], self.filtered_cloud[:, 1],
                                     self.filtered_cloud[:, 2], c=self.filtered_cloud[:, 3])

 
        
    def plot_data(self):
        self.plot_2d_view()
        self.plot_3d_data()
        self.draw()
    
    def plot_2d_view(self):
        self.view_2d_ax.contourf(self.scenario.search_x, self.scenario.search_y,
                                    self.interp_data.T, cmap='jet', levels=200,
                                    zorder=1)
        
        for mag_obj in self.scenario.mag_objects.values():
            if len(mag_obj.vertices) == 1:
                self.view_2d_ax.scatter(
                                mag_obj.vertices[0, 0], mag_obj.vertices[0, 1], zorder=1e2, c='k')
            else:
                rect = np.vstack((mag_obj.vertices, mag_obj.vertices[0]))
                self.view_2d_ax.plot(rect[:, 0], rect[:, 1], zorder=1e2, c='k')[0]

            
 
        
    def height_changed(self, val):
        if self.filtered_cloud is None:
            return
        
        # Receive all the pts in the given height.
        idxs = np.where(self.filtered_cloud[:, 2] - val < 1e-1)[0]
        self.view_2d_ax.clear()
        self.plot_2d_view()
        self.view_2d_ax.scatter(self.filtered_cloud[idxs, 0], self.filtered_cloud[idxs, 1],
                                c=self.filtered_cloud[idxs, 3], zorder=1e2-1)
        self.draw()


    # FIXME - Duplicated code from simulation canvas.
    def draw_mag_objects(self):
        """
        Draw all the relevant magnetic objects.
        - Dipole - Single black dot.
        - Rectangle - Add a rectangle patch.
        """
        for obj_id, mag_obj in self.scenario.mag_objects.items():
            self.draw_mag_object(mag_obj)
                
    def draw_mag_object(self, mag_obj, color='k'):
        if len(mag_obj.vertices) == 1:
            self.interp_ax.scatter(
                            mag_obj.vertices[0, 0], mag_obj.vertices[0, 1], c=color, zorder=1e2)
        else:
            rect = np.vstack((mag_obj.vertices, mag_obj.vertices[0]))
            self.mag_obj_plots[mag_obj.obj_id] = self.interp_ax.plot(rect[:, 0], rect[:, 1], c=color,
                                                                     zorder=1e2)[0]



