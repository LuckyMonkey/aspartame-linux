"""GStreamer playback for Jukebox, without GTK.

GTK's own Gtk.MediaFile needs GTK's media module, which Arch's gtk4 does
not ship, so Jukebox drives ``playbin`` directly. Video frames arrive on an
appsink as RGBA and are handed to ``on_frame(width, height, stride, bytes)``
on the main loop, where the Activity turns them into textures.
"""

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst  # noqa: E402

Gst.init(None)

VIDEO_SINK = ("videoconvert ! videoscale ! video/x-raw,format=RGBA,pixel-aspect-ratio=1/1 ! "
              "appsink name=frames emit-signals=true max-buffers=1 drop=true sync=true")


class Player:
    def __init__(self, on_frame=None, on_state=None, on_ended=None, on_error=None,
                 audio_sink=None):
        self.on_frame = on_frame or (lambda *a: None)
        self.on_state = on_state or (lambda playing: None)
        self.on_ended = on_ended or (lambda: None)
        self.on_error = on_error or (lambda message: None)
        self.has_video = False
        self.playing = False
        self.pipeline = Gst.ElementFactory.make("playbin", None)
        if self.pipeline is None:
            raise RuntimeError("GStreamer playbin is not installed")
        video = Gst.parse_bin_from_description(VIDEO_SINK, True)
        video.get_by_name("frames").connect("new-sample", self._sample)
        self.pipeline.set_property("video-sink", video)
        if audio_sink:
            self.pipeline.set_property("audio-sink", Gst.ElementFactory.make(audio_sink, None))
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        self._watch = bus.connect("message", self._message)

    def open(self, uri):
        self.pipeline.set_state(Gst.State.NULL)
        self.has_video = False
        self.pipeline.set_property("uri", uri)

    def play(self):
        if self.pipeline.set_state(Gst.State.PLAYING) == Gst.StateChangeReturn.FAILURE:
            self.on_error("cannot start playback")

    def pause(self):
        self.pipeline.set_state(Gst.State.PAUSED)

    def close(self):
        """Stop and release the pipeline; the Player cannot be reused."""
        bus = self.pipeline.get_bus()
        bus.disconnect(self._watch)
        bus.remove_signal_watch()
        self.pipeline.set_state(Gst.State.NULL)
        self.playing = False

    def position(self):
        ok, value = self.pipeline.query_position(Gst.Format.TIME)
        return value if ok else 0

    def duration(self):
        ok, value = self.pipeline.query_duration(Gst.Format.TIME)
        return value if ok and value > 0 else 0

    def seek(self, nanoseconds):
        self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                                  max(0, int(nanoseconds)))

    def _sample(self, sink):
        # Streaming thread: copy the frame, then hand it to the main loop.
        sample = sink.emit("pull-sample")
        if sample is None:
            return Gst.FlowReturn.OK
        structure = sample.get_caps().get_structure(0)
        width, height = structure.get_value("width"), structure.get_value("height")
        buffer = sample.get_buffer()
        ok, info = buffer.map(Gst.MapFlags.READ)
        if ok:
            data = bytes(info.data)
            buffer.unmap(info)
            stride = len(data) // height if height else 0
            self.has_video = True
            GLib.idle_add(self.on_frame, width, height, stride, data)
        return Gst.FlowReturn.OK

    def _message(self, _bus, message):
        if message.type == Gst.MessageType.EOS:
            self.playing = False
            self.on_state(False)
            self.on_ended()
        elif message.type == Gst.MessageType.ERROR:
            error, _debug = message.parse_error()
            self.playing = False
            self.on_state(False)
            self.on_error(error.message)
        elif message.type == Gst.MessageType.STATE_CHANGED and message.src == self.pipeline:
            _old, new, _pending = message.parse_state_changed()
            playing = new == Gst.State.PLAYING
            if playing != self.playing:
                self.playing = playing
                self.on_state(playing)
