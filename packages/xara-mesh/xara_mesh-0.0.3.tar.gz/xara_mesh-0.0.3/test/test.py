import xara_mesh.distance as dmsh
from xara_mesh.distance.helpers import show
import meshio

geo = dmsh.Circle([0.0, 0.0], 1.0)
X, cells = dmsh.generate(geo, 0.1)

# visualize the mesh
show(X, cells, geo)

