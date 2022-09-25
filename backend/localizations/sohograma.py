import numba
from numba import cuda
from collections import namedtuple
import numpy as np

"""
This is a junk of untested code from my memory for the sohograma algorithm.
Need to write a UI for it and test it out on a cuda gpu.
"""

SohogramaInput = namedtuple('SohogramaInput', 'grid_range scan_pts scan_vals z_min z_max')

def civilized_cpu_sohograma(num_samples):
    def cpu_sohograma(ix, iy, iz, search_x, search_y, search_z, scan_pts, scan_vals, norm_dipole_axis,
                        semb_vals, scan_max_val, scan_min, center, angle):
       
        if (ix >= search_x.shape[0] or iy >= search_y.shape[0] or iz >= search_z.shape[0]):
            return
        
        
        # mag_field_vals = cuda.shared.array(num_samples, dtype=numba.float64)
        mag_field_vals = np.zeros(num_samples)
        
        
        for ipoint in range(num_samples):
            x_val = scan_pts[ipoint, 0]
            y_val = scan_pts[ipoint, 1]
            z_val = scan_pts[ipoint, 2]
            
            x_grid = search_x[ix]
            y_grid = search_y[iy]
            
            if angle != 0:
                diff_x = search_x[ix]-center[0]
                diff_y = search_y[iy]-center[1]
                
                x_grid = (diff_x*np.cos(angle) + diff_y * np.sin(angle)) + center[0]
                y_grid = (-diff_x * np.sin(angle) + diff_y * np.cos(angle)) + center[1]
                
            
            dipole_vec_x = x_val-x_grid
            dipole_vec_y = y_val-y_grid
            dipole_vec_z = z_val-search_z[iz]
            
            
            sqrt_dot = (dipole_vec_x**2 + dipole_vec_y**2 + dipole_vec_z**2) ** 0.5
            
            normed_sens_x = dipole_vec_x / sqrt_dot
            normed_sens_y = dipole_vec_y / sqrt_dot
            normed_sens_z = dipole_vec_z / sqrt_dot


            const_val = numba.float64(1.2566e-6 / (4 * np.pi * (sqrt_dot ** 3)))
            
            dot_norm_axis_sen_vec = (norm_dipole_axis[0] * normed_sens_x 
                                        + norm_dipole_axis[1] * normed_sens_y
                                        + norm_dipole_axis[2] * normed_sens_z)
            
            vec_val_x = 3 * normed_sens_x * dot_norm_axis_sen_vec - norm_dipole_axis[0]
            vec_val_y = 3 * normed_sens_y * dot_norm_axis_sen_vec - norm_dipole_axis[1]
            vec_val_z = 3 * normed_sens_z * dot_norm_axis_sen_vec - norm_dipole_axis[2]
            
            mean_x = norm_dipole_axis[0] * 1e-9
            mean_y = norm_dipole_axis[1] * 1e-9
            mean_z = norm_dipole_axis[2] * 1e-9
            
            x_part = mean_x + const_val * vec_val_x
            y_part = mean_y + const_val * vec_val_y
            z_part = mean_z + const_val * vec_val_z
            
            field_val = (x_part ** 2 + y_part ** 2 + z_part ** 2) ** 0.5
            mag_field_vals[ipoint] = field_val * 1e9


        max_field_val = numba.float64(0)
        min_field_val = numba.float64(1e10)
        for ipoint in range(num_samples):
            if mag_field_vals[ipoint] > max_field_val:
                max_field_val = mag_field_vals[ipoint]
            
            if mag_field_vals[ipoint] < min_field_val:
                min_field_val = mag_field_vals[ipoint]
            
        
        # Compute the semblance value.
        sim_trace_sq = numba.float64(0)
        semblance_nom = numba.float64(0)
        denom_scan_val = numba.float64(0)
        
        for ipoint in range(num_samples):
            curr_val = (scan_vals[ipoint] - scan_min)/(scan_max_val-scan_min)
            normed_field = (mag_field_vals[ipoint]-min_field_val) / (max_field_val-min_field_val)
        
            sim_trace_sq = sim_trace_sq + normed_field ** 2
            semblance_nom = semblance_nom + (normed_field + curr_val) ** 2
            denom_scan_val = denom_scan_val + curr_val**2
            
        semblance_val = semblance_nom / (2 * (sim_trace_sq + denom_scan_val))
        print(f'Semblance value: {semblance_val}')
        semb_vals[ix, iy, iz] = semblance_val
    
    return cpu_sohograma



def magnetic_inversion(num_samples):
    @cuda.jit
    def cuda_func(search_x, search_y, search_z, scan_pts, scan_vals, norm_dipole_axis,
                    arr, scan_max_val, scan_min, val):
        ix = cuda.blockIdx.x
        iy = cuda.blockIdx.y
        iz = cuda.blockIdx.z

        if (ix >= search_x.shape[0] or iy >= search_y.shape[0] or iz >= search_z.shape[0]):
            return

        mag_field_vals = cuda.shared.array(num_samples, dtype=numba.float64)
        
        
        for ipoint in range(num_samples):
            x_val = scan_pts[ipoint, 0]
            y_val = scan_pts[ipoint, 1]
            z_val = scan_pts[ipoint, 2]
            
            x_grid = search_x[ix]
            y_grid = search_y[iy]
            
            dipole_vec_x = x_val-x_grid
            dipole_vec_y = y_val-y_grid
            dipole_vec_z = z_val-search_z[iz]
            
            
            sqrt_dot = (dipole_vec_x**2 + dipole_vec_y**2 + dipole_vec_z**2) ** 0.5
            
            normed_sens_x = dipole_vec_x / sqrt_dot
            normed_sens_y = dipole_vec_y / sqrt_dot
            normed_sens_z = dipole_vec_z / sqrt_dot


            const_val = numba.float64(1.2566e-6 / (4 * np.pi * (sqrt_dot ** 3)))
            
            dot_norm_axis_sen_vec = (norm_dipole_axis[0] * normed_sens_x 
                                     + norm_dipole_axis[1] * normed_sens_y
                                     + norm_dipole_axis[2] * normed_sens_z)
            
            vec_val_x = 3 * normed_sens_x * dot_norm_axis_sen_vec - norm_dipole_axis[0]
            vec_val_y = 3 * normed_sens_y * dot_norm_axis_sen_vec - norm_dipole_axis[1]
            vec_val_z = 3 * normed_sens_z * dot_norm_axis_sen_vec - norm_dipole_axis[2]
            
            mean_x = norm_dipole_axis[0] * 1e-9
            mean_y = norm_dipole_axis[1] * 1e-9
            mean_z = norm_dipole_axis[2] * 1e-9
            
            x_part = mean_x + const_val * vec_val_x
            y_part = mean_y + const_val * vec_val_y
            z_part = mean_z + const_val * vec_val_z
            
            field_val = (x_part ** 2 + y_part ** 2 + z_part ** 2) ** 0.5
            mag_field_vals[ipoint] = field_val * 1e9

        max_field_val = numba.float64(0)
        min_field_val = numba.float64(1e10)
        for ipoint in range(num_samples):
            if mag_field_vals[ipoint] > max_field_val:
                max_field_val = mag_field_vals[ipoint]
            
            if mag_field_vals[ipoint] < min_field_val:
                min_field_val = mag_field_vals[ipoint]
            
        
        # Compute the semblance value.
        sim_trace_sq = numba.float64(0)
        semblance_nom = numba.float64(0)
        denom_scan_val = numba.float64(0)
        
        for ipoint in range(num_samples):
            curr_val = (scan_vals[ipoint] - scan_min)/(scan_max_val-scan_min)
            # normed_field = (mag_field_vals[ipoint]-min_field_val) / (max_field_val-min_field_val)
            normed_field = mag_field_vals[ipoint]/max_field_val
        
            sim_trace_sq = sim_trace_sq + normed_field ** 2
            semblance_nom = semblance_nom + (normed_field + curr_val) ** 2
            denom_scan_val = denom_scan_val + curr_val**2
            
        semblance_val = semblance_nom / (2 * (sim_trace_sq + denom_scan_val))
        arr[ix, iy, iz] = semblance_val
 
    
    return cuda_func
