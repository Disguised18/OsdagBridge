# OsdagBridge LaTeX Report Generator — Technical Changes

FOSSEE Osdag Winter Internship 2026 screening task: *LaTeX Report Generator
Refactoring & Enhancements*.

- Repository: <https://github.com/Disguised18/OsdagBridge>, branch `fossee-latex-refactor`
- Base: upstream `dev` at `d74f56d` (Nidhikhare12/OsdagBridge)
- Reports: `validation/design/Report_Before.pdf` and `validation/design/Report_After.pdf`

Only the report layer (`src/osdagbridge/core/reports/`) was refactored. No
analysis, design or CAD code was changed, so every number in the report still
comes from the existing OsdagBridge solver.

## 1. Summary of the six requested changes

| # | Requirement | What was done |
|---|---|---|
| 1 | Repeated table headers | Every body table is a `longtable` with an explicit `\endfirsthead` / `\endhead` pair, so the column header row repeats on each new page. Captions sit only in the first head and end with a row break, so they are not repeated or renumbered. An empty continuation header in Chapter 2 was filled in. |
| 2 | Footer overlap and spacing | `geometry` now uses `includeheadfoot` with a 28 pt head height, 18 mm foot skip and 32 mm bottom margin, so the body can never run into the footer. Negative `\vspace` hacks near the footer were removed. Every table and longtable starts with `\Needspace{7\baselineskip}`, which moves it to the next page instead of leaving a header stranded at the bottom. Tall `multirow` cells in Chapter 5 (these caused the "G4" bleed) were replaced by a girder label on every row, so a table can break between any two rows. |
| 3 | Live-load tables | Vehicle live loads and footway live loads are now two separate tables (Tables 3.3 and 3.4), each with Parameter / Value / Unit columns. The vehicle rows follow the eight IRC vehicle checkboxes and the custom vehicles from the *Loading* tab of Additional Inputs. A serialized `"False"` is treated as unchecked. Impact factor, braking load, Class SV braking and centrifugal force each have their own row with a unit. The footway table covers none / single / both sides, and automatic (IRC 6 Cl. 206.1) or user-defined pressure. |
| 4 | Utilization-ratio chart | A bar chart in Section 5.5 shows the governing UR of steel plate girders, the concrete deck slab, cross bracing and end diaphragms, with a red dashed line at UR = 1.0. Bars above 1.0 are red and the rest green. Each bar is the maximum UR of that element's rows in the Section 5.5 summary table, and a regression test checks this against real design output. |
| 5 | Material quantity charts | Chapter 7 has two figures built from the same BOQ values as Table 7.1: structural steel tonnage (girders, cross bracing, end diaphragms), and concrete volume (m³) beside reinforcement weight (MT). The last two are drawn on separate axes because they have different units. Plots are saved as PNGs during generation and embedded with PyLaTeX `Figure`. |
| 6 | Central style module | New `styles.py` is the single source of truth for page geometry, fonts, colours, header/footer, table spacing, section gaps and the chart theme. Every chapter imports it, and no chapter defines its own colours, margins or font sizes. |

## 2. Files changed

All under `src/osdagbridge/core/reports/` unless noted.

| File | Change |
|---|---|
| `styles.py` (new) | Preamble, geometry, palette, header/footer, named spacing and font commands, chart theme, `report_section` decorator. |
| `plots.py` (new) | Reads stored design results and BOQ totals, draws the UR and quantity charts with Matplotlib's Agg canvas, and returns PyLaTeX figures. |
| `load_tables.py` (new) | Builds the vehicle and footway live-load tables and interprets the GUI checkbox values. |
| `report_generator.py` | Uses `styles.preamble`. Generates chart assets into the report's temporary folder and keeps a sibling `<report>_assets` folder so the saved `.tex` can be recompiled. Reports success only when the current compiler run produced the PDF. Always emits Chapter 6 so Chapter 7 keeps its number. Generates the Chapter 5/7 charts whether or not *Drawings* is ticked (the GUI ties `include_figures` to that checkbox). |
| `chap1.py` – `chap9.py`, `executive_summary.py` | Converted to `longtable` with repeated headers. Use the shared style commands. Consistent header capitalisation. Chapter 3 uses the new load tables. Chapter 5 removes tall `multirow` cells, embeds the UR chart and adds the missing summary rows. Chapter 7 embeds the quantity charts. |
| `report_utils.py` | Single-pass LaTeX escaping, so backslashes are not escaped twice. Removed negative figure spacing. |
| `tests/unit/test_reports.py` (new) | 34 regression tests (see Section 6). |
| `scripts/` (new) | `run_design_validation.py` (backend design run), `generate_validation_report.py` (Before/After PDFs), `report_layout_fixture.py` (synthetic layout stress test), `check_environment.py`. |
| `pyproject.toml`, `requirements-reports.txt` | Declare PyLaTeX and Matplotlib, and a light install for running the report tests. |

## 3. Structure of the central style module (`styles.py`)

```
styles.py
├── PALETTE        one dict of named colours (osdagGreen, reportPass, reportFail,
│                  reportInfo, reportMissing); emitted as \definecolor in LaTeX
├── CHART          chart colours derived from PALETTE + DPI and font size
├── FIGURE_WIDTH   width used for every embedded chart
├── report_section decorator: prefixes each chapter with \ReportSectionStyle
├── preamble()     document class, packages, geometry, table spacing
│                  (\tabcolsep, \arraystretch, \LTpre/\LTpost, rule widths),
│                  \Needspace guards, named commands, header/footer page styles,
│                  chapter title format
└── toc_section()  table-of-contents styling
```

Named commands defined in the preamble and used by the chapters:

| Purpose | Commands |
|---|---|
| Body / table style | `\ReportSectionStyle`, `\ReportCompactTable`, `\ReportWideRows`, `\ReportTableLeft`, `\ReportCaptionStyle` |
| Vertical rhythm | `\ReportTableGap`, `\ReportMinorGap`, `\ReportSectionGap`, `\ReportMajorGap`, `\ReportCoverTopSpace` |
| Type sizes | `\ReportSmallFont`, `\ReportFootnoteFont`, `\ReportNormalFont`, `\ReportLargeFont`, `\ReportHeadingFont`, `\ReportBrandFont` |
| Colours | `osdagGreen`, `reportPass`, `reportFail`, `reportInfo`, `reportMissing` |

Changing a margin, colour, gap or font size in `styles.py` changes it across the
whole report and in the charts. Column widths stay with each table, because
they describe that table's data rather than the report's style.

## 4. Rationale

- **Explicit longtable heads instead of a wrapper class.** The chapters already
  write raw LaTeX, so adding `\endfirsthead` / `\endhead` in place keeps the diff
  reviewable and avoids rewriting about 3,200 lines of chapter code into PyLaTeX objects.
- **Reserving footer space instead of patching individual pages.** Overlap came
  from geometry that did not count the header and footer, plus unbreakable
  `multirow` blocks. Fixing both removes the whole class of bug rather than one
  page of it.
- **Charts read the same data as the tables.** The UR chart applies the same
  rules as the Section 5.5 table: compression KL/r against the member limit for
  slenderness, and a bracing-type end diaphragm reported with the bracing
  members. A test fails if a bar ever differs from its table rows.
- **Missing data is shown as N/A, never as a zero bar.** A zero-height bar would
  look like a passing check.
- **Matplotlib Agg canvas, no `pyplot`.** Report generation runs inside the Qt
  desktop app, and using `pyplot` could switch the global backend or touch GUI
  state.
- **No solver changes.** The task is about presentation. Engineering issues found
  along the way are listed in Section 7 for maintainers rather than silently
  "fixed".

## 5. Visual enhancements and polish

- Consistent table headers ("Parameter / Value / Unit") and bold captions throughout.
- A girder column heading on the per-girder check tables (previously blank).
- Failing UR values in the summary table are shown in red, matching the chart.
- The page header no longer shows a stray "|" when the job number is empty.
- Chapter 6 is kept, with a short note, when drawings are not selected, so the
  contents never jump from Chapter 5 to 7.
- Section 5.5 gained the deck SLS-stress, deck minimum-reinforcement and
  end-diaphragm slenderness rows, so every governing value in the chart appears
  in the table.
- Bracing-type end-diaphragm rows are labelled Compression / Tension /
  Slenderness ("as bracing") instead of Moment / Shear, which they are not.
- The saved `.tex` stays recompilable because its images are kept beside it.

## 6. Validation

**Design case.** 20 m span, 7.5 m carriageway, footways on both sides (1.5 m),
zero skew, Maharashtra location, all IRC vehicles selected, optimized design,
default materials. The inputs are saved in `validation/design/inputs.json` and
the matching `Report_Validation.osi` (loadable in the app). The complete
backend result is in `outputs.json`.

**How the reports were made.** `scripts/run_design_validation.py` runs the
real solver (`PlateGirderBridge.design()`) on the inputs above and saves the
result, including the Chapter 4 load-case and reaction summaries, exactly as
`PlateGirderBridge.generate_design_report` hands them to the report generator
when *Generate Report* is clicked. Running the design twice gives identical
results; only the solver log's timestamp changes.

**Before / After.** Both PDFs are generated from that same snapshot by
`scripts/generate_validation_report.py`, through the same
`build_report_payload` / `generate_report` calls the GUI uses. `Report_Before` uses the
unchanged upstream report code at `d74f56d`; `Report_After` uses this branch.

| | Report_Before | Report_After |
|---|---|---|
| pdfTeX exit codes (2 passes) | 1, 1 | 0, 0 |
| LaTeX errors | 138 | 0 |
| Overfull boxes | 61 | 0 |
| Pages | 54 | 60 |

The upstream generator runs pdfTeX in non-stop mode and keeps the PDF despite
the errors, so `Report_Before.pdf` is the real original output, errors included.
Every numeric value in `Report_Before.pdf` also appears in `Report_After.pdf`,
and spot checks against the solver output (girder moment, fatigue stress, SLS
stress, LTB, governing UR) match in both.

**Tests.** `pytest tests` → 34 passed (Python 3.12, PyLaTeX 1.4.2, Matplotlib
3.10). They cover header repetition in every table, checkbox parsing, vehicle
and footway cases, invalid and missing data, chart/table agreement on the real
design snapshot, PNG creation and embedding, shared styles and palette, the
Chapter 6 placeholder, and the generator's asset and compiler handling.

## 7. Known limitations (upstream, not changed here)

- **Braking load shows N/A.** `IRC6_2017.cl_211_2_braking_force` raises
  `UnboundLocalError` (`braking_force_2`) for every lane count, so the report
  falls back to N/A.
- **Deflection values disagree inside the report.** The design module's girder
  check gives a live-load deflection within L/800 (used in Section 5.5 and the
  chart). The older deflection table in Sections 4 and 5.1 shows a larger value
  marked FAIL. Both values come from existing upstream code; the Before report
  shows the same mismatch.
- **Centrifugal force** is not produced by the analysis, so it is shown as N/A.
- **End-diaphragm steel tonnage** is not in the BOQ, so the quantity chart shows
  N/A. A bracing-type end diaphragm has no separate design results, so it is
  reported with the cross-bracing members, as the upstream table already did.
- **Wind and earthquake load tables** have empty rows that upstream does not fill.
- **Drawings** (Chapter 6 figures) need CAD exports from the GUI and were not
  part of the backend validation run.
- **GUI run.** The desktop app starts and its CAD view initialises, but on the
  test machine it closed during the input-file dialog (Windows COM errors
  0x8001010d / 0x80010108). The reports were therefore produced by the backend
  scripts, which run the same solver and report code as the *Design* and
  *Generate Report* buttons.
- The fatigue check fails for this case (UR 2.56). It is left visible on purpose
  to show the failing state of the chart and table.

## 8. Reproducing

```bash
conda env create -f environment.yml
conda activate osdagbridge-env
pip install -r requirements-reports.txt      # report tests only
pytest tests -q

# from the repository root, with PYTHONPATH=src
python scripts/run_design_validation.py        # writes validation/design/inputs.json, outputs.json
python scripts/generate_validation_report.py   # Report_After.pdf
# Report_Before: put an upstream d74f56d checkout's src first on PYTHONPATH, then
python scripts/generate_validation_report.py --baseline
```

See `docs/LOCAL_ENVIRONMENT.md` for Windows installation notes.
