def test_import():
    from trame_vtk3d.widgets.vtk3d import Vtk3dScene  # noqa: F401

    # For components only, the CustomWidget is also importable via trame
    from trame.widgets.vtk3d import Vtk3dScene  # noqa: F401,F811
