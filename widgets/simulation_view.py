import PyQt5.QtWidgets as Qtw
from widgets.plots.sim_canvas import SimulationCanvas
from widgets.scan_designer import ScanDesigner
from widgets.sim_controller import SimulationController
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar



class SimulationView(Qtw.QWidget):
    
    def __init__(self, parent, on_server_response) -> None:
        super().__init__(parent)
        
        self.sim_canvas = SimulationCanvas()
        self.scan_designer = ScanDesigner(self, self.sim_canvas, on_set_scan=self.inject_scan)
        self.sim_controller = SimulationController(self, self.sim_canvas,
                                                   on_server_response=on_server_response)
        
        # self.toolbar = NavigationToolbar(self.sim_canvas, self)
        self.toolbar = None


        # set the layout
        self.initUI()
        
    def reset_toolbar(self):
        self.toolbar = NavigationToolbar(self.sim_canvas, self)

        
    def get_scenario(self):
        return self.sim_canvas.scenario
    
    def get_interp_data(self):
        return self.sim_canvas.interp_data
        
    def inject_scan(self, scenario):
        self.tab_widget.removeTab(0)
        self.sim_canvas.set_scenario(scenario)
        self.sim_controller.bind_mag_field_changed_event()
        self.tab_widget.addTab(self.sim_controller, 'Simulate Objects')
 
    def initUI(self):
        left_layout = Qtw.QVBoxLayout()
        self.tab_widget = Qtw.QTabWidget()
        self.tab_widget.addTab(self.scan_designer, 'Design Scan')
        # self.tab_widget.addTab(self.sim_controller, 'Simulate Objects')
        left_layout.addWidget(self.tab_widget)
        left_widget = Qtw.QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setStyleSheet('''
            QLabel#h1{
                font-size:15px;
                font-weight:800;
                text-align:left;
            }
            
            QLabel#h2{
                font-size:12px;
                font-weight:500;
                text-align:left;
            }

        ''')
        
        # left_widget_size_policy = Qtw.QSizePolicy()
        # left_widget_size_policy.setHorizontalStretch(1)
        
        # sim_canvas_size_policy = Qtw.QSizePolicy()
        # sim_canvas_size_policy.setHorizontalStretch(2)

        main_layout = Qtw.QHBoxLayout()
        main_layout.addWidget(left_widget)
        
        main_layout.addWidget(self.sim_canvas)
        self.setLayout(main_layout)

        
        
    