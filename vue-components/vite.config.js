export default {
  base: "./",
  build: {
    lib: {
      entry: "./src/main.js",
      name: "trame_vtk3d",
      formats: ["umd"],
      fileName: "trame_vtk3d",
    },
    rollupOptions: {
      external: ["vue"],
      output: {
        globals: {
          vue: "Vue",
        },
      },
    },
    outDir: "../trame_vtk3d/module/serve",
    assetsDir: ".",
  },
};
