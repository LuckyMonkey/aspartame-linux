from pathlib import Path


ROOT = Path(__file__).parents[1]
PATCH = ROOT / "patches/gtk4-preview/0028-toolkit-sugar-interactions.patch"


def _changed_lines(prefix):
    return {
        line[1:]
        for line in PATCH.read_text().splitlines()
        if line.startswith(prefix) and not line.startswith(prefix * 3)
    }


def test_canvas_icons_have_one_primary_activation_path():
    added = _changed_lines("+")
    removed = _changed_lines("-")

    assert "        click_gesture.set_button(1)" in added
    assert (
        '        click_gesture.connect("pressed", self._on_canvas_pressed)'
        in removed
    )
    assert (
        '        click_gesture.connect("released", self._on_canvas_released)'
        in removed
    )
    assert "        super()._on_pressed(gesture, n_press, x, y)" in added
    assert "        super()._on_released(gesture, n_press, x, y)" in added


def test_svg_scaling_and_toolbar_snapshotting_are_native_and_theme_driven():
    patch = PATCH.read_text()
    added = _changed_lines("+")
    removed = _changed_lines("-")

    assert "        ) * max(0.0, self.scale)" in added
    assert "        ctx.scale(render_scale, render_scale)" in added
    assert "        super().do_snapshot(snapshot)" in added
    assert "        Gtk.Widget.do_snapshot(self, snapshot)" in removed
    assert "@theme_selected_bg_color" in patch
    assert "+" + "@theme_selected_bg_color" not in patch


def test_toolbuttons_use_only_sugar_palettes_for_tooltips():
    added = _changed_lines("+")
    removed = _changed_lines("-")

    assert "        self.set_tooltip_text(None)" in added
    assert "        self.set_tooltip_text(tooltip)" in removed
    assert "    def _apply_toolbar_button_css(self):" in removed
    assert "def _apply_module_css():" in removed


def test_activity_toolbar_uses_bundle_icon_and_canonical_stop_button():
    added = _changed_lines("+")

    assert (
        "from sugar4.bundle.activitybundle import get_bundle_instance" in added
    )
    assert "            bundle = get_bundle_instance(get_bundle_path())" in added
    assert "            icon_name = bundle.get_icon()" in added
    assert (
        "        ToolButton.__init__(self, icon_name=icon_name, **kwargs)" in added
    )


def test_palettes_are_anchored_popovers_without_nested_windows():
    added = _changed_lines("+")
    removed = _changed_lines("-")

    assert "class _PaletteWindowWidget(Gtk.Popover):" in added
    assert "class _PaletteWindowWidget(Gtk.Window):" in removed
    assert "            self._widget = Gtk.Window()" in removed
    assert "        self.set_child(widget)" in added
    assert '        self.add_css_class("sugar-palette")' in added
    assert '            self._widget.connect("show", self.__show_cb)' in added
    assert '            self._widget.connect("hide", self.__hide_cb)' in added


def test_palette_menu_activation_is_guarded_and_uses_global_sugar_css():
    patch = PATCH.read_text()
    css = (ROOT / "assets/gtk4/sugar.css").read_text()
    added = _changed_lines("+")
    removed = _changed_lines("-")

    assert '        self.connect("clicked", self._clicked_cb)' in added
    assert '        self.connect("activate", self._clicked_cb)' in removed
    assert "    def do_activate(self):" in added
    assert "        if self._forwarding_activate:" in added
    assert "force-black" in patch
    assert all("force-black" not in line for line in added)

    for selector in (
        "button.toolbar-button",
        ".canvas-icon:hover",
        "popover.sugar-palette > contents",
        "button.palette-menu-item",
        "separator.palette-menu-separator",
        "tooltip.background",
    ):
        assert selector in css
    assert "@theme_selected" not in css
