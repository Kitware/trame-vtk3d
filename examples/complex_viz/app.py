import yaml
from yaml import Loader
from pathlib import Path

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk3d
from trame.decorators import TrameApp, change

VTU_FILE = Path(__file__).with_name("data.vtu")

SCENE_FILE = Path(__file__).with_name("scene.yaml")
COLOR_FILE = Path(__file__).with_name("colors.yaml")
CAMERA_FILE = Path(__file__).with_name("camera.yaml")


@TrameApp()
class DataApp:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue2")
        self.ui = self.create_ui()

    @property
    def state(self):
        return self.server.state

    def init_scene(self, **kwargs):
        self.wasm.fs.mkdir("/data")
        self.wasm.fs.writeFile(
            f"/data/{VTU_FILE.name}",
            VTU_FILE.read_text(),
        )
        self.wasm.update()
        self.wasm.reset_camera()

    @change("opacity")
    def on_opacity_change(self, opacity, **kwargs):
        if self.wasm is not None:
            self.state.geometry["unstructured_grid"]["geometry"]["clip"][
                "opacity"
            ] = opacity
            self.state.geometry["unstructured_grid"]["geometry"]["clip"]["color"] = (
                "0xDD0000" if opacity < 0.5 else "0x00DD00"
            )
            self.state.geometry["unstructured_grid"]["geometry"]["clip"][
                "inside_out"
            ] = (opacity < 0.5)
            self.state.dirty("geometry")

    @change("bbox_visible")
    def on_bbox_visible_change(self, bbox_visible, **kwargs):
        if self.wasm is not None:
            self.state.geometry["bounding_box"]["visible"] = bbox_visible
            self.state.dirty("geometry")

    def reset_camera(self):
        self.wasm.scene.resetCamera()

    def create_ui(self):
        with SinglePageLayout(self.server) as layout:
            with layout.toolbar.clear():
                vuetify.VToolbarTitle("vtkUnstructuredGrid")
                vuetify.VSpacer()
                vuetify.VSwitch(
                    v_model=("bbox_visible", False),
                    dense=True,
                    hide_details=True,
                )
                vuetify.VSlider(
                    v_model=("opacity", 1),
                    min=0.01,
                    max=1,
                    step=0.01,
                    dense=True,
                    hide_details=True,
                )
                with vuetify.VBtn(click=self.reset_camera, icon=True):
                    vuetify.VIcon("mdi-crop-free")

            with layout.content:
                with vuetify.VContainer(fluid=True, classes="fill-height pa-0 ma-0"):
                    self.wasm = vtk3d.Vtk3dScene(
                        ref="vtk_wasm",
                        path_prefix="/data/",
                        camera=(
                            "camera",
                            yaml.load(CAMERA_FILE.read_text(), Loader=Loader),
                        ),
                        geometry=(
                            "geometry",
                            yaml.load(SCENE_FILE.read_text(), Loader=Loader),
                        ),
                        color_maps=(
                            "colors",
                            yaml.load(COLOR_FILE.read_text(), Loader=Loader),
                        ),
                        on_ready=self.init_scene,
                        on_char="if ($event === 'R') $refs.vtk_wasm.scene.resetCamera()",
                        # on_camera="console.log($event)",
                    )

            return layout


if __name__ == "__main__":
    app = DataApp()
    app.server.start()
