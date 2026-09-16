"""Home's GTK4 top bar must match the classic Space's furniture.

Three separate faults, all visible in the same 75px band:

- a Gtk.Box gives its children valign=FILL, so the search entry and the
  view buttons stretched to the whole band (0154);
- the centred clock was never ported (0155);
- the universal help icon was never ported, and rendering its SVG through
  Gtk.Image silently produces an empty image because the file colours
  itself with internal DTD entities (0155).
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / 'patches/gtk4-preview'
CENTRING = PATCHES / '0154-home-toolbar-centres-its-items.patch'
FURNITURE = PATCHES / '0155-home-top-bar-clock-and-help-icon.patch'


def _added(patch):
    return '\n'.join(line[1:] for line in patch.read_text().splitlines()
                     if line.startswith('+') and not line.startswith('+++'))


# --- 0154: stop stretching the toolbar items ------------------------------

def test_search_entry_is_centred_not_stretched():
    assert 'self.search_entry.set_valign(Gtk.Align.CENTER)' in _added(CENTRING)


def test_view_buttons_are_centred_not_stretched():
    added = _added(CENTRING)
    assert 'self._button_box.set_valign(Gtk.Align.CENTER)' in added
    assert 'toolitem.set_valign(Gtk.Align.CENTER)' in added


# --- 0155: the clock ------------------------------------------------------

def test_clock_is_built_and_exposed():
    added = _added(FURNITURE)
    assert 'def _build_clock' in added
    assert 'def get_clock_widget' in added


def test_clock_is_placed_as_an_overlay_child():
    # Keeping it out of the toolbar's allocation flow is what stops the
    # search and view controls from shifting the time sideways.
    added = _added(FURNITURE)
    assert 'self._overlay.add_overlay(self._clock)' in added
    assert 'self._overlay.set_child(self._box)' in added


def test_clock_takes_the_band_height_rather_than_a_margin():
    added = _added(FURNITURE)
    assert 'set_size_request(-1, style.GRID_CELL_SIZE)' in added
    assert 'set_margin_top' not in added


def test_clock_follows_the_aspartame_format_setting():
    added = _added(FURNITURE)
    assert "Gio.Settings.new('org.aspartame.clock')" in added
    assert "changed::format" in added


# --- 0155: the help icon --------------------------------------------------

def test_help_icon_uses_sugars_own_icon_not_gtk_image():
    # Gtk.Image.new_from_file() does not expand the SVG's DTD entities, so
    # the icon rasterises fully transparent.
    added = _added(FURNITURE)
    assert 'Icon(file_name=help_path' in added
    assert 'from sugar4.graphics.icon import Icon' in added
    code = [line for line in added.splitlines()
            if not line.lstrip().startswith('#')]
    assert not any('Gtk.Image.new_from_file' in line for line in code)


def test_help_icon_reuses_the_help_activity_artwork():
    added = _added(FURNITURE)
    assert 'Help.activity/' in added
    assert 'activity-help.svg' in added


def test_help_button_opens_help_and_says_so():
    added = _added(FURNITURE)
    assert "'org.laptop.HelpActivity'" in added
    assert 'misc.launch(bundle)' in added
    assert 'Select-a-Thing' in FURNITURE.read_text(), \
        'the missing GTK3 behaviour must be recorded in the patch'


def test_help_button_degrades_when_the_artwork_is_absent():
    assert 'if not os.path.exists(help_path):' in _added(FURNITURE)


def test_build_routes_both_patches_to_the_shell_checkout():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0154*) target="$root/sources/sugar" ;;' in build
    assert '*0155*) target="$root/sources/sugar" ;;' in build
