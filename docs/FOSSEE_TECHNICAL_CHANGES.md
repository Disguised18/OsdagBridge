# OsdagBridge LaTeX Report Generator — Technical Changes

FOSSEE Osdag Winter Internship 2026 screening task: *LaTeX Report Generator
Refactoring & Enhancements*.

> The typeset version of this document is [`FOSSEE_TECHNICAL_CHANGES.pdf`](FOSSEE_TECHNICAL_CHANGES.pdf),
> built from [`FOSSEE_TECHNICAL_CHANGES.tex`](FOSSEE_TECHNICAL_CHANGES.tex) with `pdflatex` (run twice).

- Repository: <https://github.com/Disguised18/OsdagBridge>, branch `fossee-latex-refactor`
- Base: upstream `dev` at `d74f56d` (Nidhikhare12/OsdagBridge)
- Reports: `validation/design/Report_Before.pdf` and `validation/design/Report_After.pdf`

The refactoring is in the report layer (`src/osdagbridge/core/reports/`), plus
two small fixes outside it: how the desktop app starts a report, and the bracing
chord quantities in the Bill of Quantities (see Section 2). No analysis, design
or CAD code was changed, so every design value in the report still comes from
the existing OsdagBridge solver.

## 1. Summary of the six requested changes

| # | Requirement | What was done |
|---|---|---|
| 1 | Repeated table headers | Every body table is a `longtable` with an explicit `\endfirsthead` / `\endhead` pair, so the column header row repeats on each new page. Captions sit only in the first head and end with a row break, so they are not repeated or renumbered. An empty continuation header in Chapter 2 was filled in. At each page break the table is closed with a rule and marked *Continued on next page*, and the next page starts with *Table N continued from previous page* above the repeated header. These notices are added centrally to all 58 tables. |
| 2 | Footer overlap and spacing | `geometry` now uses `includeheadfoot` with a 28 pt head height, 18 mm foot skip and 32 mm bottom margin, so the body can never run into the footer. Negative `\vspace` hacks near the footer were removed. Every table and longtable starts with `\Needspace{7\baselineskip}`, which moves it to the next page instead of leaving a header stranded at the bottom. Tall `multirow` cells in Chapter 5 (these caused the "G4" bleed) were replaced by a girder label on every row, so a table can break between any two rows. |
| 3 | Live-load tables | Vehicle and footway live loads are two separate tables (3.3 and 3.4). Table 3.3 follows the layout of the example in the brief: one row per vehicle selected in the *Loading* tab (eight IRC classes plus custom vehicles), with Total Load (kN), Impact Factor (1 + IM) and Braking Load (Considered? / Value / Eccentricity). Total loads come from the IRC 6 vehicle definitions the analysis uses; impact factors follow IRC 6 Cl. 208.2 / 208.3 per class; braking is considered for every selected vehicle (the app's own rule; Class SV has its own opt-in), its value is 20% of the vehicle load per IRC 6 Cl. 211.2, and its eccentricity comes from the Loading tab. Notes under the table explain each N/A and why centrifugal force does not apply (straight bridge). A serialized `"False"` is treated as unchecked. The footway table covers none / single / both sides, and automatic (IRC 6 Cl. 206.1) or user-defined pressure. |
| 4 | Utilization-ratio chart | A bar chart in Section 5.5 shows the governing UR of steel plate girders, the concrete deck slab, cross bracing and end diaphragms, with a red dashed line at UR = 1.0. Bars above 1.0 are red and the rest green. Each bar is the maximum UR of that element's rows in the Section 5.5 summary table, and a regression test checks this against real design output. |
| 5 | Material quantity charts | Chapter 7 has two figures built from the same BOQ values as Table 7.1: structural steel tonnage (girders, cross bracing, end diaphragms), and concrete volume (m³) beside reinforcement weight (MT). The last two are drawn on separate axes because they have different units. Plots are saved as PNGs during generation and embedded with PyLaTeX `Figure`. The BOQ previously counted top and bottom bracing chords even when the user had disabled them; it now follows the chord settings, so the bracing tonnage in Table 7.1 and Figure 7.1 is right for every configuration. The BOQ also had no end-diaphragm quantity; row 2(d) now gives the steel in bracing-type end diaphragms (one frame per bay at each support, two diagonals plus enabled chords, designed section areas, 7.85 t/m³), 8 frames and 1.21 t for this design. |
| 6 | Central style module | New `styles.py` is the single source of truth for page geometry, fonts, colours, header/footer, row and cell spacing, section and title-page gaps, PASS/FAIL labels and the chart theme. Every chapter imports it. The 259 hardcoded row gaps (`\\[6pt]` etc.) and the raw colours and title-page lengths were replaced by named commands, and a test fails if any report module hardcodes a row gap, colour or font size. |

## 2. Files changed

All under `src/osdagbridge/core/reports/` unless noted.

| File | Change |
|---|---|
| `styles.py` (new) | Preamble, geometry, palette, header/footer, named spacing and font commands, chart theme, `report_section` decorator, and `continued_tables()`, which adds the page-break notices to every longtable. |
| `plots.py` (new) | Reads stored design results and BOQ totals, draws the UR and quantity charts with Matplotlib's Agg canvas, and returns PyLaTeX figures. |
| `load_tables.py` (new) | Builds Table 3.3 in the brief's per-vehicle layout (total load, impact factor, braking) and the footway table, and interprets the GUI checkbox values. |
| `report_generator.py` | Uses `styles.preamble`. Generates chart assets into the report's temporary folder and keeps a sibling `<report>_assets` folder so the saved `.tex` can be recompiled. Reports success only when the current compiler run produced the PDF. Always emits Chapter 6 so Chapter 7 keeps its number. Generates the Chapter 5/7 charts whether or not *Drawings* is ticked (the GUI ties `include_figures` to that checkbox). |
| `chap1.py` – `chap9.py`, `executive_summary.py` | Converted to `longtable` with repeated headers. Use the shared style commands. Consistent header capitalisation. Chapter 3 uses the new load tables. Chapter 5 removes tall `multirow` cells, embeds the UR chart and adds the missing summary rows. Chapter 7 embeds the quantity charts. |
| `report_utils.py` | Single-pass LaTeX escaping, so backslashes are not escaped twice. Removed negative figure spacing. |
| `desktop/ui/template_page.py`, `desktop/ui/docks/output_dock.py` (under `src/osdagbridge/`) | *File → Create Design Report* now goes through the same 3D-view and plot capture as the Output panel's *Generate Report* button. Before, the menu skipped the capture, so every drawing in the report was a placeholder. |
| `core/boq/boq_generator.py` (under `src/osdagbridge/`) | Bracing chord quantities follow the top/bottom chord settings recorded by the cross-bracing force calculation, instead of always being included. End-diaphragm steel (Table 7.1 row 2(d)) added. |
| `tests/unit/test_reports.py` (new) | 40 report regression tests; with the 5 existing tests the suite has 45 (see Section 6). |
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
├── toc_section()  table-of-contents styling
└── continued_tables()  adds "continued" notices and a closing rule at page
                   breaks to every longtable in the finished document
```

Named commands defined in the preamble and used by the chapters:

| Purpose | Commands |
|---|---|
| Body / table style | `\ReportSectionStyle`, `\ReportCompactTable`, `\ReportWideRows`, `\ReportTableLeft`, `\ReportCaptionStyle` |
| Vertical rhythm | `\ReportTableGap`, `\ReportMinorGap`, `\ReportSectionGap`, `\ReportMajorGap`, `\ReportCoverTopSpace` |
| Row / cell spacing (lengths) | `\ReportRowGap` (6 pt), `\ReportRowGapLarge` (8 pt), `\ReportCellLineGap` (3 pt) |
| Title page (lengths) | `\ReportTitleLineGap`, `\ReportTitleBlockGap`, `\ReportTitleLogoGap` |
| Check status | `\ReportPass`, `\ReportFail` (red) |
| Page-break notices | `\ReportContinuedOn`, `\ReportContinuedFrom`, `\ReportContinuedFromNumbered` |
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

- Table 3.3 uses a two-level header (Braking Load over Considered? / Value / Eccentricity), as in the brief, and repeats it on the next page.
- Consistent table headers ("Parameter / Value / Unit") and bold captions throughout.
- A girder column heading on all per-girder tables in Chapter 5 (previously blank).
- Tables that break across pages are closed with a rule and labelled *Continued on next page* / *Table N continued from previous page*.
- Failing UR values in the summary table are shown in red, matching the chart.
- The page header no longer shows a stray "|" when the job number is empty.
- Missing values are shown as N/A instead of empty cells (23 rows upstream left
  blank, in the wind, seismic and stiffener tables).
- The Reactions at Supports table (Table 4.2), which upstream left with three
  empty rows, now shows the ULS and SLS envelopes and dead-load reactions from
  the analysis.
- Reports no longer fail for designs whose check names contain symbols such as
  `≤` (e.g. "Int.Stiff: Leg ≤ H_limit"); `styles.py` maps these symbols for
  pdfLaTeX. Found by running the real design for 15 m, 30 m (skewed, no footway)
  and 40 m bridges: all three now produce clean reports.
- UR chart labels have a white backing, so a value near 1.0 stays readable over
  the red threshold line.
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
| Pages | 54 | 63 |

The upstream generator runs pdfTeX in non-stop mode and keeps the PDF despite
the errors, so `Report_Before.pdf` is the real original output, errors included.
Every numeric value in `Report_Before.pdf` also appears in `Report_After.pdf`,
and spot checks against the solver output (girder moment, fatigue stress, SLS
stress, LTB, governing UR) match in both.

**Other designs.** The real solver was also run for a 15 m span with a
footway on one side, a 30 m span with an 11 m carriageway, 10° skew and no
footway, and a 40 m span at a site with wind and seismic data. All three
reports compile with no errors, no overfull boxes and no empty cells, and
every table carries the page-break notices.

**Tests.** `pytest tests` → 45 passed in the full environment; the one GUI test
is skipped where PySide6 is not installed (Python 3.12, PyLaTeX 1.4.2, Matplotlib
3.10). They cover header repetition in every table, checkbox parsing, vehicle
and footway cases, the per-vehicle table layout, invalid and missing data, chart/table agreement on the real
design snapshot, PNG creation and embedding, shared styles and palette, the
Chapter 6 placeholder, the absence of hardcoded formatting outside `styles.py`,
and the generator's asset and compiler handling.

## 7. Known limitations (upstream, not changed here)

- **No braking load case.** Table 3.3 gives each vehicle's braking force per
  IRC 6 Cl. 211.2 (20% of the vehicle load), but the analysis does not apply a
  braking load, and `IRC6_2017.cl_211_2_braking_force` raises `UnboundLocalError`
  (`braking_force_2`) for every lane count.
- **Vehicle selection does not drive the analysis.** The grillage analysis always
  places Class A and Class 70R (Wheeled) vehicles per IRC 6 Table 6 and applies
  the Cl. 208.3 impact factor to all vehicle cases, whatever is ticked in the
  Loading tab. Table 3.3 lists the vehicles as selected, as the brief asks, and
  says this in its notes. Class AA and Class 70R (Bogie) have no vehicle
  definition in the code, so their total load is N/A.
- **Deflection values disagree inside the report.** The design module's girder
  check gives a live-load deflection within L/800 (used in Section 5.5 and the
  chart). The older deflection table in Sections 4 and 5.1 shows a larger value
  marked FAIL. Both values come from existing upstream code; the Before report
  shows the same mismatch.
- **End-diaphragm design results.** A bracing-type end diaphragm has no
  separate design results, so its checks are reported with the cross-bracing
  members, as the upstream table already did. Its steel quantity is in Table 7.1
  (row 2(d)); end diaphragms of other types show N/A there.
- **Wind and seismic data.** The location database has no wind speed or seismic
  zone for the Ahmednagar station, so the analysis falls back to its defaults
  (33 m/s, Zone II, Z = 0.10). The report shows these location values, and the
  values derived from them, as N/A instead of the blank cells upstream printed.
- **Drawings** (Chapter 6 figures) need CAD exports from the GUI, so the
  script-made Before/After reports show placeholders. A report started from the
  GUI (Output panel or File menu) includes them; see `Report_After_GUI.pdf`.
- **GUI run.** The full GUI workflow (load inputs → Design → File → Create
  Design Report) was completed and produced `validation/design/Report_After_GUI.pdf`
  (72 pages, all drawings and analysis plots). The Before/After pair is still
  generated by the backend scripts, so both use one identical result snapshot.
  Two GUI issues found on the way were fixed: the File-menu route skipped the
  drawing capture, and the bracing dialog's extra text entries crashed the
  report once drawings were captured. On one machine the native Windows file
  dialog closed the app (COM errors 0x8001010d / 0x80010108); this did not
  recur in the final run.
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
