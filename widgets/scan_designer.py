import PyQt5.QtWidgets as Qtw
import numpy as np
from simulations.scenario import GridRange, Scenario
from widgets.forms.grid_form import GridForm
from widgets.forms.spiral_form import SpiralForm
from widgets.forms.strip_form import StripForm

DEFAULT_GRID_X = '40'

DEFAULT_GRID_Y = '40'

DEFAULT_LINE_DIST = 2

DEFAULT_NUM_LINES = 5

DEFAULT_ANGULAR_RES = 15

class ScanDesigner(Qtw.QWidget):
    """_summary_
    Widget that allows users to design scan paths over the simulation canvas.
    Args:
        Qtw (_type_): _description_
    """
    
    def __init__(self, parent, sim_canvas, on_set_scan) -> None:
        super().__init__(parent)
        
        self.sim_canvas = sim_canvas
        self.on_set_scan = on_set_scan
        
        # Contains the path collection of the previewed scan path.
        self.previewed_scan_plot = None

        self.center_button_cid = None
        
        # Relevant forms.
        self.spiral_form = SpiralForm(self, on_filled=self.replot_previewed_path,
                                      on_mark=self.select_pt)
        
        self.strip_form = StripForm(self, on_filled=self.replot_previewed_path,
                                    on_mark=self.select_pt)
        
        self.grid_form = GridForm(self, on_filled=self.replot_previewed_path)
        
    
        self.form_map = {0: self.spiral_form, 1: self.strip_form, 2: self.grid_form}
        
        self.displayed_form = self.spiral_form
        
        self.current_form = self.spiral_form
        
        # Properties for the scan path.
        self.line_dist_edit = None
        self.num_lines_edit = None
        self.samp_dist_edit = None
        
        # Dropdown for path type selection.
        self.path_type_dropdown = None
        
        self.set_scan_button = None
        
        self.grid_range = None
        
        # Holds a list of the scan paths designed by the user.
        # self.scan_paths = []
        
        self.initUI()
        
    def initUI(self):
        layout = Qtw.QVBoxLayout()
        
        # Header.
        # design_scans_label = Qtw.QLabel("Design Scan Path")
        # design_scans_label.setObjectName("h1")
        # layout.addWidget(design_scans_label)
       
        total_scan_type_widget = Qtw.QWidget()
        total_scan_type_layout = Qtw.QVBoxLayout()
        main_scan_type_widget = Qtw.QWidget()
        main_scan_type_layout = Qtw.QVBoxLayout()
        
        # Path type configuration.
        type_path_left = Qtw.QWidget()
        type_path_layout = Qtw.QHBoxLayout()
        type_path_label = Qtw.QLabel('Select Path Type')
        type_path_label.setObjectName('h2')
        self.path_type_dropdown = Qtw.QComboBox()
        self.path_type_dropdown.addItems(['Spiral', 'Strip', 'Grid'])
        self.path_type_dropdown.currentIndexChanged.connect(self.changed_selected_path_type)
        type_path_layout.addWidget(type_path_label)
        type_path_layout.addWidget(self.path_type_dropdown)
        type_path_left.setLayout(type_path_layout)
        main_scan_type_layout.addWidget(type_path_left)
        
        type_path_right = Qtw.QWidget()
        path_props_form = Qtw.QFormLayout()
        # path_props_form.
        
        self.line_dist_edit = Qtw.QLineEdit(str(DEFAULT_LINE_DIST))
        self.num_lines_edit = Qtw.QLineEdit(str(DEFAULT_NUM_LINES))
        self.samp_dist_edit = Qtw.QLineEdit(str(DEFAULT_ANGULAR_RES))
        
        self.line_dist_edit.returnPressed.connect(self.replot_previewed_path)
        self.num_lines_edit.returnPressed.connect(self.replot_previewed_path)
        self.samp_dist_edit.returnPressed.connect(self.replot_previewed_path)
        
        
        self.center_pt_button = Qtw.QPushButton('Mark Center Point')
        self.center_pt_button.setCheckable(True)
        self.center_pt_button.clicked.connect(self.select_pt)

        path_props_form.addRow('Line Distance: ', self.line_dist_edit)
        path_props_form.addRow('Number of lines: ', self.num_lines_edit)
        path_props_form.addRow('Sampling distance: ', self.samp_dist_edit)
        type_path_right.setLayout(path_props_form)
        
        # Hide the non-selected widgets.
        main_scan_type_layout.addWidget(self.spiral_form)
        main_scan_type_layout.addWidget(self.strip_form)
        main_scan_type_layout.addWidget(self.grid_form)
        
        self.strip_form.hide()
        self.grid_form.hide()
        # main_scan_type_layout.addWidget(type_path_right)
        main_scan_type_widget.setLayout(main_scan_type_layout)
        total_scan_type_layout.addWidget(main_scan_type_widget)
        
        self.set_scan_button = Qtw.QPushButton('Set Scan Path')
        self.set_scan_button.setDisabled(True)
        self.set_scan_button.clicked.connect(self.set_scan_path)
        
        
        total_scan_type_layout.addWidget(self.set_scan_button)
        total_scan_type_widget.setLayout(total_scan_type_layout)
        # total_scan_type_widget.lay
        layout.addWidget(total_scan_type_widget)
        self.setLayout(layout)

    def set_scan_path(self):
        scan_pts = self.current_form.evaluate_scan_path()
        scan_path = Scenario(scan_pts)
        
        if self.previewed_scan_plot is not None:
            self.previewed_scan_plot.remove()
        
        if self.center_button_cid:
            self.sim_canvas.fig.canvas.mpl_disconnect(self.center_button_cid)
            
        self.on_set_scan(scan_path)
        
    
    def select_pt(self, is_checked):
        if is_checked:
            self.center_button_cid = self.sim_canvas.fig.canvas.mpl_connect('button_press_event', self.set_pt)
        else:
            self.sim_canvas.fig.canvas.mpl_disconnect(self.center_button_cid)

    
    def set_pt(self, event):
        if event.inaxes == self.sim_canvas.interp_ax:
            self.current_form.set_pt([event.xdata, event.ydata])
            
            # Enable the add scan button.
            self.set_scan_button.setDisabled(False)

            self.replot_previewed_path(self.current_form.evaluate_scan_path())
            self.sim_canvas.draw()
        
        
    def replot_previewed_path(self, scan_path):
        # scan_path = self.evaluate_scan_path()
        # if scan_path is None:
            # return

        if self.previewed_scan_plot is not None:
                self.previewed_scan_plot.remove()
                
        self.previewed_scan_plot = self.sim_canvas.interp_ax.scatter(scan_path[:, 0], scan_path[:, 1], s=20, c='pink')
        self.grid_range = GridRange(x_min=scan_path[:, 0].min(),
                                        x_max=scan_path[:, 0].max(),
                                        y_min=scan_path[:, 1].min(),
                                        y_max=scan_path[:, 1].max())
       
        self.sim_canvas.set_grid_range(self.grid_range)
        
        
    def changed_selected_path_type(self, index):
        self.current_form.hide()
        
        self.current_form = self.form_map[index]
        self.current_form.show()