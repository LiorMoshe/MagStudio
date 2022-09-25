import matplotlib
from widgets.scan_designer import ScanDesigner
from widgets.sim_controller import SimulationController
from widgets.simulation_view import SimulationView
from widgets.sohograma_view import SohogramaView

matplotlib.use('Qt5Agg')
from PyQt5.QtWidgets import QApplication, QWidget
import PyQt5.QtWidgets as Qtw
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from widgets.plots.sim_canvas import SimulationCanvas
from consts import *

class Window(Qtw.QMainWindow):
    def __init__(self):
        super().__init__()
  
        # setting title
        self.setWindowTitle("MagStudio")
  
        # setting geometry
        self.setGeometry(100, 100, 600, 400)

        
        self.mag_obj_list = None
        
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        # self.toolbar = NavigationToolbar(self.sim_canvas, self)


        # # set the layout
        # self.addToolBar(self.toolbar)
        
        self.tab_widget = None
        self.toolbar = None
 
        # showing all the widgets
        self.initUI()
        self.showMaximized()
        self.show()
    
    def on_sohograma_finish(self, pt_cloud, z_min, z_max):
        """
        Add a new tab presenting the sohograma results.
        """
        soh_view = SohogramaView(self, scenario=self.sim_view.get_scenario(), pt_cloud=pt_cloud,
                                 interp_data=self.sim_view.get_interp_data(), z_min=z_min, z_max=z_max)
        self.tab_widget.addTab(soh_view, 'SohogramaView')
        
        # Jump to the last tab.
        self.tab_widget.setCurrentIndex(self.tab_widget.count()-1)
    
    
      
    def initUI(self):
        layout = Qtw.QHBoxLayout()
        self.tab_widget = Qtw.QTabWidget()
        
        self.tab_widget.currentChanged.connect(self.on_tab_change)
        self.sim_view = SimulationView(self, self.on_sohograma_finish)
        
        # self.toolbar = self.sim_view.toolbar
        # self.addToolBar(self.sim_view.toolbar)
        
        self.tab_widget.addTab(self.sim_view, 'Simulation View')
        layout.addWidget(self.tab_widget)
        
        main_widget = Qtw.QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
    def on_tab_change(self, idx):
        self.removeToolBar(self.toolbar)
        self.tab_widget.currentWidget().reset_toolbar()
        self.toolbar = self.tab_widget.currentWidget().toolbar
        self.addToolBar(self.toolbar)
 
        
        
if __name__=="__main__":
    # create pyqt5 app
    App = QApplication(sys.argv)
    
    # create the instance of our Window
    window = Window()
    
    # start the app
    sys.exit(App.exec())