from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Optional, List, FrozenSet
import random


Suit = Literal["SPADE", "HEART", "DIAMOND", "CLUB"]
FaceTag = Literal["GLASS", "HOT", "JUICED", "TAB"]


@dataclass(slots=True)
class RuleContext:
    """
    Active rules for this pot.
    """
    short_deck: bool = False
    low_ceiling: bool = False
    comped_ruin: bool = False


@dataclass(slots=True)
class Face:
    """
    A single side on a die.
    """
    base_value: int
    suit: Optional[Suit] = None
    is_royal: bool = False
    is_wild: bool = False
    base_tags: FrozenSet[FaceTag] = field(default_factory=frozenset)
    dead: bool = False

    def pattern_value(self, ctx: RuleContext) -> int:
        """
        Value used for hand detection.
        """
        v = self.base_value

        if ctx.short_deck and v > 4:
            v = 4
        if ctx.low_ceiling and v > 10:
            v = 10

        return v

    def sum_value(self, ctx: RuleContext) -> int:
        """
        Value used in the scoring sum for Heat.
        """
        if self.dead:
            return 0

        v = self.pattern_value(ctx)

        if ctx.comped_ruin and self.base_tags:
            return 0

        return v

    def effective_tags(self, ctx: RuleContext) -> FrozenSet[FaceTag]:
        """
        Tags that are "effective" for the current pot. Effective tags are determined
        by the current pots/floors rules, which are listed in RuleContext.
        """
        if self.dead:
            return frozenset()

        if ctx.comped_ruin and self.base_tags:
            return frozenset()

        return self.base_tags

    def is_royal_for_hand(self, ctx: RuleContext) -> bool:
        """
        Whether the face counts as a Royal (J/Q/K/Wild) for hand classification.
        """
        if ctx.low_ceiling:
            return False
        if ctx.comped_ruin and self.base_tags:
            return False
        return self.is_royal or self.is_wild

    def to_dict(self):
        return {
            "base_value": self.base_value,
            "suit": self.suit,
            "is_royal": self.is_royal,
            "is_wild": self.is_wild,
            "base_tags": list(self.base_tags),
            "dead": self.dead,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            base_value=data["base_value"],
            suit=data.get("suit"),
            is_royal=data.get("is_royal", False),
            is_wild=data.get("is_wild", False),
            base_tags=frozenset(data.get("base_tags", [])),
            dead=data.get("dead", False),
        )


@dataclass(slots=True)
class Die:
    faces: List[Face]

    @property
    def sides(self) -> int:
        return len(self.faces)

    def roll_index(self, rng: Optional[random.Random] = None) -> int:
        if rng is None:
            rng = random
        return rng.randrange(self.sides)

    # serializes the faces of the die, for persistence
    def to_dict(self) -> dict:
        return {"faces": [f.to_dict() for f in self.faces]}

    @classmethod
    def from_dict(cls, data: dict) -> "Die":
        return cls(faces=[Face.from_dict(fd) for fd in data["faces"]])


@dataclass(slots=True)
class DieState:
    die: Die
    current_index: int
    locked: bool = False

    @classmethod
    def from_die(cls, die: Die, rng: Optional[random.Random] = None) -> "DieState":
        idx = die.roll_index(rng)
        return cls(die=die, current_index=idx, locked=False)

    def roll(self, rng: Optional[random.Random] = None) -> None:
        if self.locked:
            return
        self.current_index = self.die.roll_index(rng)

    @property
    def current_face(self) -> Face:
        return self.die.faces[self.current_index]

    @classmethod
    def from_dict(cls, data: dict):
        """
        loads the serialized die state.
        dictionary contains info about the die, it's current top face, 
        and whether it is locked or not

        retrns a DieState
        """
        return cls(
            die=Die.from_dict(data["die"]),
            current_index=data["current_index"],
            locked=data.get("locked", False),
        )

    def to_dict(self):
        # TODO FIX YOUR DAMN LSP
        # BASEDPYRIGHT IS WAY TOO STRICT, EVEN ON LAXED TYPE CHECKING
        return {
            "die": self.die.to_dict(),
            "current_index": self.current_index,
            "locked": self.locked,
        }


def make_plain_d6() -> Die:
    """
    constructs a plain d6 with numeric values 1..6 and simple suits
    for now just cycle suits SPADE/HEART/DIAMOND/CLUB.

    TODO:
        - implement d6, d12, d20
        - dice shouldnt start with any suits
        - suits are added with "loaded face" angles
    """
    suit_cycle: list[Suit] = ["SPADE", "HEART", "DIAMOND", "CLUB"]
    faces: list[Face] = []
    for i, v in enumerate(range(1, 7)):
        suit = suit_cycle[i % len(suit_cycle)]
        faces.append(Face(base_value=v, suit=suit))
    return Die(faces=faces)

