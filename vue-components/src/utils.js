import { unref } from "vue";

// https://github.com/emscripten-ports/SDL2/issues/137
export function wrapAddEventListener(canvas) {
  const originalAddEventListener = Document.prototype.addEventListener;

  Document.prototype.addEventListener = function (...args) {
    unref(canvas).addEventListener(...args);
  };

  return () => {
    Document.prototype.addEventListener = originalAddEventListener;
  };
}

export function addListeners(canvas) {
  const savedEvents = new Set();

  function onKeydown(e) {
    if (["Control", "Shift", "Alt", "Meta"].includes(e.key)) {
      savedEvents.add(e);
    }
  }

  function onKeyup(e) {
    for (const savedEvent of savedEvents) {
      if (savedEvent.code === e.code) {
        savedEvents.delete(savedEvent);
      }
    }
  }

  /** If you click outside of canvas with the modifiers pressed, canvas will lose focus and won't
   * notice when you release the modifiers afterwards. Well, let's get the focus back. */
  function onBlur() {
    if (savedEvents.size) {
      /* Without setTimeout, the focus will not return to canvas. */
      setTimeout(() => {
        unref(canvas).focus();
      });
    }
  }

  function onPointerdown(e) {
    unref(canvas).setPointerCapture(e.pointerId);
    if (document.activeElement !== unref(canvas)) {
      unref(canvas).focus();

      if (savedEvents.size) {
        for (const savedEvent of savedEvents) {
          unref(canvas).dispatchEvent(savedEvent);
        }
      }
    }
  }

  function onWindowBlur() {
    /* For example, if you switch to another window with alt+tab, the keydown event with the alt
        button will be saved in savedEvents and when you return to the window, it will be proxied to
        canvas (because there was no corresponding keyup event). Well, let's just clear the savedEvents.
         */
    savedEvents.clear();
  }

  unref(canvas).addEventListener("pointerdown", onPointerdown);
  unref(canvas).addEventListener("blur", onBlur);
  document.addEventListener("keydown", onKeydown);
  document.addEventListener("keyup", onKeyup);
  window.addEventListener("blur", onWindowBlur);

  return () => {
    document.removeEventListener("keydown", onKeydown);
    document.removeEventListener("keyup", onKeyup);
    window.removeEventListener("blur", onWindowBlur);
  };
}

export function createVtkModule(canvas, scene) {
  const module = {
    locateFile() {
      return "__trame_vtk3d/vtk3d.wasm";
    },
    canvas: unref(canvas),
    setWindowTitle() {},
  };

  function onRuntimeInitialized() {
    try {
      scene.value = new module.Scene();
      const unwrap = wrapAddEventListener(canvas);
      scene.value.start();
      unwrap();
    } catch (error) {
      console.error(error);
    }
  }

  module.onRuntimeInitialized = onRuntimeInitialized;

  return module;
}
