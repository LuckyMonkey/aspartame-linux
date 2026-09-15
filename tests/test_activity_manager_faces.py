"""Focused UI tests for the Activity Manager face-rating control.

These construct the real GTK3 widget rather than asserting on source text,
so face selection, keyboard reachability, and accessible naming are checked
as behavior.
"""

import sys
import unittest
from pathlib import Path

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
PACKAGED = ROOT / 'archiso/aspartame/airootfs/usr/share/aspartame'
sys.path.insert(0, str(PACKAGED))
sys.path.insert(0, str(PACKAGED / 'cpsection'))

from activities.rating_faces import FaceRating, RATING_LABELS  # noqa: E402


class FaceRatingTests(unittest.TestCase):
    def test_unanswered_is_a_valid_state(self):
        rating = FaceRating()
        self.assertEqual(rating.get_rating(), 0)
        self.assertFalse(any(button.get_active()
                             for button in rating.get_buttons()))

    def test_five_faces_are_offered(self):
        rating = FaceRating()
        self.assertEqual(len(rating.get_buttons()), 5)
        self.assertEqual(len(RATING_LABELS), 5)

    def test_selecting_a_face_deselects_the_previous_one(self):
        rating = FaceRating()
        buttons = rating.get_buttons()
        buttons[3].set_active(True)
        self.assertEqual(rating.get_rating(), 4)
        buttons[0].set_active(True)
        self.assertEqual(rating.get_rating(), 1)
        self.assertEqual([button.get_active() for button in buttons],
                         [True, False, False, False, False])

    def test_deselecting_returns_to_unanswered(self):
        rating = FaceRating(rating=2)
        self.assertEqual(rating.get_rating(), 2)
        rating.get_buttons()[1].set_active(False)
        self.assertEqual(rating.get_rating(), 0)

    def test_rating_changed_reports_the_selected_face(self):
        rating = FaceRating()
        seen = []
        rating.connect('rating-changed', lambda _widget, value: seen.append(value))
        rating.get_buttons()[4].set_active(True)
        self.assertEqual(seen, [5])

    def test_out_of_range_rating_is_treated_as_unanswered(self):
        self.assertEqual(FaceRating(rating=9).get_rating(), 0)
        self.assertEqual(FaceRating(rating=-1).get_rating(), 0)

    def test_selected_face_carries_the_selection_style_class(self):
        rating = FaceRating()
        button = rating.get_buttons()[2]
        self.assertFalse(button.get_style_context().has_class(
            'aspartame-rating-selected'))
        button.set_active(True)
        self.assertTrue(button.get_style_context().has_class(
            'aspartame-rating-selected'))
        button.set_active(False)
        self.assertFalse(button.get_style_context().has_class(
            'aspartame-rating-selected'))

    def test_every_face_is_reachable_without_a_pointer(self):
        rating = FaceRating()
        for button in rating.get_buttons():
            self.assertTrue(button.get_can_focus())

    def test_every_face_has_an_accessible_name_and_description(self):
        rating = FaceRating(context='Count')
        names = [button.get_accessible().get_name()
                 for button in rating.get_buttons()]
        self.assertEqual(names, list(RATING_LABELS))
        for button in rating.get_buttons():
            description = button.get_accessible().get_description()
            self.assertIn('Count', description)

    def test_missing_face_artwork_still_produces_a_usable_control(self):
        rating = FaceRating(face_root='/nonexistent/aspartame/faces')
        self.assertEqual(len(rating.get_buttons()), 5)
        rating.get_buttons()[2].set_active(True)
        self.assertEqual(rating.get_rating(), 3)


if __name__ == '__main__':
    unittest.main()
