"""GTK4-native About my Computer view."""

from gettext import gettext as _

from gi.repository import Gtk

from sugar4.graphics import style

from jarabe import config
from jarabe.controlpanel.sectionview import SectionView


class AboutComputer(SectionView):
    def __init__(self, model, alerts=None):
        super().__init__()
        self._model = model

        self.set_margin_top(style.DEFAULT_SPACING * 2)
        self.set_margin_bottom(style.DEFAULT_SPACING * 2)
        self.set_margin_start(style.DEFAULT_SPACING * 2)
        self.set_margin_end(style.DEFAULT_SPACING * 2)
        self.set_spacing(style.DEFAULT_SPACING)
        self._group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        scrollwindow = Gtk.ScrolledWindow()
        scrollwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrollwindow.set_vexpand(True)
        scrollwindow.set_hexpand(True)
        self.append(scrollwindow)

        self._vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrollwindow.set_child(self._vbox)

        self._setup_identity()
        self._setup_system()
        self._setup_software()
        self._setup_copyright()

    def create_information_box(self, label_text, value_text):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                      spacing=style.DEFAULT_SPACING)
        label = Gtk.Label(label=label_text)
        label.set_halign(Gtk.Align.END)
        style.apply_css_to_widget(
            label, 'color: %s;' % style.COLOR_SELECTION_GREY.get_html())
        box.append(label)
        self._group.add_widget(label)
        value = Gtk.Label(label=str(value_text), xalign=0)
        value.set_halign(Gtk.Align.START)
        value.set_selectable(True)
        value.set_wrap(True)
        value.set_hexpand(True)
        box.append(value)
        return box

    def _section_title(self, title):
        self._vbox.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        label = Gtk.Label(label=title, xalign=0)
        label.add_css_class('heading')
        self._vbox.append(label)

    def _setup_identity(self):
        self._section_title(_('Identity'))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                      spacing=style.DEFAULT_SPACING)
        box.set_margin_top(style.DEFAULT_SPACING * 2)
        box.set_margin_bottom(style.DEFAULT_SPACING * 2)
        box.set_margin_start(style.DEFAULT_SPACING * 2)
        box.set_margin_end(style.DEFAULT_SPACING * 2)
        model = self._model.get_hardware_model()
        if model:
            box.append(self.create_information_box(_('Model:'), model))
        box.append(self.create_information_box(
            _('Serial Number:'), self._model.get_serial_number()))
        self._vbox.append(box)

    def _setup_system(self):
        self._section_title(_('System'))
        self._system_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                   spacing=style.DEFAULT_SPACING)
        self._system_box.set_margin_top(style.DEFAULT_SPACING * 2)
        self._system_box.set_margin_bottom(style.DEFAULT_SPACING * 2)
        self._system_box.set_margin_start(style.DEFAULT_SPACING * 2)
        self._system_box.set_margin_end(style.DEFAULT_SPACING * 2)
        self._vbox.append(self._system_box)
        self._refresh_system()

    def _refresh_system(self):
        while (child := self._system_box.get_first_child()) is not None:
            self._system_box.remove(child)
        self._system_box.append(self.create_information_box(
            _('Status:'), _('Read-only local inventory')))
        for label, value in self._model.get_system_information():
            self._system_box.append(self.create_information_box(label, value))
        refresh = Gtk.Button(label=_('Refresh inventory'))
        refresh.set_halign(Gtk.Align.START)
        refresh.set_tooltip_text(_('Read the local system sources again.'))
        refresh.update_property(
            [Gtk.AccessibleProperty.LABEL,
             Gtk.AccessibleProperty.DESCRIPTION],
            [refresh.get_label(), refresh.get_tooltip_text()])
        refresh.connect('clicked', self._refresh_clicked)
        self._system_box.append(refresh)

    def _refresh_clicked(self, _button):
        self._refresh_system()

    def _setup_software(self):
        self._section_title(_('Software'))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                      spacing=style.DEFAULT_SPACING)
        box.set_margin_top(style.DEFAULT_SPACING * 2)
        box.set_margin_bottom(style.DEFAULT_SPACING * 2)
        box.set_margin_start(style.DEFAULT_SPACING * 2)
        box.set_margin_end(style.DEFAULT_SPACING * 2)
        box.append(self.create_information_box(
            _('Build:'), self._model.get_build_number()))
        box.append(self.create_information_box(_('Sugar:'), config.version))
        box.append(self.create_information_box(
            _('Firmware:'), self._model.get_firmware_number()))
        box.append(self.create_information_box(
            _('Wireless Firmware:'), self._model.get_wireless_firmware()))
        self._vbox.append(box)

    def _setup_copyright(self):
        self._section_title(_('Copyright and License'))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                      spacing=style.DEFAULT_SPACING)
        box.set_margin_top(style.DEFAULT_SPACING * 2)
        box.set_margin_bottom(style.DEFAULT_SPACING * 2)
        box.set_margin_start(style.DEFAULT_SPACING * 2)
        box.set_margin_end(style.DEFAULT_SPACING * 2)
        copyright_text = ('© 2006-2020 One Laptop per Child Association Inc, '
                          'Sugar Labs Inc, Red Hat Inc, Collabora Ltd and '
                          'Contributors.')
        box.append(Gtk.Label(label=copyright_text, xalign=0,
                             wrap=True, max_width_chars=80))
        box.append(Gtk.Label(
            label=_('Sugar is the graphical user interface that you are '
                    'looking at. Sugar is free software, covered by the '
                    'GNU General Public License.'),
            xalign=0, wrap=True, max_width_chars=80))
        expander = Gtk.Expander(label=_('Full license:'))
        expander.connect('notify::expanded', self.license_expander_cb)
        box.append(expander)
        for license_text in self._model.get_secondary_licenses():
            box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
            box.append(Gtk.Label(label=license_text, xalign=0,
                                 wrap=True, max_width_chars=80))
        box.set_vexpand(True)
        self._vbox.append(box)

    def license_expander_cb(self, expander, _param_spec):
        if expander.get_expanded():
            view = Gtk.TextView()
            view.set_editable(False)
            view.set_wrap_mode(Gtk.WrapMode.WORD)
            view.get_buffer().set_text(self._model.get_license())
            view.add_css_class('monospace')
            expander.set_child(view)
        else:
            expander.set_child(None)

    def setup(self):
        self._refresh_system()

    def apply(self):
        return None

    def undo(self):
        self.setup()
