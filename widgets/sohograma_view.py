import PyQt5.QtWidgets as Qtw
from widgets.plots.sohograma_canvas import SohogramaCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
        


class SohogramaView(Qtw.QWidget):
    
    def __init__(self, parent, scenario, pt_cloud, interp_data, z_min, z_max) -> None:
        super().__init__(parent)
        
        self.sohograma_canvas = SohogramaCanvas(scenario, pt_cloud, interp_data, z_min, z_max)
        self.toolbar = None
        self.initUI()

    def reset_toolbar(self):
        self.toolbar = NavigationToolbar(self.sohograma_canvas, self)

    def initUI(self):
        main_layout = Qtw.QHBoxLayout()
        main_layout.addWidget(self.sohograma_canvas)
        self.setLayout(main_layout)


        
    