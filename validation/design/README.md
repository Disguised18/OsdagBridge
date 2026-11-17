# Calculated report comparison

`inputs.json` and `outputs.json` preserve a completed backend design run using
the application's material dialog defaults: 20 m span, 7.5 m carriageway, zero
skew and a database-backed project location. The run completed structural
analysis, girder checks, deck design and transverse-member design. This is a
demonstration case: fatigue and deflection checks fail, and those failures are
intentionally visible in the report and utilization chart. It is not a certified
or passing bridge design.

`Report_After.pdf` is generated from the modified report code and the recorded
result snapshot. Both compiler passes return zero, with no overfull-box warnings.
All pages were reviewed in a rendered overview; text-coordinate checks found no
text outside a 35pt horizontal safety margin. Geometry drawings and analysis
plot exports were not supplied, so the existing report placeholders remain.

`Report_Before.pdf` is the actual output of unchanged upstream dev code at
`d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` using the same inputs and outputs.
The original generator runs pdfTeX in nonstop mode and saves its PDF even when
compilation fails. Both passes return 1 with 138 LaTeX errors, beginning with
table caption/rule alignment errors. This file is retained to show the original
behavior, not as a successfully compiled report. The baseline code was not
modified to manufacture a clean output.

The scripts use the real backend and normal material-property dialog extraction;
they do not claim a completed click-by-click GUI workflow. Missing upstream
centrifugal-force and end-diaphragm quantity/design values remain explicitly N/A.

Reproduce the enhanced PDF with `scripts/generate_validation_report.py` in the
installed environment. Reproduce the baseline with the unchanged sources first
on PYTHONPATH and the script's `--baseline` flag. The baseline TeX references
temporary image paths inherited from upstream; the enhanced TeX includes a
persisted sibling asset directory and remains rebuildable.
