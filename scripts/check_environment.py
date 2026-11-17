"""Check desktop, native analysis/CAD libraries and the bundled PDF compiler."""
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    handles = []
    if os.name == 'nt':
        for folder in (Path(sys.prefix), Path(sys.prefix) / 'Library/bin', Path(sys.prefix) / 'DLLs'):
            if folder.is_dir():
                handles.append(os.add_dll_directory(str(folder)))
                os.environ['PATH'] = str(folder) + os.pathsep + os.environ.get('PATH', '')
    results = {}
    for module in ('PySide6.QtWidgets', 'numpy', 'scipy', 'fiona', 'shapely',
                   'pydantic', 'xarray', 'ifcopenshell', 'openpyxl', 'OCC.Core.BRep',
                   'osdag_core', 'openseespy.opensees', 'opsvis', 'pylatex',
                   'osdagbridge.core.reports'):
        try:
            importlib.import_module(module)
            results[module] = 'OK'
        except Exception as error:
            results[module] = f'{type(error).__name__}: {error}'
    try:
        from osdag_latex_env.__main__ import OsdagLatexEnv
        latex = OsdagLatexEnv()
        compiler = str(latex.pdflatex)
        run = subprocess.run([compiler, '--version'], capture_output=True, text=True, timeout=30)
        results['pdflatex'] = run.stdout.splitlines()[0] if run.returncode == 0 else run.stderr
    except Exception as error:
        results['pdflatex'] = f'{type(error).__name__}: {error}'
    print(json.dumps({'python': sys.version, 'prefix': sys.prefix, 'checks': results}, indent=2))
    return int(any(value.startswith(('ModuleNotFoundError:', 'ImportError:', 'OSError:', 'FileNotFoundError:'))
                   for value in results.values()))


if __name__ == '__main__':
    raise SystemExit(main())
