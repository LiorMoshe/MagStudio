import numpy as np

"""
Map the points in the point cloud to the given
"""

def np_where_3d_wrapper(condition):
    idxs = np.where(condition)
    return np.vstack((idxs[0], idxs[1], idxs[2])).T
    
def get_percentile_vals(start_val=80, end_val=99.99, jump=5.):
    vals = []
    curr_val = start_val
    while curr_val < end_val:
        vals.append(curr_val)
        curr_val += jump
        if jump > 0.1:
            jump = float(jump)/1.99
    return np.array(vals)


class PercentileFilter():
    
    def __init__(self, search_x, search_y, search_z, pt_cloud) -> None:
        
        # Map each percentile to the pts that will be added once we pass it.
        self.pt_cloud = pt_cloud
        self.percentile_map = {}
        
        self.X, self.Y, self.Z = np.meshgrid(search_x, search_y, search_z, indexing='ij')
        
        self.percentile_vals = get_percentile_vals()
        self.preprocess()
        

    def preprocess(self):
        prev_per_val = None
        for per in self.percentile_vals[::-1]:
            per_val = np.percentile(self.pt_cloud, per)
            
            if prev_per_val:
                idxs = np_where_3d_wrapper(self.pt_cloud >= per_val and self.pt_cloud <= prev_per_val)
            else:
                idxs = np_where_3d_wrapper(self.pt_cloud >= per_val)
            
            
            self.percentile_map[per] = idxs
    
    def get_pts_over_percentile(self, percentile):
        """
        Gather all the preprocessed indices and return a section of the pt cloud
        Args:
            percentile (_type_): _description_
        """
        pts = []
        per_idx = np.argmin(np.abs(self.percentile_vals-percentile))
        for i in range(per_idx, len(self.percentile_vals)):
            idxs = self.percentile_map[self.percentile_vals[i]]
            for idx in idxs:
                tup_idx = tuple(idx)
                pts.append([self.X[tup_idx], self.Y[tup_idx], self.Z[tup_idx], self.pt_cloud[tup_idx]])
        
        return np.array(pts)