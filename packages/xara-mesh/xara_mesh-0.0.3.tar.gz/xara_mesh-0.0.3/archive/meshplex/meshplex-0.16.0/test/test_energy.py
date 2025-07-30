import pathlib

import pytest

import meshplex

this_dir = pathlib.Path(__file__).resolve().parent


@pytest.mark.skip
def test_pacman():
    mesh = meshplex.read(this_dir / "meshes" / "pacman.vtk")
    ref = 3.14
    assert abs(mesh.energy - ref) < 1.0e-14 * ref
