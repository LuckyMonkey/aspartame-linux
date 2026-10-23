"""Portfolio slides and the Activity's own payload, independent of GTK.

As in GTK3 Portfolio (sugarlabs/portfolio-activity), the slides are the
Journal entries the learner starred (``keep`` = "1"). Slide titles and
descriptions live in those entries' metadata. The Portfolio object itself
keeps only the cover and the show settings::

    {"format": "aspartame-portfolio-v2", "title", "introduction",
     "order": [object ids], "current": int, "interval": seconds}
"""

from dataclasses import dataclass, field

FORMAT = "aspartame-portfolio-v2"
INTERVALS = (2, 10, 30, 60)      # GTK3: 2 seconds, 10 seconds, 30 seconds, 1 minute


@dataclass
class Slide:
    uid: str
    title: str = ""
    description: str = ""
    mime_type: str = ""
    preview: bytes = b""          # Journal preview PNG
    dirty: bool = field(default=False, compare=False)


class Show:
    def __init__(self):
        self.title = ""
        self.introduction = ""
        self.slides = []
        self.order = []           # remembered order, applied on each scan
        self.current = 0
        self.interval = 10

    def load_starred(self, slides):
        """Replace the slides with a fresh Journal scan, keeping our order."""
        known = {s.uid: s for s in self.slides}
        fresh = []
        for slide in slides:
            old = known.get(slide.uid)
            if old is not None and old.dirty:
                # Unsaved edits win over the Journal copy.
                slide.title, slide.description, slide.dirty = old.title, old.description, True
            fresh.append(slide)
        rank = {uid: i for i, uid in enumerate(self.order)}
        fresh.sort(key=lambda s: rank.get(s.uid, len(rank)))
        current_uid = self.slide.uid if self.slide else None
        self.slides = fresh
        self.order = [s.uid for s in fresh]
        uids = [s.uid for s in fresh]
        self.current = uids.index(current_uid) if current_uid in uids else min(self.current, max(0, len(fresh) - 1))

    @property
    def slide(self):
        return self.slides[self.current] if 0 <= self.current < len(self.slides) else None

    def go(self, index):
        if self.slides:
            self.current = max(0, min(len(self.slides) - 1, index))

    def step(self, direction, wrap=False):
        if not self.slides:
            return False
        target = self.current + direction
        if wrap:
            target %= len(self.slides)
        if not 0 <= target < len(self.slides):
            return False
        self.current = target
        return True

    def move(self, step):
        """Move the current slide earlier or later in the show."""
        target = self.current + step
        if not (self.slide and 0 <= target < len(self.slides)):
            return False
        self.slides[self.current], self.slides[target] = self.slides[target], self.slides[self.current]
        self.current = target
        self.order = [s.uid for s in self.slides]
        return True

    def remove(self, uid):
        self.slides = [s for s in self.slides if s.uid != uid]
        self.order = [s.uid for s in self.slides]
        self.current = min(self.current, max(0, len(self.slides) - 1))

    def edit(self, title=None, description=None):
        slide = self.slide
        if slide is None:
            return
        if title is not None and title != slide.title:
            slide.title, slide.dirty = title, True
        if description is not None and description != slide.description:
            slide.description, slide.dirty = description, True

    def dirty(self):
        return [s for s in self.slides if s.dirty]

    def to_payload(self):
        return {"format": FORMAT, "title": self.title, "introduction": self.introduction,
                "order": [s.uid for s in self.slides] or self.order, "current": self.current,
                "interval": self.interval}

    @classmethod
    def from_payload(cls, payload):
        if not isinstance(payload, dict):
            raise ValueError("Portfolio payload must be an object")
        show = cls()
        if "format" not in payload and set(payload) <= {"title", "body"}:
            # GTK4 Portfolio 1 was a text editor; its text becomes the cover.
            if not all(isinstance(payload.get(k, ""), str) for k in ("title", "body")):
                raise ValueError("title and body must be text")
            show.title, show.introduction = payload.get("title", ""), payload.get("body", "")
            return show
        if payload.get("format") != FORMAT:
            raise ValueError("unsupported Portfolio format %r" % payload.get("format"))
        title, intro, order = payload.get("title", ""), payload.get("introduction", ""), payload.get("order", [])
        current, interval = payload.get("current", 0), payload.get("interval", 10)
        if not isinstance(title, str) or not isinstance(intro, str):
            raise ValueError("title and introduction must be text")
        if not isinstance(order, list) or not all(isinstance(u, str) for u in order):
            raise ValueError("order must list object ids")
        if isinstance(current, bool) or not isinstance(current, int) or current < 0:
            raise ValueError("current must be a slide index")
        if interval not in INTERVALS:
            raise ValueError("interval must be one of %s" % (INTERVALS,))
        show.title, show.introduction, show.order = title, intro, order
        show.current, show.interval = current, interval
        return show
