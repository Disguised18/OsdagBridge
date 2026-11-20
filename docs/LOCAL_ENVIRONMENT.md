# Windows environment notes

The full app was installed from `environment.yml` with two extra pins:

```
vtk<9.4
libboost<1.88
```

Newer builds of these CAD packages contain file paths longer than the Windows
limit and fail to extract. With the pins, the environment resolves to VTK 9.3.1,
PythonOCC 7.8.1.1 and Python 3.12. The bundled TeX Live 2025 pdfTeX 1.40.28
compiles the reports.

Start the app from the repository's `src` folder:

```bash
python -m osdagbridge.desktop
```

`scripts/check_environment.py` checks that Qt, the CAD stack, the solvers and
PyLaTeX import correctly and that the bundled `pdflatex` (from `osdag_latex_env`) runs.

For the report tests alone, a plain Python 3.11+ virtual environment is enough:

```bash
pip install -r requirements-reports.txt
pytest tests -q
```
