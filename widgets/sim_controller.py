import PyQt5.QtWidgets as Qtw
from consts import *
from widgets.mag_list import MagneticObjectsList
from widgets.plots.sim_canvas import SimMode
from simulations.mag_object import MagProps
from simulations.mag_object import MagneticObject
from interps.interps import InterpType
from PyQt5.QtCore import Qt
from transforms.rtp import rtp
import math
import requests
import numpy as np
import json

# Insert here the url of your server if you're running your backend remotely.
SERVER_URL = 'http://127.0.0.1:5000/sohograma' 


class SimulationController(Qtw.QWidget):
    
    def __init__(self, parent, sim_canvas, on_server_response) -> None:
        super().__init__(parent)
        self.sim_canvas = sim_canvas
        self.sim_canvas.set_mag_props_query(self.get_mag_properties)
        self.sim_canvas.set_mag_object_listener(self.add_object_to_list)
        self.v_min = None
        self.v_max = None
        
        self.on_server_response = on_server_response

        self.initUI()
    
    def bind_mag_field_changed_event(self):
        self.sim_canvas.scenario.set_field_update_listener(self.mag_field_changed)
        
    def add_object_to_list(self, mag_object):
        self.mag_obj_list.addItem(str(mag_object))
    
    def mag_field_changed(self, min_field, max_field):
        print(f'Added Object: Min:{min_field} Max: {max_field}')
        
        # sliders work with integers.
        min_field = math.floor(min_field)
        max_field = math.ceil(max_field)
        
        self.vmin_slider.setRange(min_field, 
                                  max_field)
        self.vmax_slider.setRange(min_field,
                                  max_field)
        
        self.vmin_slider.setValue(min_field)
        self.vmax_slider.setValue(max_field)

    def get_mag_properties(self):
        return float(self.moment_edit.text()), float(self.depth_edit.text()), \
                float(self.zdim_edit.text())
                
    def flip_sim_mode(self, i):
        self.zdim_edit.setText(DEFAULT_MAGOBJ_ZDIM if i == SimMode.MAGOBJ.value else DEFAULT_DIPOLE_ZDIM)
        self.sim_canvas.flip_simulation_mode(i)

    def recalc_field(self):
        selected_id = self.mag_obj_list.get_selected_obj_id()
        if selected_id is None:
            return 
        
        self.sim_canvas.update_mag_properties(
            MagProps(moment=float(self.moment_edit.text()),
                     depth=float(self.depth_edit.text()),
                     zdim=float(self.zdim_edit.text())),
                selected_id)
 

    def object_selection_changed(self):
        """
        Once an object was selected - update the values in the forms and highlight it.
        FIXME - Assumes only a single object can be selected, disable multiselection in the QListWidget.
        """
        if len(self.mag_obj_list.selectedIndexes()) == 0:
            return

        selected_id = int(self.mag_obj_list.selectedIndexes()[0].data().split('-')[1])
        mag_obj = self.sim_canvas.get_magnetic_object(selected_id)
        
        # Update the forms.
        self.moment_edit.setText(str(mag_obj.scalar_moment))
        
        # FIXME - Currently the scan points are zero-adjusted so depth=max_z - will be changed.
        self.depth_edit.setText(str(mag_obj.depth))
        self.zdim_edit.setText(str(mag_obj.z_dim))
        self.sim_canvas.set_selected_id(selected_id)

    def initUI(self):
        layout = Qtw.QVBoxLayout()
        sim_objects_label = Qtw.QLabel("Simulate Magnetic Objects")
        sim_objects_label.setObjectName('h1')
        self.sim_mode_button = Qtw.QPushButton("Simulate")
        self.sim_mode_button.setCheckable(True)
        self.sim_mode_button.clicked.connect(self.sim_canvas.toggle_sim_mode)
        self.sim_mode_button.setShortcut('s')
        
        # self.sim_mode_button.setObjectName('SimHeader')
        # left_layout.setSpacing(1)
        # Selection dropdown.
        self.sim_mode_selection = Qtw.QComboBox()
        self.sim_mode_selection.addItems(['Dipole', 'Rectangle'])
        self.sim_mode_selection.currentIndexChanged.connect(self.flip_sim_mode)
        
        simulate_bar_layout = Qtw.QHBoxLayout()
        simulate_bar_layout.addWidget(self.sim_mode_button)
        simulate_bar_layout.addWidget(self.sim_mode_selection)
        simulate_bar_widget = Qtw.QWidget()
        simulate_bar_widget.setLayout(simulate_bar_layout)
        layout.addWidget(sim_objects_label)
        layout.addWidget(simulate_bar_widget)
        
        # Initialize list which will hold all the magnetic objects.
        self.mag_obj_list = MagneticObjectsList(self, on_delete=self.sim_canvas.delete_mag_object,
                                                on_hide=self.sim_canvas.toggle_hidden_object)
        self.mag_obj_list.itemSelectionChanged.connect(self.object_selection_changed)
        layout.addWidget(self.mag_obj_list)
        
        self.mag_prop_widget = Qtw.QWidget()
        mag_prop_layout = Qtw.QFormLayout()
        self.moment_edit = Qtw.QLineEdit(DEFAULT_MOMENT)
        self.depth_edit = Qtw.QLineEdit(DEFAULT_DEPTH)
        self.zdim_edit = Qtw.QLineEdit(DEFAULT_DIPOLE_ZDIM)
        self.moment_edit.returnPressed.connect(self.recalc_field)
        self.depth_edit.returnPressed.connect(self.recalc_field)
        self.zdim_edit.returnPressed.connect(self.recalc_field)

        # Add user form for magnetic properties.
        mag_prop_layout.addRow('Moment: ', self.moment_edit)
        mag_prop_layout.addRow('Depth: ', self.depth_edit)
        mag_prop_layout.addRow('Z-Dimension: ', self.zdim_edit)
        self.mag_prop_widget.setLayout(mag_prop_layout)
        layout.addWidget(self.mag_prop_widget)
        
        recalc_field_button = Qtw.QPushButton('Recalculate Field')
        recalc_field_button.clicked.connect(self.recalc_field)
        layout.addWidget(recalc_field_button)
        
        interp_container = Qtw.QWidget()
        interp_layout = Qtw.QHBoxLayout()
        interp_layout.addWidget(Qtw.QLabel('Interpolation: '))
        
        interp_dropdown = Qtw.QComboBox()
        interp_dropdown.currentIndexChanged.connect(self.changed_interp)
        interp_dropdown.addItems([interp.value.display_str for interp in InterpType])
        interp_layout.addWidget(interp_dropdown)
        interp_container.setLayout(interp_layout)
        layout.addWidget(interp_container)
        
        slider_container = Qtw.QWidget()
        slider_layout = Qtw.QVBoxLayout()

        min_slider_container = Qtw.QWidget()
        max_slider_container = Qtw.QWidget()

        min_slider_layout = Qtw.QHBoxLayout()
        max_slider_layout = Qtw.QHBoxLayout()
        min_field_label = Qtw.QLabel('Min Field')
        max_field_label = Qtw.QLabel('Max Field')
        min_field_label.setObjectName('h2')
        max_field_label.setObjectName('h2')
        
        min_slider_layout.addWidget(min_field_label)
        self.vmin_slider = Qtw.QSlider(Qt.Orientation.Horizontal, self)
        self.vmin_slider.valueChanged.connect(self.vmin_slider_changed)
        self.vmax_slider = Qtw.QSlider(Qt.Orientation.Horizontal, self)
        self.vmax_slider.valueChanged.connect(self.vmax_slider_changed)
        min_slider_layout.addWidget(self.vmin_slider)
        max_slider_layout.addWidget(max_field_label)
        
        max_slider_layout.addWidget(self.vmax_slider)
        min_slider_container.setLayout(min_slider_layout)
        max_slider_container.setLayout(max_slider_layout)
        slider_layout.addWidget(min_slider_container)
        slider_layout.addWidget(max_slider_container)
        
        slider_container.setLayout(slider_layout)
        layout.addWidget(slider_container)

        transforms_container = Qtw.QWidget()
        transforms_layout = Qtw.QHBoxLayout()
        transforms_header = Qtw.QLabel('Transformations')
        transforms_header.setObjectName('h2')
        
        self.rtp_button = Qtw.QPushButton('RTP')
        self.rtp_button.setCheckable(True)
        self.rtp_button.clicked.connect(self.flip_rtp_mode)
        transforms_layout.addWidget(transforms_header)
        transforms_layout.addWidget(self.rtp_button)
        transforms_container.setLayout(transforms_layout)
        
        layout.addWidget(transforms_container)        
        
        self.server_request_button = Qtw.QPushButton('Inversion')
        self.server_request_button.clicked.connect(self.request_from_server)
        layout.addWidget(self.server_request_button)
        
        
        reset_button = Qtw.QPushButton('Reset')
        reset_button.clicked.connect(self.reset_state)
        layout.addWidget(reset_button)
 
        self.setLayout(layout)
        
    def request_from_server(self):
        if self.sim_canvas.scenario is None:
            return
        
        
        soh_inp = self.sim_canvas.scenario.get_sohograma_input(-20, -5)
        pt_cloud = json.loads(requests.post(SERVER_URL, json=soh_inp).content.decode())
        pt_cloud = np.array(pt_cloud['pt_cloud'])
        self.on_server_response(pt_cloud, -20, -5)
        
    
    def flip_rtp_mode(self):
        self.sim_canvas.flip_rtp_mode()
        if self.rtp_button.isChecked():
            # Show the rtp of the interpolation and the signal.
            rtp_vals = rtp(self.sim_canvas.scenario.search_x, self.sim_canvas.scenario.search_y,
                self.sim_canvas.interp_data)
            
            self.sim_canvas.interp_data = rtp_vals
            
            # Update boundaries to match the rtp values.
            self.sim_canvas.scenario.min_field = rtp_vals.min()
            self.sim_canvas.scenario.max_field = rtp_vals.max()
            
            self.mag_field_changed(rtp_vals.min(), rtp_vals.max())
        else:
            # Go back.
            self.sim_canvas.scenario.reevaluate_mag_field()
            self.sim_canvas.update_interp_data()
            
            # Reupdate the boundaries back.
            self.sim_canvas.scenario.update_boundaries()
        
        self.sim_canvas.plot_data()
            

    def vmin_slider_changed(self, value):
        self.sim_canvas.update_clim(vmin=value, vmax=self.vmax_slider.value())

    
    def vmax_slider_changed(self, value):
        self.sim_canvas.update_clim(vmin=self.vmin_slider.value(), vmax=value)
        
    def changed_interp(self, interp_idx):
        self.sim_canvas.set_interp_type(list(InterpType)[interp_idx])
        
    def reset_state(self):
        MagneticObject.ID = 1
        self.mag_obj_list.clear()
        self.sim_canvas.reset_state()
        self.moment_edit.setText(DEFAULT_MOMENT)
        self.zdim_edit.setText(DEFAULT_DIPOLE_ZDIM)
        self.depth_edit.setText(DEFAULT_DEPTH)
        self.sim_mode_button.setChecked(False)
        self.sim_mode_selection.setCurrentIndex(SimMode.DIPOLE.value)
        
        self.vmin_slider.setValue(math.floor(self.sim_canvas.scenario.min_field))
        self.vmax_slider.setValue(math.ceil(self.sim_canvas.scenario.max_field))

 