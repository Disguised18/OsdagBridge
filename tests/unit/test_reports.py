"""Report regressions runnable without Osdag, Qt, CAD or a TeX installation."""
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from osdagbridge.core.reports import report_generator as report
from osdagbridge.core.reports.chap1 import ch1_project_info
from osdagbridge.core.reports.chap2 import ch2_input_parameters
from osdagbridge.core.reports.chap3 import ch3_loads
from osdagbridge.core.reports.chap4 import ch4_analysis
from osdagbridge.core.reports.chap5 import ch5_design_checks
from osdagbridge.core.reports.chap7 import ch7_quantities
from osdagbridge.core.reports.chap8 import ch8_design_log
from osdagbridge.core.reports.plots import (
    material_values, utilization_values, number, save_plots, figure_latex, _bars,
)
from osdagbridge.core.reports.load_tables import selected
from osdagbridge.core.reports.report_utils import _tex
from osdagbridge.core.reports.styles import preamble
from osdagbridge.core.utils import common as keys


@pytest.fixture
def metadata():
    return report.ReportMetadata('Report regression fixture', 'Test location', 'Test', 'Test', 'Test')


@pytest.fixture
def outputs():
    return {
        'design_results': {'per_girder': {
            'G1': {'checks': [{'check_id': 1, 'dcr': .8, 'demand': 80, 'capacity': 100}],
                   'per_lc': {'SLS': {'checks': [{'id': 13, 'dcr': 1.2}]}}},
            'G2': {'checks': [{'check_id': 2, 'dcr': .95}]},
            'EB1': {'checks': [{'dcr': 99}]},
        }},
        'deck_design_results': {'ur_flexure': .75, 'ur_shear': 1.05},
        'crossbracing_design_results': {'G1-G2': {'diagonal': {'compression': {'Optimum.UR': .9}}}},
        'end_diaphragm_design_results': {'end': {'chord': {'tension': {'Member.efficiency': .6}}}},
    }


def assert_headers(tex):
    tables = re.findall(r'\\begin\{longtable\}(.*?)\\end\{longtable\}', tex, re.S)
    assert tables
    for table in tables:
        assert table.count(r'\endfirsthead') == 1
        assert table.count(r'\endhead') == 1
        first, remainder = table.split(r'\endfirsthead')
        continuation, body = remainder.split(r'\endhead')
        assert r'\textbf' in continuation, table[:150]
        assert r'\caption' not in continuation  # repeated captions change numbering
        assert r'\hline' in continuation
        assert body.strip()
        if r'\caption' in first:
            assert re.search(r'\\(?:\n)?\s*\\hline', first), first[:150]


def test_every_table_has_real_continuation_headers(metadata):
    inputs = {keys.KEY_TS_NO_OF_GIRDERS: 4}
    bridge = report.ReportDataBridge({}, inputs, None)
    for tex in (ch1_project_info(metadata), ch2_input_parameters(metadata, inputs, {}),
                ch3_loads(inputs), ch4_analysis({}, {}, bridge, 20),
                ch5_design_checks([], bridge), ch7_quantities({}), ch8_design_log([], {})):
        assert_headers(tex)
        assert tex.count(r'\begingroup') == tex.count(r'\endgroup')
    assert r'\multirow' not in ch5_design_checks([], bridge)


@pytest.mark.parametrize('value,expected', [(False, False), ('False', False), ('0', False),
                                         ('off', False), (True, True), ('true', True), (1, True)])
def test_gui_checkbox_values(value, expected):
    assert selected(value) == expected


def test_vehicle_and_footway_selection():
    inputs = {keys.KEY_LL_IRC_CLASS_A: 'False', keys.KEY_LL_IRC_70R_TRACKED: True,
              keys.KEY_LL_CUSTOM_VEHICLES: [{'name': 'Custom & Heavy_1'}],
              keys.KEY_FOOTPATH: 'Both Sides', keys.KEY_LL_FOOTPATH_PRESSURE_MODE: 'Custom',
              keys.KEY_LL_FOOTPATH_PRESSURE_VALUE: 7.5}
    tex = ch3_loads(inputs)
    vehicle = tex.split('Vehicle Live Loads (LL)')[1].split(r'\end{longtable}')[0]
    footway = tex.split('Footway Live Loads')[1].split(r'\end{longtable}')[0]
    assert 'Class 70R (Tracked)' in vehicle
    assert 'Class A' not in vehicle
    assert r'Custom \& Heavy\_\allowbreak{}1' in vehicle
    assert '7.5' in footway and 'kN/m$^2$' in footway
    assert 'Footway live load' not in vehicle
    inputs[keys.KEY_FOOTPATH] = 'None'
    tex = ch3_loads(inputs).split('Footway Live Loads')[1].split(r'\end{longtable}')[0]
    assert 'Not applicable' in tex and '7.5' not in tex


def test_automatic_footway_and_no_vehicles():
    tex = ch3_loads({keys.KEY_FOOTPATH: 'Single Side', keys.KEY_LL_FOOTPATH_PRESSURE_MODE: 'As per IRC 6'})
    assert 'None selected' in tex and '4.905' in tex


def test_ur_uses_ratios_all_members_and_all_cases(outputs):
    assert list(utilization_values(outputs).values()) == [1.2, 1.05, .9, .6]
    assert all(v is None for v in utilization_values({}).values())


@pytest.mark.parametrize('value', [None, 'N.A.', 'bad', float('inf'), float('nan'), -1, True])
def test_invalid_data_is_not_zero(value):
    assert number(value) is None


def test_quantities_preserve_units_and_avoid_partial_sums():
    values = {'steel_girders_wt_total': 10, 'bracing_top_wt_total': 1,
              'bracing_bot_wt_total': 2, 'bracing_diag_wt_total': 3,
              'concrete_deck_vol_total': 24, 'rebar_deck_wt_total': 2.88}
    data = material_values(values)
    assert data == {'Girders': 10, 'Cross bracing': 6, 'End diaphragms': None,
                    'Concrete': 24, 'Reinforcement': 2.88}
    del values['bracing_bot_wt_total']
    assert material_values(values)['Cross bracing'] is None
    values['steel_bracing_wt_total'] = 6
    assert material_values(values)['Cross bracing'] == 6


def test_plots_write_real_png_and_embed_in_requested_sections(tmp_path, outputs):
    paths = save_plots(outputs, {}, tmp_path)
    for path in paths.values():
        assert Path(path).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    from matplotlib.figure import Figure
    ax = Figure().subplots()
    _bars(ax, {'pass': .8, 'fail': 1.2, 'missing': None, 'zero': 0}, 'Utilization Ratio', True)
    assert len(ax.patches) == 3  # missing value has text, no fabricated zero bar
    assert ax.get_xlim()[1] > 3  # include missing and zero categories in the view
    assert list(ax.lines[0].get_ydata()) == [1.0, 1.0]
    assert ax.lines[0].get_linestyle() == '--'
    bridge = report.ReportDataBridge({}, {}, None)
    tex = ch5_design_checks([], bridge, paths)
    assert tex.index('utilization.png') > tex.index(r'\label{sec:overall-summary}')
    assert 'structural_steel.png' in ch7_quantities({}, paths)
    assert 'concrete_reinforcement.png' in ch7_quantities({}, paths)
    assert figure_latex(None, 'Caption') == ''


def test_shared_styles_reserve_footer_space():
    tex = preamble('Project', 'Job', 'Date')
    assert 'includeheadfoot' in tex and 'footskip=18mm' in tex and 'bottom=32mm' in tex
    assert r'\vspace{-20pt}' not in tex
    assert r'\Needspace{7\baselineskip}' in tex
    assert r'\titleformat{\chapter}' in tex  # chapter styling also applies without a TOC
    assert _tex('A\\B_{x}&') == r'A\textbackslash{}B\_\allowbreak{}\{x\}\&'


def test_full_pipeline_keeps_assets_and_rejects_stale_pdf(tmp_path, monkeypatch, metadata):
    options = report.ReportOptions(['loads', 'design_checks'], True, False, True)
    payload = report.ReportPayload(metadata, options, {}, {}, [], report.ReportFigures())
    request = report.ReportRequest(metadata, options, str(tmp_path), 'Report_After')
    stale = tmp_path / 'Report_After.pdf'
    stale.write_bytes(b'stale PDF must not count as successful generation')
    monkeypatch.setattr(report.subprocess, 'run', lambda *a, **k: SimpleNamespace(
        returncode=1, stdout=b'compiler unavailable in test', stderr=b''))
    result = report.generate_report(payload, request)
    assert result.pdf_path is None
    assert result.tex_path is not None
    tex = Path(result.tex_path).read_text(encoding='utf-8')
    assert 'Report_After_assets/utilization.png' in tex
    assert 'Report_After_Report_After_assets' not in tex
    assert (tmp_path / 'Report_After_assets/utilization.png').exists()
    assert str(tmp_path).replace('\\', '/') not in tex
    assert_headers(tex)


def test_disabled_figures_skip_plots_and_missing_compiler_keeps_tex(tmp_path, monkeypatch, metadata):
    options = report.ReportOptions(['loads'], False, False, True)
    payload = report.ReportPayload(metadata, options, {}, {}, [], report.ReportFigures())
    request = report.ReportRequest(metadata, options, str(tmp_path), 'No_Figures')
    def no_plot(*args, **kwargs):
        pytest.fail('Charts must respect include_figures=False')
    def missing_compiler(*args, **kwargs):
        raise FileNotFoundError('pdflatex missing')
    monkeypatch.setattr(report, 'save_plots', no_plot)
    monkeypatch.setattr(report.subprocess, 'run', missing_compiler)
    result = report.generate_report(payload, request)
    assert result.pdf_path is None and Path(result.tex_path).exists()
    assert 'utilization.png' not in Path(result.tex_path).read_text(encoding='utf-8')


def test_successful_compiler_returns_new_pdf(tmp_path, monkeypatch, metadata):
    options = report.ReportOptions([], False, False, True)
    payload = report.ReportPayload(metadata, options, {}, {}, [], report.ReportFigures())
    request = report.ReportRequest(metadata, options, str(tmp_path), 'Fresh')
    def compiler(args, **kwargs):
        (Path(kwargs['cwd']) / 'Fresh.pdf').write_bytes(b'%PDF-test-compiler-output')
        return SimpleNamespace(returncode=0, stdout=b'', stderr=b'')
    monkeypatch.setattr(report.subprocess, 'run', compiler)
    result = report.generate_report(payload, request)
    assert Path(result.pdf_path).read_bytes() == b'%PDF-test-compiler-output'
