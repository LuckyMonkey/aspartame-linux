import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / 'gtk4-overlay/src/cpsection/activities/model.py'


def load_model():
    jarabe = types.ModuleType('jarabe')
    jarabe_model = types.ModuleType('jarabe.model')
    jarabe_model.bundleregistry = types.SimpleNamespace(
        get_registry=lambda: [])
    jarabe.model = jarabe_model
    with mock.patch.dict(sys.modules, {
            'jarabe': jarabe, 'jarabe.model': jarabe_model}):
        spec = importlib.util.spec_from_file_location(
            'gtk4_snakepit_model', MODEL_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class SnakepitActivityManagerTests(unittest.TestCase):
    def test_records_are_truthful_and_failed_records_are_not_launchable(self):
        model = load_model()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'records'
            root.mkdir()
            source = Path(directory) / 'source'
            source.mkdir()
            environment = Path(directory) / 'environment'
            (environment / 'bin').mkdir(parents=True)
            (environment / 'bin' / 'python').write_text('', encoding='utf-8')
            qualified = {
                'schema': model.SNAKEPIT_SCHEMA,
                'status': 'PASS',
                'software': {'name': 'Demo Python'},
                'interpreter': {'version': 'Python 3.14.7'},
                'launch': {
                    'command': [sys.executable, '-c', 'print("ok")'],
                    'cwd': str(source),
                    'environment': str(environment),
                },
            }
            failed = {
                'schema': model.SNAKEPIT_SCHEMA,
                'status': 'FAIL',
                'software': {'name': 'Not Ready'},
                'error': 'requires Python 99',
            }
            (root / 'qualified.json').write_text(
                json.dumps(qualified), encoding='utf-8')
            (root / 'failed.json').write_text(
                json.dumps(failed), encoding='utf-8')
            old = os.environ.get('ASPARTAME_SNAKEPIT_RECORD_DIR')
            os.environ['ASPARTAME_SNAKEPIT_RECORD_DIR'] = str(root)
            try:
                rows = model.list_snakepit_activities()
            finally:
                if old is None:
                    os.environ.pop('ASPARTAME_SNAKEPIT_RECORD_DIR', None)
                else:
                    os.environ['ASPARTAME_SNAKEPIT_RECORD_DIR'] = old
            by_name = {row['name']: row for row in rows}
            self.assertTrue(by_name['Demo Python']['launchable'])
            self.assertTrue(by_name['Demo Python']['installed'])
            self.assertFalse(by_name['Demo Python']['removable'])
            self.assertEqual(by_name['Demo Python']['runtime'], 'snakepit-python')
            self.assertFalse(by_name['Not Ready']['launchable'])
            self.assertFalse(by_name['Not Ready']['installed'])
            self.assertFalse(by_name['Not Ready']['removable'])

    def test_launch_uses_the_record_environment_without_removal(self):
        model = load_model()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'records'
            root.mkdir()
            source = Path(directory) / 'source'
            source.mkdir()
            environment = Path(directory) / 'environment'
            (environment / 'bin').mkdir(parents=True)
            (environment / 'bin' / 'python').write_text('', encoding='utf-8')
            record = root / 'demo.json'
            record.write_text(json.dumps({
                'schema': model.SNAKEPIT_SCHEMA,
                'status': 'PASS',
                'software': {'name': 'Demo'},
                'launch': {
                    'command': ['/usr/bin/python3', '-c', 'print("ok")'],
                    'cwd': str(source),
                    'environment': str(environment),
                },
            }), encoding='utf-8')
            old = os.environ.get('ASPARTAME_SNAKEPIT_RECORD_DIR')
            os.environ['ASPARTAME_SNAKEPIT_RECORD_DIR'] = str(root)
            try:
                activity = {'runtime': 'snakepit-python', 'record': str(record)}
                with mock.patch.object(model.subprocess, 'Popen') as popen:
                    model.launch_activity(activity)
                command, kwargs = popen.call_args
            finally:
                if old is None:
                    os.environ.pop('ASPARTAME_SNAKEPIT_RECORD_DIR', None)
                else:
                    os.environ['ASPARTAME_SNAKEPIT_RECORD_DIR'] = old
            self.assertEqual(command[0][0], '/usr/bin/python3')
            self.assertEqual(kwargs['cwd'], str(source))
            self.assertEqual(kwargs['env']['VIRTUAL_ENV'], str(environment))
            self.assertEqual(kwargs['env']['PYTHONNOUSERSITE'], '1')
            self.assertTrue(kwargs['start_new_session'])


if __name__ == '__main__':
    unittest.main()
