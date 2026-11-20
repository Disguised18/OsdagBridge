"""Generate before/after reports from the same calculated result snapshot."""
import argparse
import json
from pathlib import Path
from osdagbridge.core.reports import report_generator as report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args()
    folder = Path('validation/design')
    inputs = json.loads((folder / 'inputs.json').read_text())
    outputs = json.loads((folder / 'outputs.json').read_text())
    stem = 'Report_Before' if args.baseline else 'Report_After'
    metadata = report.ReportMetadata('FOSSEE report validation — 20 m bridge', '',
                                     'Disguised18', 'Screening task demonstration', 'FOSSEE applicant',
                                     report_date='2026-11-20', job_number='FOSSEE-WI-2026')
    options = report.ReportOptions(['loads', 'analysis', 'design_checks'], True, True, True)
    request = report.ReportRequest(metadata, options, str(folder.resolve()), stem)
    payload = report.build_report_payload(request, inputs, outputs)
    original_run = report.subprocess.run
    runs = []
    def capture(*args, **kwargs):
        result = original_run(*args, **kwargs)
        runs.append({'returncode': result.returncode,
                     'stdout': result.stdout.decode('utf-8', 'replace'),
                     'stderr': result.stderr.decode('utf-8', 'replace')})
        return result
    report.subprocess.run = capture
    result = report.generate_report(payload, request)
    (folder / (stem + '_compiler.json')).write_text(json.dumps(runs, indent=2))
    print(stem, result)
    if not result.pdf_path:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
