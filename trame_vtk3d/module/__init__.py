from pathlib import Path

serve_path = str(Path(__file__).with_name("serve").resolve())
serve = {"__trame_vtk3d": serve_path}
scripts = ["__trame_vtk3d/trame_vtk3d.umd.js", "__trame_vtk3d/vtk3d.js"]
vue_use = ["trame_vtk3d"]
