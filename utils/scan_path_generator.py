import numpy as np
import math

def generate_grid(search_x, search_y):
    xvals, yvals = np.meshgrid(search_x, search_y, indexing='ij')
    scan_pts = np.vstack((xvals.reshape(-1), yvals.reshape(-1))).T
    return scan_pts


def generate_spiral_scan(center_pt, line_dist, num_lines, angle_resolution):
    """_summary_
    Generate a spiral according to the equation:
    (r(theta) * cos(theta), r(theta) * sin(theta))

    Args:
        center_pt (_type_): _description_
        line_dist (_type_): _description_
        num_lines (_type_): _description_
        sample_dist (_type_): _description_
    """
    angles = np.arange(0, 2 * np.pi * num_lines, angle_resolution)
    radii = (line_dist / (2 * np.pi)) * angles
    pts = np.vstack((center_pt[0] + radii * np.cos(angles), center_pt[1] + radii * np.sin(angles))).T
    return pts

def generate_strip_scan(start_pt, strip_length, strips_dist, num_strips, sample_dist):
    """
    Generate a scan in the form of strips according to the given parameters.
    Args:
        start_pt (2d array): The top-left corner of the scan.
        strip_length (float): Length of each strip in meters.
        strips_dist (float): Distance between each pair of strips in meters.
        num_strips (int): Total number of strips.
        sample_dist (float): Distance in meters between each pair of points in the strip.
    """
    # First half.
    
    strips = [[start_pt[0] + i * sample_dist, start_pt[1]] for i in range(int(math.ceil(strip_length/sample_dist)))]
    
    prev_strip = strips
    # Add the remaining strips iteratively.
    for i in range(num_strips-1):
        
        end_pt = prev_strip[0] if i % 2 == 1 else prev_strip[-1]
        connector = [[end_pt[0], end_pt[1] - sample_dist * t] for t in range(1, int(math.ceil(strips_dist/sample_dist)))]
        
        strips += connector
        curr_strip = [[start_pt[0] + t * sample_dist, start_pt[1] - strips_dist * (i+1)] 
                      for t in range(int(math.ceil(strip_length/sample_dist)))]
        
        strips += curr_strip if i % 2 == 1 else curr_strip[::-1]
        prev_strip = curr_strip
    
    return np.array(strips)
        

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib import use
    use('Qt5Agg')
    
    plt.figure()
    spiral = generate_spiral_scan((0, 0), 3,10, 0.1)
    strips = generate_strip_scan([0, 0], 10, 2, 10, 0.5)
    plt.scatter(strips[:, 0], strips[:, 1])
    plt.show()