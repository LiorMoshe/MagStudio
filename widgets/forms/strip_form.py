import PyQt5.QtWidgets as Qtw
import numpy as np
from utils.scan_path_generator import generate_strip_scan


DEFAULT_STRIP_LENGTH = 10

DEFAULT_LINE_DIST = 2

DEFAULT_NUM_LINES = 5

DEFAULT_DIST_RES = 1


class StripForm(Qtw.QWidget):
    
    def __init__(self, parent, on_filled, on_mark) -> None:
        super().__init__(parent)
        self.on_filled = on_filled
        self.on_mark = on_mark
        
        self.start_pt = None
        
        # Relevant line edits.
        self.line_length_edit = None
        self.line_dist_edit = None
        self.num_lines_edit = None
        self.samp_dist_edit = None
        self.initUI()
        
    def initUI(self):
        layout = Qtw.QVBoxLayout()
        container = Qtw.QWidget()
        path_props_form = Qtw.QFormLayout()
        
        self.line_length_edit = Qtw.QLineEdit(str(DEFAULT_STRIP_LENGTH))
        self.line_dist_edit = Qtw.QLineEdit(str(DEFAULT_LINE_DIST))
        self.num_lines_edit = Qtw.QLineEdit(str(DEFAULT_NUM_LINES))
        self.samp_dist_edit = Qtw.QLineEdit(str(DEFAULT_DIST_RES))
        
        self.line_length_edit.returnPressed.connect(self.update_scan_params)
        self.line_dist_edit.returnPressed.connect(self.update_scan_params)
        self.num_lines_edit.returnPressed.connect(self.update_scan_params)
        self.samp_dist_edit.returnPressed.connect(self.update_scan_params)
        
        
        self.start_pt_button = Qtw.QPushButton('Mark Start Point')
        self.start_pt_button.setCheckable(True)
        self.start_pt_button.clicked.connect(self.toggle_mark_pt)
        
        layout.addWidget(self.start_pt_button)
        
        # path_props_form.addRow(self.center_pt_button , self.center_edit)
        path_props_form.addRow('Strip Length: ', self.line_length_edit)
        path_props_form.addRow('Strip Distance: ', self.line_dist_edit)
        path_props_form.addRow('Number of strips: ', self.num_lines_edit)
        path_props_form.addRow('Sampling distance: ', self.samp_dist_edit)
        container.setLayout(path_props_form)
        
        layout.addWidget(container)
        self.setLayout(layout)
    
    def set_pt(self, pt):
        self.start_pt = pt
    
    def update_scan_params(self):
        scan_pts = self.evaluate_scan_path()
        if scan_pts is not None:
            self.on_filled(scan_pts)
    
    def evaluate_scan_path(self):
        if self.start_pt is None:
            return
        
        return generate_strip_scan(start_pt=self.start_pt,
                                   strip_length=float(self.line_length_edit.text()),
                                   strips_dist=float(self.line_dist_edit.text()),
                                   num_strips=int(self.num_lines_edit.text()),
                                   sample_dist=float(self.samp_dist_edit.text()))
    
    
    def toggle_mark_pt(self):
        self.on_mark(self.start_pt_button.isChecked())
    
        
