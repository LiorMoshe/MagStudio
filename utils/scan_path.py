
from simulations.scenario import GridRange


class ScanPath():
    
    def __init__(self, scan_pts) -> None:
        self.scan_pts = scan_pts
        self.grid_range = GridRange(x_min=scan_pts[:, 0].min(),
                                    x_max=scan_pts[:, 0].max(),
                                    y_min=scan_pts[:, 1].min(),
                                    y_max=scan_pts[: ,1].max())
    
    @staticmethod
    def get_scans_grid_range(self, grid_ranges):
        x_min = min([gr.x_min for gr in grid_ranges])
        y_min = min([gr.y_min for gr in grid_ranges])
        x_max = max([gr.x_max for gr in grid_ranges])
        y_max = max([gr.y_max for gr in grid_ranges])
        return GridRange(x_min, x_max, y_min, y_max)

