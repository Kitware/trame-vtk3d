import { onMounted, ref, onUnmounted, unref, watch } from "vue";
import { createVtkModule, addListeners } from "../utils";

/**
 * Scene API
 *  - findPointInside(arg)
 *  - findPointOutside(arg)
 *  - getBounds(arg)
 *  - getColorMapPresets()
 *  - getPathPrefix()
 *  - inspect(arg)
 *  - processEvents()
 *  - render()
 *  - resetCamera()
 *  - resetCameraTo(arg)
 *  - resetCameraToBounds(arg)
 *  - screenshot(arg0, arg1, arg2, arg3)
 *  - setBackground(top, bottom)
 *  - setCallback((event, info) => {})
 *  - setPathPrefix(path)
 *  - setSize(width, height)
 *  - start()
 *  - updateCamera(cameraProp)
 *  - updateColorMaps(colorMapProp)
 *  - updateGeometry(geometryProp)
 */

export default {
  emits: [
    "on-ready",
    "on-geometry",
    "on-clicked",
    "on-render",
    "on-char",
    "on-camera",
  ],
  props: ["camera", "colorMaps", "geometry", "pathPrefix"],
  setup(props, { emit, expose }) {
    const scene = ref(null);
    const container = ref(null);
    const canvas = ref(null);
    const canvasWidth = ref(300);
    const canvasHeight = ref(300);
    let vtkModule = null;
    let removeListeners = null;
    let resizeObserver = null;

    function resize() {
      const s = unref(scene);
      if (!unref(container) || !unref(canvas)) {
        return;
      }
      const { clientWidth, clientHeight } = unref(container);
      canvasWidth.value = clientWidth;
      canvasHeight.value = clientHeight;
      if (s) {
        s.setSize(canvasWidth.value, canvasHeight.value);
        s.render();
      }
    }

    function updateCamera(config) {
      if (config && scene.value) {
        scene.value.updateCamera(config);
        scene.value.render();
      }
    }

    function updateGeometry(config) {
      if (config && scene.value) {
        scene.value.updateGeometry(config);
        scene.value.render();
      }
    }

    function updateColorMaps(config) {
      if (config && scene.value) {
        scene.value.updateColorMaps(config);
        scene.value.render();
      }
    }

    function setPathPrefix(pathPrefix) {
      if (pathPrefix && scene.value) {
        scene.value.setPathPrefix(pathPrefix);
        scene.value.render();
      }
    }

    function update() {
      updateGeometry(props.geometry);
    }

    function resetCamera() {
      if (scene.value) {
        scene.value.resetCamera();
        scene.value.render();
      }
    }

    onMounted(async () => {
      vtkModule = createVtkModule(canvas, scene);
      await window.vtk3d(vtkModule);
      await vtkModule.ready;
      removeListeners = addListeners(canvas);
      unref(scene).setCallback((event, value) => {
        emit(`on-${event}`, value);
      });

      if (window.ResizeObserver) {
        resizeObserver = new ResizeObserver(resize);
        resizeObserver.observe(unref(container));
      }

      setPathPrefix(props.pathPrefix);
      updateColorMaps(props.colorMaps);
      updateCamera(props.camera);
      updateGeometry(props.geometry);

      emit("on-ready");
    });

    onUnmounted(() => {
      if (removeListeners) {
        removeListeners();
        removeListeners = undefined;
      }
      if (resizeObserver) {
        resizeObserver.disconnect();
        resizeObserver = undefined;
      }
      vtkModule = null;
    });

    watch(() => props.camera, updateCamera);
    watch(() => props.geometry, updateGeometry);
    watch(() => props.colorMaps, updateColorMaps);
    watch(() => props.pathPrefix, setPathPrefix);

    function sceneExec(method, ...args) {
      return unref(scene)[method](...args);
    }

    function fsExec(method, ...args) {
      return vtkModule?.FS[method](...args);
    }

    expose({
      sceneExec,
      fsExec,
      resize,
      setPathPrefix,
      updateCamera,
      updateGeometry,
      updateColorMaps,
      update,
      resetCamera,
    });

    return {
      container,
      canvas,
      canvasWidth,
      canvasHeight,
      sceneExec,
      fsExec,
      resize,
      scene,
      update,
      resetCamera,
    };
  },
  template: `
    <div ref="container" style="position: relative; width: 100%; height: 100%">
      <canvas
        style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;"
        ref="canvas"
        tabindex="-1"
        @contextmenu.prevent
        :width="canvasWidth"
        :height="canvasHeight"
      />
    </div>
  `,
};
