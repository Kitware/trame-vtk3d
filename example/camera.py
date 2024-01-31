import json

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk3d

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
            "x": 1,
            "y": 1,
            "z": 1,
        },
        "color": "0xFFFFff",
        "edge_color": "0xFF0000",
        "opacity": 0.7,
        "representation": "surface_with_edges",
        "interactive": False,
    },
}


class DemoApp:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue2")
        self.ui = self.create_ui()

    @property
    def state(self):
        return self.server.state

    def _scene_update_geometry(self, info):
        info = json.loads(info)
        if info["object"] == "bounding_box" and info["event"] == "modified":
            [minmax, key] = info["info"]["property"].split("/")
            self.state.geometry["bounding_box"][minmax][key] = info["info"]["value"]

    def _scene_clicked(self, info):
        info = json.loads(info)
        if info.get("object") == "bounding_box":
            self.state.geometry["bounding_box"]["interactive"] = (
                not self.state.geometry["bounding_box"]["interactive"]
            )
            self.state.dirty("geometry")
        elif GEOMETRY_CONFIG["bounding_box"]["interactive"]:
            self.state.geometry["bounding_box"]["interactive"] = False
            self.state.dirty("geometry")

    def camera_x(self):
        self.state.camera["position"] = dict(x=10, y=0, z=0)
        self.state.camera["view_up"] = dict(x=0, y=1, z=0)
        self.server.force_state_push("camera")

    def camera_y(self):
        self.state.camera["position"] = dict(x=0, y=10, z=0)
        self.state.camera["view_up"] = dict(x=0, y=0, z=1)
        self.server.force_state_push("camera")

    def camera_z(self):
        self.state.camera["position"] = dict(x=0, y=0, z=10)
        self.state.camera["view_up"] = dict(x=0, y=1, z=0)
        self.server.force_state_push("camera")

    def create_ui(self):
        with SinglePageLayout(self.server) as layout:
            with layout.toolbar.clear():
                vuetify.VToolbarTitle("VTK WASM from DiceHub")
                vuetify.VSpacer()
                vuetify.VBtn("X", click=self.camera_x)
                vuetify.VBtn("Y", click=self.camera_y)
                vuetify.VBtn("Z", click=self.camera_z)

            with layout.content:
                with vuetify.VContainer(fluid=True, classes="fill-height pa-0 ma-0"):
                    self.wasm = vtk3d.Vtk3dScene(
                        ref="vtk_wasm",
                        geometry=("geometry", GEOMETRY_CONFIG),
                        camera=("camera", CAMERA_CONFIG),
                        on_ready="$refs.vtk_wasm.scene.resetCamera()",
                        on_geometry=(self._scene_update_geometry, "[$event]"),
                        on_clicked=(self._scene_clicked, "[$event]"),
                        on_char="if ($event === 'R') $refs.vtk_wasm.resetCamera()",
                        # on_camera=(lambda m: print(m), "[$event]"),
                    )

            return layout


def main():
    app = DemoApp()
    app.server.start()


if __name__ == "__main__":
    main()
