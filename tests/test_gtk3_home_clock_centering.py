"""The classic Home clock must sit in the middle of the toolbar band.

The clock is an overlay child, so it is positioned by hand. Offsetting it
by its own natural height centred the label's *line box*; digits occupy
only the ascent of that box, so the time rendered visibly above centre.
Giving the label the toolbar's height and letting it centre its own text
puts the digits in the middle of the band.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOMEWINDOW = ROOT / 'sugar-overlay/src/jarabe/desktop/homewindow.py'


def _source():
    return HOMEWINDOW.read_text()


def test_clock_takes_the_toolbar_height():
    src = _source()
    assert 'self._clock.set_size_request(-1, allocation.height)' in src


def test_clock_no_longer_offsets_by_its_natural_height():
    src = _source()
    assert 'get_preferred_height()' not in src
    assert 'allocation.height - natural' not in src


def test_the_allocation_handler_is_idempotent():
    # set_size_request() inside size-allocate re-runs allocation; bail out
    # when the band has not actually changed.
    src = _source()
    assert 'self._clock_band_height == allocation.height' in src
    assert 'self._clock_band_height = None' in src


def test_clock_stays_an_overlay_child():
    # Keeping it out of the toolbar's allocation flow is what stops the
    # search and view controls from shifting the time sideways.
    src = _source()
    assert 'self._overlay.add_overlay(self._clock)' in src
    assert 'self._clock.set_halign(Gtk.Align.CENTER)' in src
