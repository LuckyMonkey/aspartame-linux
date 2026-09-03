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
            self.assertEqual(result[0]['icon'], '')

    def test_malformed_activity_does_not_hide_valid_activities(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "activities"
            good = root / "Good.activity" / "activity"
            bad = root / "Bad.activity" / "activity"
            good.mkdir(parents=True)
            bad.mkdir(parents=True)
            (good / "activity.info").write_text(
                "[Activity]" + chr(10) + "name = Good" + chr(10),
                encoding="utf-8")
            (bad / "activity.info").write_text(
                "[Activity" + chr(10) + "name = Bad" + chr(10),
                encoding="utf-8")
            result = model.list_activities((str(root),))
            self.assertEqual([item["name"] for item in result], ["Good"])

    def test_user_copy_wins_over_system_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            system = Path(directory) / "system"
            user = home / ".local/share/sugar/activities"
            for root, name in ((system, "System Copy"), (user, "User Copy")):
                activity = root / "same.activity" / "activity"
                activity.mkdir(parents=True)
                (activity / "activity.info").write_text(
                    "[Activity]" + chr(10) + "name = " + name + chr(10) +
                    "bundle_id = org.example.Same" + chr(10),
                    encoding="utf-8")
            old_home = os.environ.get("HOME")
            os.environ["HOME"] = str(home)
            try:
                result = model.list_activities((str(system), str(user)))
            finally:
                if old_home is None:
                    os.environ.pop("HOME", None)
                else:
                    os.environ["HOME"] = old_home
            self.assertEqual(result[0]["name"], "User Copy")

    def test_activity_metadata_preserves_icon_and_cleans_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'activities'
            activity = root / 'Example.activity' / 'activity'
            activity.mkdir(parents=True)
            (activity / 'activity.info').write_text(
                '[Activity]\nname = Example\nbundle_id = org.example.Activity\n'
                'icon = activity-generic\nsummary =   A useful thing.  \n',
                encoding='utf-8')
            result = model.list_activities((str(root),))
            self.assertEqual(result[0]['icon'], 'activity-generic')
            self.assertEqual(result[0]['summary'], 'A useful thing.')

    def test_ratings_are_persistent_and_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, 'ratings.json')
            model.save_rating('org.aspartame.Count', 5, filename)
            self.assertEqual(model.load_ratings(filename)['org.aspartame.Count'], 5)
            with self.assertRaises(ValueError):
                model.save_rating('org.aspartame.Count', 6, filename)

    def test_clearing_rating_removes_the_answer(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "ratings.json")
            model.save_rating("org.aspartame.Count", 5, filename)
            model.clear_rating("org.aspartame.Count", filename)
            self.assertNotIn("org.aspartame.Count", model.load_ratings(filename))

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

    def test_system_activity_hide_is_persistent_and_reversible(self):
        with tempfile.TemporaryDirectory() as directory:
            favorites = os.path.join(directory, 'favorite_activities')
            model.set_activity_hidden('org.example.Activity', '7', True,
                                      favorites)
            self.assertTrue(model.is_activity_hidden(
                'org.example.Activity', '7', favorites))
            model.set_activity_hidden('org.example.Activity', '7', False,
                                      favorites)
            self.assertFalse(model.is_activity_hidden(
                'org.example.Activity', '7', favorites))
            data = json.loads(Path(favorites).read_text(encoding='utf-8'))
            self.assertEqual(data['favorites']['org.example.Activity 7'],
                             {'favorite': True})

    def test_system_activity_paths_are_managed_by_remover_policy(self):
        self.assertIn('/usr/share/sugar/activities', model.MANAGED_SYSTEM_ROOTS)
        self.assertIn('/usr/share/aspartame/activities', model.MANAGED_SYSTEM_ROOTS)
        self.assertIn('/usr/local/share/sugar/activities', model.MANAGED_SYSTEM_ROOTS)
        self.assertTrue(model.SYSTEM_REMOVER.endswith('aspartame-remove-activity'))


if __name__ == '__main__':
    unittest.main()
