"""Presentation of selected live loads; no new load calculations."""
from .report_utils import _tex
from .styles import report_section
from osdagbridge.core.utils.common import (
    KEY_FOOTPATH, KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE, KEY_BL_IRC_CLASS_SV,
)


def selected(value):
    """Accept GUI booleans and serialized checkbox values without truthy 'False'."""
    return value is True or value == 1 or str(value).strip().lower() in {'true', 'yes', 'on', 'checked'}


def _table(caption, rows):
    header = (r'\hline' + '\n' + r'\textbf{Parameter} & \textbf{Value} & \textbf{Unit} \\'
              + '\n' + r'\hline' + '\n')
    return (r'\begin{longtable}{|L{4.0cm}|L{9.0cm}|C{2.0cm}|}' + '\n'
            + r'\caption{' + caption + r'}\\' + '\n' + header
            + r'\endfirsthead' + '\n' + header + r'\endhead' + '\n'
            + '\n'.join(_tex(label) + ' & ' + _tex(value) + ' & ' + unit + r' \\'
                        + '\n' + r'\hline' for label, value, unit in rows)
            + '\n' + r'\end{longtable}')


@report_section
def live_load_tables(inputs, vehicles, impact, braking):
    vehicle_rows = [('Selected vehicle class', vehicle, '--') for vehicle in vehicles]
    if not vehicle_rows:
        vehicle_rows = [('Selected vehicle class', 'None selected', '--')]
    vehicle_rows += [
        ('Dynamic load multiplier (1 + IM)', impact if vehicles else 'Not applicable', '--'),
        ('Braking load', braking.split(' kN')[0] if vehicles else 'Not applicable', 'kN'),
        ('Class SV braking enabled', 'Yes' if selected(inputs.get(KEY_BL_IRC_CLASS_SV)) else 'No', '--'),
        ('Centrifugal force', 'N/A: not supplied by the current analysis', 'kN'),
    ]
    footpath = str(inputs.get(KEY_FOOTPATH, '')).strip()
    if footpath.lower() in {'none', 'no', 'false', '0'}:
        footway_rows = [('Footway configuration', 'None', '--'),
                        ('Footway live load', 'Not applicable', r'kN/m$^2$')]
    else:
        mode = str(inputs.get(KEY_LL_FOOTPATH_PRESSURE_MODE, ''))
        pressure = inputs.get(KEY_LL_FOOTPATH_PRESSURE_VALUE)
        if mode.strip().lower() in {'as per irc 6', 'as per irc6', 'automatic'}:
            from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017
            pressure = IRC6_2017.cl_206_1_footway_load()
        footway_rows = [('Footway configuration', footpath or 'Not supplied', '--'),
                        ('Pressure mode', mode or 'Not supplied', '--'),
                        ('Footway live load', pressure if pressure not in ('', None) else 'N/A', r'kN/m$^2$')]
    return _table('Vehicle Live Loads (LL)', vehicle_rows) + '\n' + _table('Footway Live Loads', footway_rows)
