# FOSSEE Osdag Winter Internship 2026 — Screening Task Submission

**Task:** OsdagBridge LaTeX Report Generator Refactoring & Enhancements
**Branch:** [`fossee-latex-refactor`](https://github.com/Disguised18/OsdagBridge/tree/fossee-latex-refactor) (based on upstream `dev` at `d74f56d`)

## Deliverables

| Item | Location |
|---|---|
| Python changes | `src/osdagbridge/core/reports/` (new: `styles.py`, `plots.py`, `load_tables.py`) |
| Original report | [`validation/design/Report_Before.pdf`](validation/design/Report_Before.pdf) |
| Enhanced report | [`validation/design/Report_After.pdf`](validation/design/Report_After.pdf) |
| Enhanced report from the desktop app, with drawings | [`validation/design/Report_After_GUI.pdf`](validation/design/Report_After_GUI.pdf) |
| Technical changes document | [`docs/FOSSEE_TECHNICAL_CHANGES.pdf`](docs/FOSSEE_TECHNICAL_CHANGES.pdf) (typeset from [`.tex`](docs/FOSSEE_TECHNICAL_CHANGES.tex); same content as [`.md`](docs/FOSSEE_TECHNICAL_CHANGES.md)) |
| Design inputs used for both reports | [`validation/design/Report_Validation.osi`](validation/design/Report_Validation.osi) |
| Regression tests | `tests/unit/test_reports.py` (35 report tests; 40 in the full suite) |

## Where to look in Report_After.pdf

| Requirement | Section |
|---|---|
| Repeated table headers | Any multi-page table, e.g. the Chapter 5 girder checks |
| Footer spacing | All pages; compare the Chapter 5 tables with Report_Before |
| Vehicle / footway live loads | Tables 3.3 and 3.4 |
| Utilization-ratio chart | Section 5.5, Figure 5.1 |
| Material quantity charts | Chapter 7, Figures 7.1 and 7.2 |
| Central style module | `src/osdagbridge/core/reports/styles.py` |

Report_Before and Report_After come from the same design inputs and solver
output. The original code's PDF is produced despite 138 LaTeX errors (pdfTeX
exit code 1). The enhanced report compiles with no errors and no overfull boxes.

`Report_After_GUI.pdf` was produced in the desktop app (Design, then File →
Create Design Report) and includes the Chapter 6 CAD drawings and the Chapter 4
analysis plots. It uses the same bridge geometry, but its session inputs differ
slightly, so a few values differ (e.g. girder fatigue UR 2.55 vs 2.56).

Known upstream limitations (braking-load helper, deflection values) are listed
in Section 7 of the technical changes document.
