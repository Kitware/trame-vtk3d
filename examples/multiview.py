from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk3d

GEOMETRY_1 = {
    "bounding_box": {
        "type": "BoxWidget",
        "min": {
            "x": -2,
            "y": -1,
            "z": -1,
        },
        "max": {
            "x": 2,
            "y": 1,
            "z": 1,
        },
        "color": "0xFF0000",
        "opacity": 0.7,
        "representation": "surface_with_edges",
        "interactive": False,
    },
}

GEOMETRY_2 = {
    "bounding_box": {
        "type": "BoxWidget",
        "min": {
            "x": -1,
            "y": -2,
            "z": -1,
        },
        "max": {
            "x": 1,
            "y": 2,
            "z": 1,
        },
        "color": "0x00FF00",
        "opacity": 0.7,
        "representation": "surface_with_edges",
        "interactive": False,
    },
}


class MultiView:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue2")
        self.ui = self.create_ui()

    @property
    def state(self):
        return self.server.state

    def create_ui(self):
        with SinglePageLayout(self.server) as layout:
            with layout.toolbar.clear():
                vuetify.VToolbarTitle("VTK WASM from DiceHub")

            with layout.content:
                with vuetify.VContainer(fluid=True, classes="fill-height pa-0 ma-0"):
                    with vuetify.VRow(classes="fill-height pa-0 ma-0"):
                        with vuetify.VCol(classes="pa-0 ma-0"):
                            self.wasm_1 = vtk3d.Vtk3dScene(
                                ref="vtk_wasm1",
                                geometry=("geo1", GEOMETRY_1),
                                on_ready="$refs.vtk_wasm1.scene.resetCamera()",
                                on_char="if ($event === 'R') $refs.vtk_wasm1.scene.resetCamera()",
                            )
                        with vuetify.VCol(classes="pa-0 ma-0"):
                            self.wasm_2 = vtk3d.Vtk3dScene(
                                ref="vtk_wasm2",
                                geometry=("geo2", GEOMETRY_2),
                                on_ready="$refs.vtk_wasm2.scene.resetCamera()",
                                on_char="if ($event === 'R') $refs.vtk_wasm2.scene.resetCamera()",
                            )

            return layout


def main():
    app = MultiView()
    app.server.start()


if __name__ == "__main__":
    main()
