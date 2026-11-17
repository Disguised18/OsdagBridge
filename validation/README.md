# Report validation evidence

The latest calculated comparison is in `design/README.md`, with both named PDFs
and a completed backend design snapshot. The enhanced PDF compiles successfully;
the unchanged baseline PDF preserves the original compiler-error behavior.

The baseline is upstream/dev at d74f56dd7f22925fb8148cabf5740ed8d1e39ff3.
The five existing tests passed before implementation; all five are placeholders.
The report regression suite adds coverage of headers, checkbox values, missing
data, result extraction, chart assets, styles and report orchestration.

Final result: **29 tests passed** on Python 3.12.14 with pytest 9.2.0,
Matplotlib 3.11.2 and PyLaTeX 1.4.2. `git diff --check` passed.

`layout/Layout_After.tex` and the PNGs in `layout/assets` use explicitly synthetic
data from `scripts/report_layout_fixture.py`. These exercise page transitions and
the plot integration; they are not engineering validation or GUI-generated
submission reports. The fixture includes four girders and both passing and
failing utilization ratios, and deliberately omits end-diaphragm quantities.

`layout/Layout_After.pdf` compiled successfully with Tectonic 0.17.0 and contains
39 A4 pages. The rendered overview was reviewed across all pages; continuation
tables and the chart pages were also inspected at larger size. The final compiler
log contains no overfull-box warnings, but retains underfull-box warnings for
some narrow table headings. All text stays inside a 40pt horizontal safety
margin in a PDF text-coordinate check. These checks do not replace a full design
run or engineering review.

The same fixture using unchanged upstream modules produced `Layout_Before.tex`,
but compilation failed at line 253 with `Misplaced \noalign` at `\hline`.
The preceding longtable caption has no row terminator. There is no valid
`Layout_Before.pdf`; no baseline source was altered to manufacture one.

The missing-dependency blocker was resolved by installing the full environment
at `C:\ob-env`. Dependency imports, the bundled pdfTeX compiler, and desktop
window construction succeed; all 29 tests pass in that environment too.
The assignment's required Design → Generate Report comparison remains to be
performed. Tectonic was used for the synthetic layout evidence above.
