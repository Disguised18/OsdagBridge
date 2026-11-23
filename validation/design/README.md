# Before / After report comparison

| File | Contents |
|---|---|
| `inputs.json`, `Report_Validation.osi` | Design inputs (identical; the `.osi` loads in the app) |
| `outputs.json` | Complete solver result for those inputs, plus the Chapter 4 summaries the GUI passes to the report |
| `Report_Before.pdf` / `.tex` | Unchanged upstream report code (`d74f56d`) |
| `Report_After.pdf` / `.tex` | This branch's report code |
| `Report_After_assets/` | Charts and logo referenced by `Report_After.tex` |
| `Report_After_GUI.pdf` / `.tex` / `_assets/` | Same report code, generated in the desktop app with CAD drawings and analysis plots (72 pages, 24 images) |

**Design case:** 20 m span, 7.5 m carriageway, 1.5 m footways on both sides,
zero skew, Maharashtra location, all IRC vehicle classes, optimized design with
default materials. The full structural analysis and girder, deck and bracing
designs ran to completion. The fatigue check fails (UR 2.56), so the failing
state of the chart and tables is visible.

| | Before | After |
|---|---|---|
| pdfTeX exit codes (2 passes) | 1, 1 | 0, 0 |
| LaTeX errors | 138 | 0 |
| Overfull boxes | 61 | 0 |
| Pages | 54 | 63 |

The original generator runs pdfTeX in non-stop mode and keeps the PDF even when
compilation fails, so `Report_Before.pdf` is the real original output.
Drawings need CAD exports from the GUI, so they are placeholders in these two
script-made reports. `Report_After_GUI.pdf` shows them: it was generated in the
desktop app with the same bridge geometry, but its session inputs differ
slightly, so a few values differ (girder fatigue UR 2.55 vs 2.56).

## Regenerate

From the repository root with `PYTHONPATH=src` in the OsdagBridge environment:

```bash
python scripts/run_design_validation.py
python scripts/generate_validation_report.py
```

For the baseline, put the `src` folder of an upstream `d74f56d` checkout first
on `PYTHONPATH` and add `--baseline`.
