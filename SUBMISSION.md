# FOSSEE Osdag Winter Internship 2026 — Screening Task Submission

**Task:** OsdagBridge LaTeX Report Generator Refactoring & Enhancements
**Branch:** [`fossee-latex-refactor`](https://github.com/Disguised18/OsdagBridge/tree/fossee-latex-refactor) (based on upstream `dev` at `d74f56d`)

## Deliverables

| Item | Location |
|---|---|
| Python changes | `src/osdagbridge/core/reports/` (new: `styles.py`, `plots.py`, `load_tables.py`) |
| Original report | [`validation/design/Report_Before.pdf`](validation/design/Report_Before.pdf) |
| Enhanced report | [`validation/design/Report_After.pdf`](validation/design/Report_After.pdf) |
| Technical changes document | [`docs/FOSSEE_TECHNICAL_CHANGES.md`](docs/FOSSEE_TECHNICAL_CHANGES.md) |
| Design inputs used for both reports | [`validation/design/Report_Validation.osi`](validation/design/Report_Validation.osi) |
| Regression tests | `tests/unit/test_reports.py` (36 tests) |

## Where to look in Report_After.pdf

| Requirement | Section |
|---|---|
| Repeated table headers | Any multi-page table, e.g. the Chapter 5 girder checks |
| Footer spacing | All pages; compare the Chapter 5 tables with Report_Before |
| Vehicle / footway live loads | Tables 3.3 and 3.4 |
| Utilization-ratio chart | Section 5.5, Figure 5.1 |
| Material quantity charts | Chapter 7, Figures 7.1 and 7.2 |
| Central style module | `src/osdagbridge/core/reports/styles.py` |

Both PDFs come from the same design inputs and solver output. The original
code's PDF is produced despite 138 LaTeX errors (pdfTeX exit code 1). The
enhanced report compiles with no errors and no overfull boxes.

Known upstream limitations (braking-load helper, deflection values, drawings
and the GUI file-dialog crash) are listed in Section 7 of the technical changes
document.
