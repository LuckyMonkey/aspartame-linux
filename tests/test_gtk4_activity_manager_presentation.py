import importlib.util
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PRESENTATION = ROOT / 'gtk4-overlay/src/cpsection/activities/presentation.py'


def load_presentation():
    spec = importlib.util.spec_from_file_location('gtk4_activity_presentation', PRESENTATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_activity_icon_resolution_supports_bundle_relative_svg_and_fallback():
    presentation = load_presentation()
    with tempfile.TemporaryDirectory() as directory:
        bundle = Path(directory) / 'Count.activity'
        (bundle / 'activity').mkdir(parents=True)
        icon = bundle / 'activity' / 'count.svg'
        icon.write_text('<svg/>', encoding='utf-8')
        activity = {'path': str(bundle), 'icon': 'count'}
        assert presentation.activity_icon_file(activity) == str(icon)
        assert presentation.activity_icon_file({
            'path': str(bundle), 'icon': 'missing'}) is None


def test_activity_row_data_keeps_metadata_and_action_contract_stable():
    presentation = load_presentation()
    row = presentation.activity_row_data({
        'id': 'org.example.Count',
        'name': 'Count',
        'summary': 'Count things.  ',
        'runtime': 'native-sugar',
        'version': 7,
        'managed': True,
        'removable': True,
        'launchable': False,
    })
    assert row == {
        'name': 'Count',
        'summary': 'Count things.',
        'runtime': 'native-sugar',
        'version': '7',
        'managed': True,
        'removable': True,
        'launchable': False,
        'action_enabled': True,
    }


def test_activity_manager_wires_icon_slot_and_description_fallback():
    view = (ROOT / 'gtk4-overlay/src/cpsection/activities/view.py').read_text()
    model = (ROOT / 'gtk4-overlay/src/cpsection/activities/model.py').read_text()
    assert 'activity_icon = Icon(pixel_size=style.STANDARD_ICON_SIZE)' in view
    assert '_set_activity_icon(activity_icon, activity)' in view
    assert "_('No description available.')" in view
    assert "'icon': str(getattr(bundle, 'get_icon'" in model
    assert "'summary': str(getattr(bundle, 'get_summary'" in model
