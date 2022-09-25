import PyQt5.QtWidgets as Qtw
import numpy as np
from utils.scan_path_generator import generate_spiral_scan


DEFAULT_LINE_DIST = 2

DEFAULT_NUM_LINES = 5

DEFAULT_ANGULAR_RES = 15


class SpiralForm(Qtw.QWidget):
    
    def __init__(self, parent, on_filled, on_mark) -> None:
        super().__init__(parent)
        self.on_filled = on_filled
        self.on_mark = on_mark
        
        self.center_pt = None
        
        # Relevant line edits.
        self.line_dist_edit = None
        self.num_lines_edit = None
        self.samp_dist_edit = None
        self.initUI()
        
    def initUI(self):
        layout = Qtw.QVBoxLayout()
        container = Qtw.QWidget()
        path_props_form = Qtw.QFormLayout()
        
        self.line_dist_edit = Qtw.QLineEdit(str(DEFAULT_LINE_DIST))
        self.num_lines_edit = Qtw.QLineEdit(str(DEFAULT_NUM_LINES))
        self.samp_dist_edit = Qtw.QLineEdit(str(DEFAULT_ANGULAR_RES))
        
        self.line_dist_edit.returnPressed.connect(self.update_scan_params)
        self.num_lines_edit.returnPressed.connect(self.update_scan_params)
        self.samp_dist_edit.returnPressed.connect(self.update_scan_params)
        
        
        self.center_pt_button = Qtw.QPushButton('Mark Center Point')
        self.center_pt_button.setCheckable(True)
        self.center_pt_button.clicked.connect(self.toggle_mark_pt)
        layout.addWidget(self.center_pt_button)
        
        # path_props_form.addRow(self.center_pt_button , self.center_edit)
        path_props_form.addRow('Line Distance: ', self.line_dist_edit)
        path_props_form.addRow('Number of lines: ', self.num_lines_edit)
        path_props_form.addRow('Angular Resolution: ', self.samp_dist_edit)
        container.setLayout(path_props_form)
        layout.addWidget(container)
        
        self.setLayout(layout)
    
    def set_pt(self, pt):
        self.center_pt = pt
    
    def update_scan_params(self):
        scan_pts = self.evaluate_scan_path()
        if scan_pts is not None:
            self.on_filled(scan_pts)
        pass
    
    def evaluate_scan_path(self):
        if self.center_pt is None:
            return
        
        return generate_spiral_scan(center_pt=self.center_pt,
                                        line_dist=float(self.line_dist_edit.text()),
                                        num_lines=float(self.num_lines_edit.text()),
                                        angle_resolution=float(self.samp_dist_edit.text()) * np.pi/180)

 
        
    def toggle_mark_pt(self):
        self.on_mark(self.center_pt_button.isChecked())