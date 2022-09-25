from flask import Flask, request
from localizations.sohograma import SohogramaInput, magnetic_inversion
import numpy as np
from flask import jsonify


"""
Flask server which will fill requests of GUI's for cuda-related functions.
"""

app = Flask(__name__)

EARTH_FIELD = np.array([0, 1, -1])

@app.route('/sohograma', methods=['POST'])
def get_pt_cloud():
    scenario_data = request.json
    # print(f'Received data! {scenario_data}')

    search_x = np.arange(scenario_data['grid_range']['x_min'], scenario_data['grid_range']['x_max'])
    search_y = np.arange(scenario_data['grid_range']['y_min'], scenario_data['grid_range']['y_max'])
    
    scan_pts = np.array(scenario_data['scan_pts'])
    scan_vals = np.array(scenario_data['scan_vals'])
    
    search_z = np.arange(scenario_data['z_min'], scenario_data['z_max']+1)
    
    print(f'SearchX: {search_x.min()}-{search_x.max()}')
    print(f'SearchY: {search_y.min()}-{search_y.max()}')
    print(f'SearchZ: {search_z.min()}-{search_z.max()}')
    
    semb_vals = np.zeros((search_x.shape[0], search_y.shape[0], search_z.shape[0]))

    print(f'ScanPts: {scan_pts.shape} ScanVals: {scan_vals.shape}')
    inversion_func = magnetic_inversion(scan_vals.shape[0])
    inversion_func[(search_x.shape[0], search_y.shape[0], search_z.shape[0]), 1](search_x,
                                                                            search_y,
                                                                            search_z, 
                                                                            scan_pts,
                                                                            scan_vals,
                                                                            EARTH_FIELD, 
                                                                            semb_vals,
                                                                            scan_vals.max(),
                                                                            scan_vals.mean(),
                                                                            20)


    
    print(f'Before: {semb_vals.max()}')
    print(f'X: {search_x.shape[0]} Y: {search_y.shape[0]} Z: {search_z.shape[0]}')
    print(f'Total blocks: {search_x.shape[0] * search_y.shape[0] * search_z.shape[0]}')
    
    print(f'After: {semb_vals.max()}')

    
    return jsonify({'pt_cloud': semb_vals.tolist()})
    # return semb_vals.tolist()
    
    # Send back the pt cloud.
    
    
    

    
    
    


