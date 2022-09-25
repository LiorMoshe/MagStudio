from matplotlib.widgets import Cursor
import numpy as np


"""
Cursor that synchronized a gps 2d plot and a signal of measurements.
"""

def bind_gps_to_signal(gps_cursor, signal_cursor, raw_signal, gps_coords):
    """_summary_
    Bind two extendable cursors.
    Args:
        gps_cursor (_type_): _description_
        signal_cursor (_type_): _description_
        raw_signal (_type_): _description_
        gps_coords (_type_): _description_
    """
    
    def post_move_signal(event):
        if event.xdata is None or event.ydata is None:
            return 

        xdata = int(event.xdata)
        if xdata < 0 or xdata > len(raw_signal)-1:
            return
        
        coord = gps_coords[xdata]
        gps_cursor.move_to(coord[0], coord[1])
    
    def post_move_gps(event):
        # if event.xdata is None or event.ydata is None:
        #     return 
        
        dist_mat = np.linalg.norm(gps_coords-np.array([event.xdata, event.ydata]), axis=1)
        coord_idx = np.argmin(dist_mat)
        if dist_mat[coord_idx] > 1:
            return

        signal_cursor.move_to(coord_idx, 0)
   
    gps_cursor.post_move = post_move_gps
    signal_cursor.post_move = post_move_signal
        
        
class ExtendableCursor(Cursor):
    
    def __init__(self, ax, horizOn=True, vertOn=True, useblit=False, post_move=None,
                 **lineprops) -> None:
        super().__init__(ax, horizOn, vertOn, useblit,
                 **lineprops)
        
        self.post_move = post_move
        
    def onmove(self, event):
        
        super().onmove(event)
        
        if event.inaxes == self.ax and self.post_move is not None:
            self.post_move(event)
    
    def move_to(self, x, y):
        if self.vertOn:
            self.linev.set_xdata((x, x))
            self.linev.set_visible(True)

        if self.horizOn:
            self.lineh.set_ydata((y, y))
            self.lineh.set_visible(True)
            
        self._update()
        