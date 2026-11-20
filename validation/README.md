# Report validation evidence

- `design/` — the Before/After comparison for a real design run. See
  [`design/README.md`](design/README.md).
- `layout/` — a layout stress test built from clearly synthetic data by
  `scripts/report_layout_fixture.py`. It exercises long tables across page
  breaks and both passing and failing utilization ratios. It is not an
  engineering result.

With the unchanged upstream code, the layout fixture does not compile at all:
`Misplaced \noalign` at line 253 of `Layout_Before.tex`, because a longtable
caption has no row terminator (details in `layout/BASELINE_COMPILER_FAILURE.txt`).
`Layout_After.pdf` compiles cleanly with the new code.
