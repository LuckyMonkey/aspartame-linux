"""Native GTK4 Portfolio Activity.

A port of GTK3 Portfolio (sugarlabs/portfolio-activity): a slide show of
the Journal entries the learner starred. Each slide shows the entry's
picture (or Journal preview), title and description; edits to the title
and description are written back to that Journal entry, as in GTK3. The
show has first/previous/next/last, autoplay at the GTK3 speeds, a
thumbnail view with reordering, unstarring, refresh, fullscreen and
Save as PDF (a new Journal object).

The Portfolio's own Journal object keeps the cover (title, introduction)
and the show settings; see :mod:`portfolio_model`.
"""

import json
import tempfile
from pathlib import Path

from gi.repository import Gdk, GLib, Gtk, Pango
from sugar4.activity import SimpleActivity

from portfolio_model import INTERVALS, Show, Slide

INTERVAL_NAMES = ("2 seconds", "10 seconds", "30 seconds", "1 minute")


class Journal:
    """The Journal, through the sugar4 datastore."""

    def starred(self):
        from sugar4.datastore import datastore
        entries, _count = datastore.find({"keep": "1"}, sorting=["+timestamp"],
                                         properties=["uid", "title", "description",
                                                     "mime_type", "preview", "activity"])
        slides = []
        for entry in entries:
            meta = entry.get_metadata()
            if meta.get("activity") == "org.sugarlabs.PortfolioActivity":
                entry.destroy()
                continue   # a Portfolio is not a slide of itself
            preview = meta.get("preview") or b""
            slides.append(Slide(entry.object_id, str(meta.get("title") or ""),
                                str(meta.get("description") or ""), str(meta.get("mime_type") or ""),
                                bytes(preview) if not isinstance(preview, str) else b""))
            entry.destroy()
        return slides

    def picture(self, slide):
        """Image bytes for a slide: the file of an image entry, else its preview."""
        if slide.mime_type.startswith("image/"):
            from sugar4.datastore import datastore
            entry = datastore.get(slide.uid)
            try:
                return Path(entry.get_file_path()).read_bytes()
            except (OSError, TypeError):
                pass
            finally:
                entry.destroy()
        return slide.preview

    def update(self, slide):
        from sugar4.datastore import datastore
        entry = datastore.get(slide.uid)
        entry.metadata["title"] = slide.title
        entry.metadata["description"] = slide.description
        datastore.write(entry, update_mtime=False)
        entry.destroy()

    def unstar(self, uid):
        from sugar4.datastore import datastore
        entry = datastore.get(uid)
        entry.metadata["keep"] = "0"
        datastore.write(entry, update_mtime=False)
        entry.destroy()

    def export(self, title, mime_type, path):
        from sugar4.datastore import datastore
        entry = datastore.create()
        entry.metadata["title"] = title
        entry.metadata["mime_type"] = mime_type
        entry.file_path = str(path)
        datastore.write(entry, transfer_ownership=True)
        entry.destroy()


def texture(data):
    try:
        return Gdk.Texture.new_from_bytes(GLib.Bytes.new(data)) if data else None
    except GLib.Error:
        return None


class PortfolioActivity(SimpleActivity):
    def __init__(self, activity_handle=None, journal=None):
        super().__init__(activity_handle)
        self.set_title("Portfolio")
        self.journal = journal or Journal()
        self.show = Show()
        self._autoplay = 0
        self._showing = False
        self._build()
        GLib.idle_add(self._initial_scan)

    # Layout

    def _button(self, label, tip, handler, *args, name=None):
        button = Gtk.Button(label=label)
        button.set_tooltip_text(tip)
        button.update_property([Gtk.AccessibleProperty.LABEL], [name or label])
        button.connect("clicked", handler, *args)
        return button

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(16); root.set_margin_bottom(16)
        root.set_margin_start(24); root.set_margin_end(24)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Portfolio"])

        header = Gtk.Box(spacing=8)
        title = Gtk.Label(label="Portfolio", xalign=0, hexpand=True)
        title.add_css_class("title-1")
        header.append(title)
        self.views = Gtk.Stack()
        header.append(Gtk.StackSwitcher(stack=self.views))
        self.autoplay = Gtk.ToggleButton(label="Autoplay")
        self.autoplay.set_tooltip_text("Advance the slides automatically")
        self.autoplay.connect("toggled", self._autoplay_toggled)
        header.append(self.autoplay)
        self.speed = Gtk.DropDown.new_from_strings(list(INTERVAL_NAMES))
        self.speed.set_selected(INTERVALS.index(self.show.interval))
        self.speed.update_property([Gtk.AccessibleProperty.LABEL], ["Autoplay speed"])
        self.speed.connect("notify::selected", self._speed_changed)
        header.append(self.speed)
        header.append(self._button("Refresh", "Look for newly starred Journal entries", self._refresh_cb))
        header.append(self._button("Fullscreen", "Fill the screen with the slides (Escape leaves)",
                                   self._fullscreen))
        header.append(self._button("Save as PDF", "Save the portfolio as a PDF in the Journal",
                                   self._save_pdf))
        root.append(header)

        self.views.add_titled(self._slide_page(), "slides", "Slides")
        self.views.add_titled(self._thumb_page(), "thumbs", "Thumbnails")
        self.views.set_vexpand(True)
        self.views.connect("notify::visible-child-name", self._view_changed)
        root.append(self.views)

        self.status = Gtk.Label(xalign=0, wrap=True)
        self.status.add_css_class("dim-label")
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Portfolio status"])
        root.append(self.status)
        self.set_canvas(root)

        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self._key)
        self.add_controller(keys)
        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"button { min-height: 38px; border-radius: 18px; } entry { min-height: 40px; }"
            b" picture.slide { background: #eef3f5; border-radius: 10px; }"
            b" label.empty { font-size: 18px; } frame.slide-text { border: 1px solid #8aa8b8;"
            b" border-radius: 10px; padding: 6px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _slide_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.picture = Gtk.Picture(can_shrink=True, content_fit=Gtk.ContentFit.CONTAIN, vexpand=True)
        self.picture.add_css_class("slide")
        self.picture.update_property([Gtk.AccessibleProperty.LABEL], ["Slide picture"])
        self.empty = Gtk.Label(
            label="Do you have any items in your Journal starred?\n"
                  "Star entries in the Journal, then press Refresh.",
            justify=Gtk.Justification.CENTER, wrap=True, vexpand=True)
        self.empty.add_css_class("empty")
        page.append(self.empty)
        page.append(self.picture)
        self.slide_title = Gtk.Entry(placeholder_text="Slide title")
        self.slide_title.update_property([Gtk.AccessibleProperty.LABEL], ["Slide title"])
        self.slide_title.connect("changed", self._title_edited)
        page.append(self.slide_title)
        self.description = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD_CHAR)
        self.description.update_property([Gtk.AccessibleProperty.LABEL], ["Slide description"])
        self.description.get_buffer().connect("changed", self._description_edited)
        scroll = Gtk.ScrolledWindow(min_content_height=90)
        scroll.set_child(self.description)
        frame = Gtk.Frame(label="This project is about…")
        frame.add_css_class("slide-text")
        frame.set_child(scroll)
        page.append(frame)

        nav = Gtk.Box(spacing=8, halign=Gtk.Align.CENTER)
        self.first_button = self._button("First", "Show the first slide", self._go, 0)
        self.prev_button = self._button("Previous", "Show the previous slide", self._step, -1)
        self.counter = Gtk.Label(label="No slides")
        self.counter.update_property([Gtk.AccessibleProperty.LABEL], ["Slide number"])
        self.next_button = self._button("Next", "Show the next slide", self._step, 1)
        self.last_button = self._button("Last", "Show the last slide", self._go, -1)
        self.star = self._button("Unstar", "Remove this entry from the portfolio", self._unstar,
                                 name="Unstar this slide")
        for widget in (self.first_button, self.prev_button, self.counter, self.next_button,
                       self.last_button, self.star):
            nav.append(widget)
        page.append(nav)
        return page

    def _thumb_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        cover = Gtk.Box(spacing=8)
        self.cover_title = Gtk.Entry(placeholder_text="Portfolio title", hexpand=True)
        self.cover_title.update_property([Gtk.AccessibleProperty.LABEL], ["Portfolio title"])
        cover.append(self.cover_title)
        cover.append(self._button("Move earlier", "Move the current slide earlier", self._move, -1))
        cover.append(self._button("Move later", "Move the current slide later", self._move, 1))
        page.append(cover)
        self.introduction = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD_CHAR)
        self.introduction.update_property([Gtk.AccessibleProperty.LABEL], ["Portfolio introduction"])
        scroll = Gtk.ScrolledWindow(min_content_height=70)
        scroll.set_child(self.introduction)
        frame = Gtk.Frame(label="Introduction (the PDF cover page)")
        frame.add_css_class("slide-text")
        frame.set_child(scroll)
        page.append(frame)
        self.thumbs = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE, max_children_per_line=6,
                                  homogeneous=True, row_spacing=8, column_spacing=8)
        self.thumbs.update_property([Gtk.AccessibleProperty.LABEL], ["Slides"])
        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(self.thumbs)
        page.append(scroll)
        return page

    # Showing slides

    def _initial_scan(self):
        self._scan()
        return False

    def _scan(self):
        try:
            slides = self.journal.starred()
        except Exception as error:
            self.status.set_text("Cannot read the Journal: %s" % error)
            slides = []
        self.show.load_starred(slides)
        self._render()
        self._render_thumbs()
        count = len(self.show.slides)
        self.status.set_text("%d starred %s" % (count, "entry" if count == 1 else "entries"))

    def _render(self):
        slide = self.show.slide
        has = slide is not None
        self.empty.set_visible(not has)
        self.picture.set_visible(has)
        for widget in (self.slide_title, self.description, self.star):
            widget.set_sensitive(has)
        n, i = len(self.show.slides), self.show.current
        self.first_button.set_sensitive(has and i > 0)
        self.prev_button.set_sensitive(has and i > 0)
        self.next_button.set_sensitive(has and i < n - 1)
        self.last_button.set_sensitive(has and i < n - 1)
        self.counter.set_text("Slide %d of %d" % (i + 1, n) if has else "No slides")
        self._showing = True
        try:
            self.slide_title.set_text(slide.title if has else "")
            self.description.get_buffer().set_text(slide.description if has else "")
        finally:
            self._showing = False
        if has:
            try:
                data = self.journal.picture(slide)
            except Exception:
                data = slide.preview
            self.picture.set_paintable(texture(data))
            self.picture.update_property([Gtk.AccessibleProperty.DESCRIPTION],
                                         ["Picture for %s" % (slide.title or "untitled")])

    def _render_thumbs(self):
        self.thumbs.remove_all()
        for index, slide in enumerate(self.show.slides):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            picture = Gtk.Picture(paintable=texture(slide.preview), can_shrink=True,
                                  content_fit=Gtk.ContentFit.CONTAIN)
            picture.set_size_request(150, 110)
            box.append(picture)
            box.append(Gtk.Label(label=slide.title or "Untitled", ellipsize=Pango.EllipsizeMode.END,
                                     max_width_chars=18))
            button = Gtk.Button(child=box)
            button.set_tooltip_text("Show this slide")
            button.update_property([Gtk.AccessibleProperty.LABEL],
                                   ["Slide %d: %s" % (index + 1, slide.title or "Untitled")])
            button.connect("clicked", self._thumb_clicked, index)
            if index == self.show.current:
                button.add_css_class("suggested-action")
            self.thumbs.append(button)

    def _thumb_clicked(self, _button, index):
        self.show.go(index)
        self.views.set_visible_child_name("slides")
        self._render()

    def _view_changed(self, stack, _pspec):
        if stack.get_visible_child_name() == "thumbs":
            self._render_thumbs()

    def _go(self, _button, index):
        self.show.go(index if index >= 0 else len(self.show.slides) - 1)
        self._render()

    def _step(self, _button, direction):
        if self.show.step(direction):
            self._render()

    def _move(self, _button, step):
        if self.show.move(step):
            self._render_thumbs()
            self._render()
            self.status.set_text("Moved to position %d" % (self.show.current + 1))

    def _key(self, _controller, keyval, _keycode, _state):
        if keyval == Gdk.KEY_Escape and self.is_fullscreen():
            self.unfullscreen()
            return True
        focus = self.get_focus()
        if isinstance(focus, (Gtk.Text, Gtk.TextView)):
            return False   # arrows edit text
        if keyval in (Gdk.KEY_Right, Gdk.KEY_Page_Down):
            self._step(None, 1)
            return True
        if keyval in (Gdk.KEY_Left, Gdk.KEY_Page_Up):
            self._step(None, -1)
            return True
        return False

    def _fullscreen(self, _button):
        self.fullscreen()

    # Editing

    def _title_edited(self, entry):
        if not self._showing:
            self.show.edit(title=entry.get_text())

    def _description_edited(self, buffer):
        if not self._showing:
            self.show.edit(description=buffer.get_text(*buffer.get_bounds(), False))

    def _flush_edits(self):
        """Write edited titles/descriptions back to their Journal entries."""
        failed = 0
        for slide in self.show.dirty():
            try:
                self.journal.update(slide)
                slide.dirty = False
            except Exception:
                failed += 1
        return failed

    def _unstar(self, _button):
        slide = self.show.slide
        if slide is None:
            return
        try:
            self.journal.unstar(slide.uid)
        except Exception as error:
            self.status.set_text("Cannot unstar: %s" % error)
            return
        self.show.remove(slide.uid)
        self._render()
        self._render_thumbs()
        self.status.set_text("Removed %s from the portfolio" % (slide.title or "the slide"))

    def _refresh_cb(self, _button):
        self._flush_edits()
        self._scan()

    # Autoplay

    def _autoplay_toggled(self, button):
        if self._autoplay:
            GLib.source_remove(self._autoplay)
            self._autoplay = 0
        if button.get_active():
            self._autoplay = GLib.timeout_add_seconds(self.show.interval, self._advance)
            self.status.set_text("Autoplay every %s" % INTERVAL_NAMES[INTERVALS.index(self.show.interval)])
        else:
            self.status.set_text("Autoplay stopped")

    def _advance(self):
        if self.show.step(1, wrap=True):
            self._render()
        return True

    def _speed_changed(self, dropdown, _pspec):
        self.show.interval = INTERVALS[dropdown.get_selected()]
        if self.autoplay.get_active():
            self._autoplay_toggled(self.autoplay)

    # PDF

    def _cover(self):
        buffer = self.introduction.get_buffer()
        self.show.title = self.cover_title.get_text()
        self.show.introduction = buffer.get_text(*buffer.get_bounds(), False)

    def _save_pdf(self, _button):
        from portfolio_export import write_pdf
        self._cover()
        if not self.show.slides:
            self.status.set_text("Star some Journal entries first")
            return
        pictures = {}
        for slide in self.show.slides:
            try:
                pictures[slide.uid] = self.journal.picture(slide)
            except Exception:
                pictures[slide.uid] = slide.preview
        path = Path(tempfile.mkstemp(prefix="portfolio-", suffix=".pdf")[1])
        title = self.show.title or "Portfolio"
        try:
            pages = write_pdf(path, title, self.show.introduction, self.show.slides, pictures)
            self.journal.export("%s (PDF)" % title, "application/pdf", path)
        except Exception as error:
            path.unlink(missing_ok=True)
            self.status.set_text("Save as PDF failed: %s" % error)
            return
        self.status.set_text("Saved %s (PDF), %d pages, to the Journal" % (title, pages))

    # Journal

    def read_file(self, file_path):
        """Restore the cover and show settings; anything else raises."""
        show = Show.from_payload(json.loads(Path(file_path).read_text(encoding="utf-8")))
        self.show = show
        self.cover_title.set_text(show.title)
        self.introduction.get_buffer().set_text(show.introduction)
        self.speed.set_selected(INTERVALS.index(show.interval))
        self._scan()

    def write_file(self, file_path):
        """Save the cover and settings, and slide edits to their entries."""
        self._cover()
        self._flush_edits()
        Path(file_path).write_text(json.dumps(self.show.to_payload(), sort_keys=True) + "\n",
                                   encoding="utf-8")

    def can_close(self):
        if self._autoplay:
            GLib.source_remove(self._autoplay)
            self._autoplay = 0
        return super().can_close()
