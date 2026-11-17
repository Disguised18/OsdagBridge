"""Build a synthetic layout fixture. This is not a completed bridge design.

Run with PYTHONPATH=src; compile the resulting .tex with pdflatex twice or
tectonic. The many girder rows deliberately exercise table page transitions.
"""
import argparse
from pathlib import Path

from osdagbridge.core.reports.report_generator import ReportMetadata, ReportDataBridge
from osdagbridge.core.reports.report_generator import preamble
from osdagbridge.core.reports.chap1 import ch1_project_info
from osdagbridge.core.reports.chap2 import ch2_input_parameters
from osdagbridge.core.reports.chap3 import ch3_loads
from osdagbridge.core.reports.chap5 import ch5_design_checks
from osdagbridge.core.reports.chap7 import ch7_quantities
from osdagbridge.core.utils import common as keys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path('validation/layout'))
    parser.add_argument('--baseline', action='store_true', help='Use the unmodified dev modules on PYTHONPATH')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    inputs = {keys.KEY_SPAN: 20, keys.KEY_TS_NO_OF_GIRDERS: 4,
              keys.KEY_LL_IRC_CLASS_A: True, keys.KEY_LL_IRC_70R_WHEELED: True,
              keys.KEY_FOOTPATH: 'Both Sides', keys.KEY_LL_FOOTPATH_PRESSURE_MODE: 'Custom',
              keys.KEY_LL_FOOTPATH_PRESSURE_VALUE: 5,
              keys.KEY_WC_LD_LANE_TABLE_COUNT: 2}
    for i in range(1, 5):
        inputs[f'{keys.KEY_MP_GD_SELECT_GIRDER}.G{i}'] = f'G{i}'
        inputs[f'{keys.KEY_MP_GD_MEMBER_ID}.G{i}.M1'] = f'G{i}M1'
    quantities = {'steel_girders_wt_total': 48, 'bracing_top_wt_total': .8,
                  'bracing_bot_wt_total': .9, 'bracing_diag_wt_total': 1.2,
                  'concrete_deck_vol_total': 45, 'rebar_deck_wt_total': 5.4}
    outputs = {
        'design_results': {'per_girder': {
            f'G{i}': {'checks': [{'check_id': 1, 'name': 'Moment', 'dcr': .75 + i / 10,
                                 'demand': 750 + i * 100, 'capacity': 1000,
                                 'demand_unit': 'kNm', 'capacity_unit': 'kNm'}]}
            for i in range(1, 5)}},
        'deck_design_results': {'ur_flexure': .85},
        'crossbracing_design_results': {'G1-G2': {'diagonal': {'compression': {'Optimum.UR': .9}}}},
        'end_diaphragm_design_results': {'end': {'chord': {'tension': {'Member.efficiency': .65}}}},
    }
    metadata = ReportMetadata('Synthetic layout fixture', 'Not a bridge design', 'Test', 'Test', 'Test')
    bridge = ReportDataBridge(outputs, inputs, None)
    asset_dir = args.output_dir / 'assets'
    paths = {}
    if not args.baseline:
        from osdagbridge.core.reports.plots import save_plots
        paths = save_plots(outputs, quantities, asset_dir)
        paths = {key: 'assets/' + Path(value).name for key, value in paths.items()}
    parts = [preamble(metadata.project_name, 'Fixture', '2026-11-17'),
             r'\noindent\textbf{Synthetic report layout fixture. Values are test data and are not a bridge design.}',
             ch1_project_info(metadata), ch2_input_parameters(metadata, inputs, outputs),
             ch3_loads(inputs), r'\setcounter{chapter}{4}',
             ch5_design_checks([], bridge) if args.baseline else ch5_design_checks([], bridge, paths),
             r'\setcounter{chapter}{6}',
             ch7_quantities(quantities) if args.baseline else ch7_quantities(quantities, paths),
             r'\end{document}']
    path = args.output_dir / ('Layout_Before.tex' if args.baseline else 'Layout_After.tex')
    path.write_text('\n'.join(parts), encoding='utf-8')
    print(path)


if __name__ == '__main__':
    main()
