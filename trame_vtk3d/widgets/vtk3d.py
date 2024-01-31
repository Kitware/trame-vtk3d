from trame_client.widgets.core import AbstractElement
from .. import module


class HtmlElement(AbstractElement):
    def __init__(self, _elem_name, children=None, **kwargs):
        super().__init__(_elem_name, children, **kwargs)
        if self.server:
            self.server.enable_module(module)


__all__ = [
    "Vtk3dScene",
]


class MethodBinder:
    def __init__(self, owner, first_arg):
        self._owner = owner
        self._ref = owner.ref
        self._arg1 = first_arg

    def __call__(self, *args):
        return self._owner.server.js_call(self._ref, self._arg1, *args)

    def __getattr__(self, value):
        return lambda *args: self(value, *args)


# Expose your vue component(s)
class Vtk3dScene(HtmlElement):
    _next_id = 0

    def __init__(self, **kwargs):
        super().__init__(
            "vtk-3d-scene",
            **kwargs,
        )
        self._attr_names += [
            "camera",
            ("color_maps", "colorMaps"),
            "geometry",
            ("path_prefix", "pathPrefix"),
        ]
        self._event_names += [
            "on_ready",
            "on_geometry",
            "on_clicked",
            "on_render",
            "on_char",
            "on_camera",
        ]

        Vtk3dScene._next_id += 1
        self.__ref = kwargs.get("ref", f"Vtk3dScene_{Vtk3dScene._next_id}")
        self._attributes["ref"] = f'ref="{self.__ref}"'

        self._scene = MethodBinder(self, "sceneExec")
        self._fs = MethodBinder(self, "fsExec")

    @property
    def ref(self):
        return self.__ref

    @property
    def scene(self):
        return self._scene

    @property
    def fs(self):
        return self._fs

    def update(self):
        self.server.js_call(self.ref, "update")

    def reset_camera(self):
        self.server.js_call(self.ref, "resetCamera")
