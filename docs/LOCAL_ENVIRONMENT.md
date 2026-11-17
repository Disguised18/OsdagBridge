# Installed Windows environment

The full dependency environment is installed at `C:\ob-env`, managed by the
workspace's `.tooling/micromamba/Library/bin/micromamba.exe`.

It follows `environment.yml` with `vtk<9.4` and `libboost<1.88` added to avoid
Windows filename-length failures in newer CAD package archives. The resulting
CAD versions include VTK 9.3.1 and PythonOCC 7.8.1.1. Python is 3.12.16.

From the workspace folder, double-click `Launch-OsdagBridge.cmd` to start the app.
The launcher activates the environment's native library paths automatically.

Verification succeeded for Qt, NumPy, SciPy, Fiona, Shapely, Pydantic, xarray,
IfcOpenShell, OpenPyXL, OpenCascade, Osdag Core, OpenSeesPy, opsvis and PyLaTeX.
The bundled compiler reports pdfTeX 1.40.28 (TeX Live 2025). The desktop main
window and CAD display objects were constructed successfully in an offscreen
startup check. The Osdag Core section database was initialized from its SQL.

This resolves the earlier missing-dependency blocker. A full bridge design and
GUI-generated report comparison still require separate validation.

Subsequent validation completed a backend design and generated calculated
comparison PDFs. A visible GUI check initialized the OpenGL/CAD display but the
application closed during input-file selection with Windows exceptions
0x8001010d, 0x80010108 and 0x80010012. Offscreen construction success must not be
interpreted as a successful interactive GUI workflow. See `SUBMISSION.md`.
