===========
trame-vtk3d
===========

Trame wrapper to WASM bundle of VTK from `dicehub <https://dicehub.com/welcome>`_

License
---------------------

The trame widget is released under Apache Software License.

Installation
---------------------

.. code-block:: console

    pip install trame-vtk3d


Try out an example
---------------------

.. code-block:: console

    python -m venv .venv
    source .venv/bin/activate
    pip install trame trame-vuetify trame-vtk3d
    python ./examples/camera.py


Development
---------------------

Build and install the Vue components

.. code-block:: console

    cd vue-components
    npm i
    npm run build
    cd -

Fetch vtk3d (JS+WASM)

.. code-block:: console

    ./.fetch_externals.sh

Install the python package

.. code-block:: console

    pip install .
