import json
import os
import tempfile
import unittest

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'archiso/aspartame/airootfs/usr/share/aspartame/cpsection/activities'
import sys
sys.path.insert(0, str(MODEL.parent))
from activities import model


class ActivityManagerModelTests(unittest.TestCase):
    def test_rating_scale_has_five_preserved_values(self):
        self.assertEqual(
            model.RATINGS,
            ('Broken', 'Bad', 'Needs work', 'Good', 'Perfect'))

    def test_lists_activity_info_and_prefers_first_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'activities'
            activity = root / 'Count.activity' / 'activity'
            activity.mkdir(parents=True)
            (activity / 'activity.info').write_text(
                '[Activity]\nname = Count\nbundle_id = org.aspartame.Count\nactivity_version = 7\n',
                encoding='utf-8')
            result = model.list_activities((str(root),))
            self.assertEqual(result[0]['id'], 'org.aspartame.Count')
            self.assertEqual(result[0]['version'], '7')

    def test_ratings_are_persistent_and_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, 'ratings.json')
            model.save_rating('org.aspartame.Count', 5, filename)
            self.assertEqual(model.load_ratings(filename)['org.aspartame.Count'], 5)
            with self.assertRaises(ValueError):
                model.save_rating('org.aspartame.Count', 6, filename)

    def test_user_activity_removal_is_recoverable(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / 'home'
            user_root = home / '.local/share/sugar/activities'
            bundle = user_root / 'Example.activity' / 'activity'
            bundle.mkdir(parents=True)
            (bundle / 'activity.info').write_text('[Activity]\nname = Example\n', encoding='utf-8')
            old_home = os.environ.get('HOME')
            os.environ['HOME'] = str(home)
            try:
                target = model.remove_activity(str(bundle.parent), str(home / 'quarantine'))
                self.assertFalse(bundle.parent.exists())
                self.assertTrue(os.path.isdir(target))
            finally:
                if old_home is None:
                    os.environ.pop('HOME', None)
                else:
                    os.environ['HOME'] = old_home


if __name__ == '__main__':
    unittest.main()
