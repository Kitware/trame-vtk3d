import asyncio
import yaml
import json
from yaml import Loader
from pathlib import Path

from trame.app import get_server, asynchronous
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk3d
from trame.decorators import TrameApp, change

VTU_FILE = Path(__file__).with_name("data.vtu")

SCENE_FILE = Path(__file__).with_name("scene.yaml")
COLOR_FILE = Path(__file__).with_name("ColorMaps.json")
CAMERA_FILE = Path(__file__).with_name("camera.yaml")


@TrameApp()
class DataApp:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue2")
        self.ui = self.create_ui()
        self.last_change = 0
        self.last_apply = 0
        asynchronous.create_task(self.auto_apply())

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

    async def auto_apply(self):
        while True:
            await asyncio.sleep(0.5)
            if self.last_change > self.last_apply:
                with self.state:
                    self.last_apply = self.last_change
                    self.apply_clip()

    @change("x_clip")
    def on_clip_change(self, x_clip, auto_apply, **kwargs):
        if self.wasm is not None:
            self.state.geometry["unstructured_grid"]["geometry"]["clip"]["editor"][
                "origin"
            ]["x"] = x_clip
            self.state.geometry["bounding_box"]["max"]["x"] = x_clip
            self.state.dirty("geometry")

            if auto_apply:
                self.apply_clip()

    @change("bbox_visible")
    def on_bbox_visible_change(self, bbox_visible, **kwargs):
        if self.wasm is not None:
            self.state.geometry["bounding_box"]["visible"] = bbox_visible
            self.state.geometry["bounding_box"]["interactive"] = bbox_visible
            self.state.dirty("geometry")

    def reset_camera(self):
        self.wasm.scene.resetCamera()

    def _scene_update_geometry(self, info):
        info = json.loads(info)
        if (
            info["object"] == "unstructured_grid/geometry/clip"
            and info["event"] == "modified"
        ):
            [_, prop, axis] = info["info"]["property"].split("/")
            axis_idx = ["x", "y", "z"].index(axis)
            # save actual editor values to geometry data to use it on next update or use when apply changes to filter
            self.state.geometry["unstructured_grid"]["geometry"]["clip"]["editor"][
                prop
            ][axis_idx] = info["info"]["value"]

        elif (
            info["object"] == "bounding_box"
            and info["event"] == "modified"
            and info["info"]["property"] == "max/x"
        ):
            self.state.x_clip = info["info"]["value"]
            self.last_change += 1

    def apply_clip(self):
        for prop in ("origin", "normal"):
            for i in ("x", "y", "z"):
                value = self.state.geometry["unstructured_grid"]["geometry"]["clip"][
                    "editor"
                ][prop][i]
                self.state.geometry["unstructured_grid"]["geometry"]["clip"][prop][
                    i
                ] = value
                self.state.geometry["unstructured_grid"]["geometry"]["clip2"][prop][
                    i
                ] = value
        self.server.force_state_push("geometry")

    def create_ui(self):
        with SinglePageLayout(self.server) as layout:
            with layout.toolbar.clear():
                vuetify.VToolbarTitle("Interactive Client/Server example")
                vuetify.VSpacer()
                vuetify.VSwitch(
                    label="Interactive apply",
                    v_model=("auto_apply", False),
                    dense=True,
                    hide_details=True,
                )
                vuetify.VSwitch(
                    label="Widget",
                    v_model=("bbox_visible", False),
                    dense=True,
                    hide_details=True,
                    classes="mx-3",
                )
                vuetify.VSlider(
                    v_model=("x_clip", 0),
                    min=-0.0260093,
                    max=0.0260093,
                    step=0.0001,
                    dense=True,
                    hide_details=True,
                    change=self.apply_clip,
                    start="bbox_visible = true",
                    end="bbox_visible = false",
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
                            json.loads(COLOR_FILE.read_text()),
                        ),
                        on_ready=self.init_scene,
                        on_char="if ($event === 'R') $refs.vtk_wasm.scene.resetCamera()",
                        on_geometry=(self._scene_update_geometry, "[$event]"),
                        # on_camera="console.log($event)",
                    )

            return layout


if __name__ == "__main__":
    app = DataApp()
    app.server.start()
