# MagStudio

A simulation gui which allows users to draw out a scanning route and simulate several possible
magnetic objects using fatiando.
First, a user will propose the scan route, whether it is a spiral or a strip scan.
![](https://github.com/LiorMoshe/MagStudio/blob/main/resources/trimmed_spiral.gif)

Following the drawing out of the route we can simulate magnetic objects ranging from the smallest dipole to
a large rectangular object.

![](https://github.com/LiorMoshe/MagStudio/blob/main/resources/sim_trimmed.gif)

Using parallel programming with cuda we can use the semblance coherence measure to invert the given magnetic
data to localize the sources of the magnetic anomalies in the form of a 3d point cloud.
Where the optimal point in the cloud perfectly fits the magnetic field siganl:
![](https://github.com/LiorMoshe/MagStudio/blob/main/resources/sohograma_trimmed.gif)

The app is built such that the cuda computation is ran remotely on a server using flask.
To configure the server change the ip of SERVER_URL at `sim_controller.py`