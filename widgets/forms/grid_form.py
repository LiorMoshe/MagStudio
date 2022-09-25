import PyQt5.QtWidgets as Qtw
import numpy as np
from utils.scan_path_generator import generate_grid


DEFAULT_X_GRID = 40

DEFAULT_Y_GRID = 40

DEFAULT_RESOLUTION = 1


class GridForm(Qtw.QWidget):
    
    def __init__(self, parent, on_filled) -> None:
        super().__init__(parent)
        
        self.on_filled = on_filled
        
        self.x_edit = None
        self.y_edit = None
        self.resolution_edit = None
    
        self.initUI()
    
    def initUI(self):
        layout = Qtw.QFormLayout()
        
        self.x_edit = Qtw.QLineEdit(str(DEFAULT_X_GRID))
        self.x_edit.returnPressed.connect(self.update_scan_params)
        
        self.y_edit = Qtw.QLineEdit(str(DEFAULT_Y_GRID))
        self.y_edit.returnPressed.connect(self.update_scan_params)
        
        self.resolution_edit = Qtw.QLineEdit(str(DEFAULT_RESOLUTION))
        self.resolution_edit.returnPressed.connect(self.update_scan_params)

        layout.addRow('X: ', self.x_edit)
        layout.addRow('Y: ', self.y_edit)
        layout.addRow('Resolution: ', self.resolution_edit)
       
        self.setLayout(layout)
        
    def update_scan_params(self):
        scan_pts = self.evaluate_scan_path()
        if scan_pts is not None:
            self.on_filled(scan_pts)
 
        
   
    def evaluate_scan_path(self):
        x_size = int(self.x_edit.text())
        y_size = int(self.y_edit.text())
        resolution = float(self.resolution_edit.text())

        search_x = np.arange(-x_size//2, x_size//2+1, step=resolution)
        search_y = np.arange(-y_size//2, y_size//2+1, step=resolution)
        return generate_grid(search_x, search_y)

        