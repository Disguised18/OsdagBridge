"""Run a reproducible backend design, preserving inputs and result evidence."""
import json
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from pathlib import Path
from osdagbridge.desktop import __main__ as desktop
from osdagbridge.core.bridge_types.plate_girder.defaults import BASIC_INPUT_DICT, solve_extend_basic_input_dict
from osdagbridge.core.bridge_types.plate_girder.ui_fields_project_location import get_state_list, get_station_list, get_weather
from osdagbridge.core.utils.common import *


def main():
    from PySide6.QtWidgets import QApplication
    from osdagbridge.desktop.ui.docks.input_dock import MaterialPropertiesDialog
    app = QApplication.instance() or QApplication([])
    folder = Path('validation/design')
    folder.mkdir(parents=True, exist_ok=True)
    inputs = dict(BASIC_INPUT_DICT)
    state = next(s for s in get_state_list(False) if 'MAHARASHTRA' in s.upper())
    station = get_station_list(state, False)[0]
    weather = get_weather(state, station)
    inputs.update({KEY_SPAN: 20, KEY_CARRIAGEWAY_WIDTH: 7.5, KEY_SKEW_ANGLE: 0,
                   KEY_PROJECT_LOCATION: {'method': 'location_name', 'data': {'state': state, 'district': station}}})
    inputs.update({'wind_speed': weather['wind_speed'], 'seismic_zone': weather['zone'],
                   'shade_temp_max': weather['max_temp'], 'shade_temp_min': weather['min_temp'],
                   'latitude': weather['latitude'], 'longitude': weather['longitude']})
    solve_extend_basic_input_dict(inputs)
    for key in (KEY_GIRDER, KEY_CROSS_BRACING, KEY_END_DIAPHRAGM, KEY_DECK_CONCRETE_GRADE_BASIC):
        dialog = MaterialPropertiesDialog(read_only=True, selected_material=inputs[key], member=key)
        inputs.update(dialog.get_export_fields() or {})
    (folder / 'inputs.json').write_text(json.dumps(inputs, indent=2, default=str))
    bridge = desktop.PlateGirderBridge()
    bridge.set_input(inputs)
    bridge.design()
    outputs = dict(bridge.output_dict)
    (folder / 'outputs.json').write_text(json.dumps(outputs, indent=2, default=str))
    print('DESIGN_OUTPUT_SAVED', len(outputs), flush=True)


if __name__ == '__main__':
    main()
