import json
from pathlib import Path

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk3d

STL_FILE = Path(__file__).with_name("cube.stl")

CAMERA_CONFIG = {
    "position": {
        "x": 0,
        "y": 0,
        "z": 10,
    },
    "focal_point": {
        "x": 0,
        "y": 0,
        "z": 0,
    },
    "roll": 0,
    "view_up": {
        "x": 0,
        "y": 1,
        "z": 0,
    },
}

GEOMETRY_CONFIG = {
    "bounding_box": {
        "type": "BoxWidget",
        "min": {
            "x": -1,
            "y": -1,
            "z": -1,
        },
        "max": {
            "x": 0,
            "y": 0,
            "z": 0,
        },
        "color": "0xFFFFff",
        "edge_color": "0xFF0000",
        "opacity": 0.7,
        "representation": "surface_with_edges",
        "interactive": False,
    },
    "sample_stl": {
        "type": "STLFile",
        "path": "sample.stl",
    },
}


class DemoApp:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue2")
        self.ui = self.create_ui()

    def init_scene(self, **kwargs):
        self.wasm.fs.mkdir("/data")
        self.wasm.fs.writeFile(
            "/data/sample.stl",
            STL_FILE.read_text(),
        )
        self.wasm.scene.setPathPrefix("/data/")
        self.wasm.scene.updateCamera(CAMERA_CONFIG)
        self.wasm.scene.updateGeometry(GEOMETRY_CONFIG)
        self.wasm.scene.resetCamera()

    def _scene_update_geometry(self, info):
        info = json.loads(info)
        if info["object"] == "bounding_box" and info["event"] == "modified":
            [minmax, key] = info["info"]["property"].split("/")
            GEOMETRY_CONFIG["bounding_box"][minmax][key] = info["info"]["value"]

    def _scene_clicked(self, info):
        info = json.loads(info)
        if info.get("object") == "bounding_box":
            GEOMETRY_CONFIG["bounding_box"]["interactive"] = not GEOMETRY_CONFIG[
                "bounding_box"
            ]["interactive"]
            self.wasm.scene.updateGeometry(GEOMETRY_CONFIG)
            self.wasm.scene.render()
        elif GEOMETRY_CONFIG["bounding_box"]["interactive"]:
            GEOMETRY_CONFIG["bounding_box"]["interactive"] = False
            self.wasm.scene.updateGeometry(GEOMETRY_CONFIG)
            self.wasm.scene.render()

    def create_ui(self):
        with SinglePageLayout(self.server) as layout:
            with layout.toolbar.clear():
                vuetify.VToolbarTitle("VTK WASM from DiceHub")

            with layout.content:
                with vuetify.VContainer(fluid=True, classes="fill-height pa-0 ma-0"):
                    self.wasm = vtk3d.Vtk3dScene(
                        ref="vtk_wasm",
                        on_ready=self.init_scene,
                        on_geometry=(self._scene_update_geometry, "[$event]"),
                        on_clicked=(self._scene_clicked, "[$event]"),
                        on_char="if ($event === 'R') $refs.vtk_wasm.scene.resetCamera()",
                    )

            return layout


def main():
    app = DemoApp()
    app.server.start()


if __name__ == "__main__":
    main()
