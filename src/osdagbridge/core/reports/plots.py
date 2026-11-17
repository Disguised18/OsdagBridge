"""Read stored results and produce report-only plots without a GUI backend.

Ratios are dimensionless (never percentages). Missing, negative and nonfinite
values are not drawn as zero. No structural design is performed here.
"""
from pathlib import Path
import math

from .styles import CHART, FIGURE_WIDTH


def number(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) and result >= 0 else None


def maximum(values):
    valid = [v for value in values if (v := number(value)) is not None]
    return max(valid) if valid else None


def member_ur(results):
    """Osdag tension/compression result schemas, same keys as results_data."""
    values = []
    for members in (results or {}).values():
        for forces in (members or {}).values():
            for raw in (forces or {}).values():
                if isinstance(raw, dict):
                    values.append(osdag_summary(raw)['efficiency'])
    return maximum(values)


def osdag_summary(result):
    """Read the two serialized Osdag member schemas without analysis imports."""
    result = result or {}
    def first(*keys):
        return next((result[k] for k in keys if result.get(k) is not None), None)
    return {
        'section': first('section_size.designation', 'Optimum.Designation'),
        'capacity_kN': first('Member.tension_capacity', 'Design.Strength'),
        'efficiency': first('Member.efficiency', 'Optimum.UR'),
        'slenderness': result.get('Member.Slenderness'),
        'connection': 'Welded' if 'Weld.Type' in result else 'Bolted',
    }


def utilization_values(outputs):
    girder_urs = []
    for label, girder in ((outputs.get('design_results') or {}).get('per_girder', {}) or {}).items():
        if str(label).startswith('EB'):
            continue
        girder_urs.extend(c.get('dcr') for c in (girder.get('checks') or []))
        for case in (girder.get('per_lc') or {}).values():
            girder_urs.extend(c.get('dcr') for c in (case.get('checks') or []))
    return {
        'Steel plate\ngirders': maximum(girder_urs),
        'Concrete\ndeck slab': maximum(v for k, v in (outputs.get('deck_design_results') or {}).items()
                                        if str(k).startswith('ur_')),
        'Cross\nbracing': member_ur(outputs.get('crossbracing_design_results')),
        'End\ndiaphragms': member_ur(outputs.get('end_diaphragm_design_results')),
    }


def material_values(quantities):
    bracing = [number(quantities.get(f'bracing_{part}_wt_total')) for part in ('top', 'bot', 'diag')]
    # Prefer the component sum. A partial sum would understate the total.
    bracing_total = sum(bracing) if all(v is not None for v in bracing) else number(quantities.get('steel_bracing_wt_total'))
    return {
        'Girders': number(quantities.get('steel_girders_wt_total')),
        'Cross bracing': bracing_total,
        # The current BOQ does not calculate this value. Accept it when supplied;
        # never substitute cross-bracing quantities for an end diaphragm.
        'End diaphragms': number(quantities.get('end_diaphragms_wt_total')),
        'Concrete': number(quantities.get('concrete_deck_vol_total')),
        'Reinforcement': number(quantities.get('rebar_deck_wt_total')),
    }


def _figure(width=8, height=3.8):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    fig = Figure(figsize=(width, height), layout='constrained')
    FigureCanvasAgg(fig)  # no pyplot, global backend switch or GUI-thread state
    return fig


def _bars(ax, values, ylabel, threshold=False):
    ax.set_ylabel(ylabel, fontsize=CHART['font_size'])
    ax.set_xticks(range(len(values)), list(values), fontsize=CHART['font_size'])
    # Missing categories have no rectangle, so autoscaling cannot discover them.
    ax.set_xlim(-.6, len(values) - .4)
    highest = max([v for v in values.values() if v is not None] + [1.0])
    ax.set_ylim(0, highest * 1.3)
    ax.set_axisbelow(True)
    ax.grid(axis='y', alpha=0.2)
    for i, val in enumerate(values.values()):
        if val is None:
            ax.text(i, highest * .06, 'N/A', ha='center', color=CHART['missing'], fontsize=CHART['font_size'])
            continue
        color = CHART['fail'] if threshold and val > 1 else CHART['pass'] if threshold else CHART['neutral']
        ax.bar(i, val, color=color, width=.55)
        ax.text(i, val + highest * .025, f'{val:.3g}', ha='center', fontsize=CHART['font_size'])
    if threshold:
        ax.axhline(1.0, color=CHART['fail'], linestyle='--', label='UR = 1.0')
        ax.legend(loc='upper right', fontsize=CHART['font_size'])


def save_plots(outputs, quantities, asset_dir, include_ur=True):
    """Save figures inside the caller's temporary report directory."""
    directory = Path(asset_dir)
    directory.mkdir(parents=True, exist_ok=True)
    paths = {}
    if include_ur:
        fig = _figure()
        _bars(fig.subplots(), utilization_values(outputs), 'Utilization Ratio', threshold=True)
        path = directory / 'utilization.png'
        fig.savefig(path, dpi=CHART['dpi'])
        fig.clear()
        paths['utilization'] = str(path)
    materials = material_values(quantities)
    fig = _figure()
    _bars(fig.subplots(), {k: materials[k] for k in ('Girders', 'Cross bracing', 'End diaphragms')}, 'Structural steel (MT)')
    path = directory / 'structural_steel.png'
    fig.savefig(path, dpi=CHART['dpi'])
    fig.clear()
    paths['structural_steel'] = str(path)
    fig = _figure()
    left, right = fig.subplots(1, 2)
    _bars(left, {'Concrete': materials['Concrete']}, 'Concrete volume (m³)')
    _bars(right, {'Reinforcement': materials['Reinforcement']}, 'Reinforcement steel (MT)')
    path = directory / 'concrete_reinforcement.png'
    fig.savefig(path, dpi=CHART['dpi'])
    fig.clear()
    paths['concrete_reinforcement'] = str(path)
    return paths


def figure_latex(path, caption):
    if not path:
        return ''
    from pylatex import Figure, NoEscape
    figure = Figure(position='H')
    figure.add_image(str(path).replace('\\', '/'), width=NoEscape(FIGURE_WIDTH))
    figure.add_caption(caption)
    return figure.dumps()
