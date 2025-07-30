import numpy as np
import pytest

import meshplex


@pytest.mark.skip
def test_outer_normal():
    points = np.array([[0.0, 0.0], [1.0, 0.0], [1.1, 1.0], [0.0, 1.0]])
    cells = np.array([[0, 1, 2], [0, 3, 2]])
    mesh = meshplex.MeshTri(points, cells)
    mesh.create_edges()
    print(mesh.edges["points"])
    print(mesh.boundary_edges)
    print(mesh.is_boundary_edge)
    exit(1)


if __name__ == "__main__":
    test_outer_normal()
