"""Small, presentation-independent state model for Aspartame Chirality.

The model deliberately knows nothing about GTK, X11, workspaces, windows, or
keyboard shortcuts.  It records only the two immediate working contexts and
which one is visible/active.  A caller owns the actual Activity lifecycle and
surface switching.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ChiralityError(ValueError):
    """Base class for invalid semantic hand operations."""


class HandOccupied(ChiralityError):
    """A hand already contains an Activity and replacement was not explicit."""


class NoFreeHand(ChiralityError):
    """Both immediate hands are occupied."""


class EmptyHand(ChiralityError):
    """An operation targeted a hand without an Activity."""


@dataclass(frozen=True)
class Space:
    """One selectable full-surface context.

    A Space is a semantic surface target, not a window, pane, Activity, or
    object container.  ``switch_target`` is the controller token consumed by
    the migration bridge; it is deliberately not geometry.
    """

    space_id: str
    label: str
    switch_target: str

    def __post_init__(self) -> None:
        if not self.space_id.strip() or not self.label.strip():
            raise ChiralityError("Space id and label must not be empty")
        if not self.switch_target.strip():
            raise ChiralityError("Space switch target must not be empty")


DEFAULT_SPACES = (
    Space("classic", "Classic Space", "gtk3"),
    Space("modern", "Modern Space", "gtk4"),
)


@dataclass
class Spaces:
    """Bounded single-surface Space selection, independent of Chirality hands.

    The selector stores only the current Space.  It has no split-screen
    geometry, Activity/object state, or previous-space history.
    """

    catalog: tuple[Space, ...] = DEFAULT_SPACES
    active_space: str = "classic"

    def __post_init__(self) -> None:
        ids = [space.space_id for space in self.catalog]
        if not ids or len(ids) != len(set(ids)):
            raise ChiralityError("Space catalog must contain unique entries")
        if self.active_space not in ids:
            raise ChiralityError("active Space is not in the catalog")

    def current(self) -> Space:
        for space in self.catalog:
            if space.space_id == self.active_space:
                return space
        raise ChiralityError("active Space is not in the catalog")

    def select(self, space_id: str) -> Space:
        """Select one complete Space and return its descriptor."""

        for space in self.catalog:
            if space.space_id == space_id:
                self.active_space = space_id
                return space
        raise ChiralityError(f"unknown Space: {space_id}")

    def accessible_state(self) -> dict[str, Any]:
        return {
            "active_space": self.active_space,
            "spaces": [
                {
                    "id": space.space_id,
                    "label": space.label,
                    "switch_target": space.switch_target,
                    "state": "active" if space.space_id == self.active_space else "available",
                }
                for space in self.catalog
            ],
        }

    def to_dict(self) -> dict[str, str]:
        """Serialize current selection only; never a previous-space log."""

        return {"active_space": self.active_space}


class Side(str, Enum):
    LEFT = "left"
    RIGHT = "right"

    @property
    def label(self) -> str:
        return "Left Hand" if self is Side.LEFT else "Right Hand"

    @property
    def other(self) -> "Side":
        return Side.RIGHT if self is Side.LEFT else Side.LEFT


@dataclass(frozen=True)
class Hand:
    """The current immediate context held by one semantic hand."""

    activity_id: str
    object_ref: str | None = None
    object_title: str | None = None

    def __post_init__(self) -> None:
        if not self.activity_id.strip():
            raise ChiralityError("activity_id must not be empty")


@dataclass
class ChiralSession:
    """At most two Activities, with one active visible context.

    There is intentionally no history, rewind stack, screen geometry, or
    window handle here.  Replacing a hand returns the released context to the
    caller, which may hand it back to Sugar/Journal for ordinary resumption.
    """

    left_hand: Hand | None = None
    right_hand: Hand | None = None
    active_hand: Side | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.active_hand is not None and self.get(self.active_hand) is None:
            raise ChiralityError("active hand must contain an Activity")
        activity_ids = [
            hand.activity_id
            for hand in (self.left_hand, self.right_hand)
            if hand is not None
        ]
        if len(activity_ids) != len(set(activity_ids)):
            raise ChiralityError("an Activity may occupy only one hand")

    def get(self, side: Side) -> Hand | None:
        return self.left_hand if side is Side.LEFT else self.right_hand

    def _set(self, side: Side, hand: Hand | None) -> None:
        if side is Side.LEFT:
            self.left_hand = hand
        else:
            self.right_hand = hand

    def assign(
        self,
        side: Side,
        hand: Hand,
        *,
        replace: bool = False,
    ) -> Hand | None:
        """Put ``hand`` in ``side`` and return any explicitly released hand."""

        current = self.get(side)
        if current is not None and not replace:
            raise HandOccupied(f"{side.label} is occupied")
        other = self.get(side.other)
        if other is not None and other.activity_id == hand.activity_id:
            raise ChiralityError("an Activity may occupy only one hand")
        released = current
        self._set(side, hand)
        if self.active_hand is None:
            self.active_hand = side
        self._validate()
        return released

    def assign_first_free(self, hand: Hand) -> Side:
        """Assign an Activity to the first empty hand, or reject a third one."""

        for side in (Side.LEFT, Side.RIGHT):
            if self.get(side) is None:
                self.assign(side, hand)
                return side
        raise NoFreeHand("both hands are occupied; choose a hand to replace")

    def activate(self, side: Side) -> None:
        """Select a hand directly; this is not a toggle operation."""

        if self.get(side) is None:
            raise EmptyHand(f"{side.label} is empty")
        self.active_hand = side
        self._validate()

    def release(self, side: Side) -> Hand:
        """Let go of a hand without destroying its Activity or object."""

        released = self.get(side)
        if released is None:
            raise EmptyHand(f"{side.label} is empty")
        self._set(side, None)
        if self.active_hand is side:
            other = side.other
            self.active_hand = other if self.get(other) is not None else None
        self._validate()
        return released

    def activity_exited(self, activity_id: str) -> Side | None:
        """Remove a crashed/exited Activity while preserving the other hand."""

        for side in (Side.LEFT, Side.RIGHT):
            hand = self.get(side)
            if hand is not None and hand.activity_id == activity_id:
                self.release(side)
                return side
        return None

    def resume_activity(self, side: Side, activity_id: str) -> None:
        """Attach a replacement Activity while retaining the held object."""

        current = self.get(side)
        if current is None:
            raise EmptyHand(f"{side.label} is empty")
        other = self.get(side.other)
        if other is not None and other.activity_id == activity_id:
            raise ChiralityError("an Activity may occupy only one hand")
        self._set(
            side,
            Hand(
                activity_id=activity_id,
                object_ref=current.object_ref,
                object_title=current.object_title,
            ),
        )
        self._validate()

    def handoff_object(self, source: Side, target: Side) -> None:
        """Copy the current object reference to the other Activity.

        This is intentionally only an object reference operation.  It does
        not invent a capability system or mutate Journal data.
        """

        source_hand = self.get(source)
        target_hand = self.get(target)
        if source_hand is None or target_hand is None:
            raise EmptyHand("both hands must contain Activities for handoff")
        self._set(
            target,
            Hand(
                activity_id=target_hand.activity_id,
                object_ref=source_hand.object_ref,
                object_title=source_hand.object_title,
            ),
        )
        self._validate()

    def accessible_state(self) -> dict[str, Any]:
        """Return semantic labels suitable for an accessibility adapter."""

        def describe(side: Side) -> dict[str, Any]:
            hand = self.get(side)
            return {
                "side": side.value,
                "label": side.label,
                "state": "active" if self.active_hand is side else "held",
                "activity_id": hand.activity_id if hand else None,
                "object_ref": hand.object_ref if hand else None,
                "object_title": hand.object_title if hand else None,
            }

        return {
            "active_hand": self.active_hand.value if self.active_hand else None,
            "hands": [describe(Side.LEFT), describe(Side.RIGHT)],
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize only current semantic state; never presentation history."""

        def encode(hand: Hand | None) -> dict[str, str | None] | None:
            if hand is None:
                return None
            return {
                "activity_id": hand.activity_id,
                "object_ref": hand.object_ref,
                "object_title": hand.object_title,
            }

        return {
            "left_hand": encode(self.left_hand),
            "right_hand": encode(self.right_hand),
            "active_hand": self.active_hand.value if self.active_hand else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChiralSession":
        def decode(value: Any) -> Hand | None:
            if value is None:
                return None
            if not isinstance(value, dict) or "activity_id" not in value:
                raise ChiralityError("invalid hand state")
            return Hand(
                activity_id=str(value["activity_id"]),
                object_ref=value.get("object_ref"),
                object_title=value.get("object_title"),
            )

        active = data.get("active_hand")
        return cls(
            left_hand=decode(data.get("left_hand")),
            right_hand=decode(data.get("right_hand")),
            active_hand=Side(active) if active else None,
        )
