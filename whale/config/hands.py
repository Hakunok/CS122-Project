from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Literal

HandFamily = Literal["standard", "suit", "royal"]


@dataclass(frozen=True, slots=True)
class HandDef:
    id: str
    name: str
    family: HandFamily
    base_heat: int
    base_mult: float
    priority: int
    short_desc: str


HAND_DEFS: Dict[str, HandDef] = {
    "std_highcard": HandDef(
        id="std_highcard",
        name="High Card",
        family="standard",
        base_heat=5,
        base_mult=1.0,
        priority=1,
        short_desc="No pairs or better.",
    ),

    "std_pair": HandDef(
        id="std_pair",
        name="Pair",
        family="standard",
        base_heat=10,
        base_mult=2.0,
        priority=2,
        short_desc="Exactly one pair.",
    ),
    "std_2pair": HandDef(
        id="std_2pair",
        name="Two Pair",
        family="standard",
        base_heat=20,
        base_mult=2.0,
        priority=3,
        short_desc="Two different pairs.",
    ),
    "std_3kind": HandDef(
        id="std_3kind",
        name="Three of a Kind",
        family="standard",
        base_heat=30,
        base_mult=3.0,
        priority=4,
        short_desc="Three dice show the same value.",
    ),
    "std_straight": HandDef(
        id="std_straight",
        name="Straight",
        family="standard",
        base_heat=35,
        base_mult=4.0,
        priority=5,
        short_desc="Five consecutive values.",
    ),
    "std_fullhouse": HandDef(
        id="std_fullhouse",
        name="Full House",
        family="standard",
        base_heat=45,
        base_mult=4.5,
        priority=7,
        short_desc="Three of a kind plus a pair.",
    ),
    "std_4kind": HandDef(
        id="std_4kind",
        name="Four of a Kind",
        family="standard",
        base_heat=60,
        base_mult=7.0,
        priority=8,
        short_desc="Four dice show the same value.",
    ),
    "std_high_straight": HandDef(
        id="std_high_straight",
        name="High Straight",
        family="standard",
        base_heat=90,
        base_mult=6.5,
        priority=9,
        short_desc="A straight made entirely of high values.",
    ),
    "std_5kind": HandDef(
        id="std_5kind",
        name="Five of a Kind",
        family="standard",
        base_heat=120,
        base_mult=12.0,
        priority=10,
        short_desc="All five dice match.",
    ),

    "std_flush": HandDef(
        id="std_flush",
        name="Flush",
        family="suit",
        base_heat=40,
        base_mult=4.0,
        priority=6,
        short_desc="All dice share the same suit.",
    ),
    "std_straight_flush": HandDef(
        id="std_straight_flush",
        name="Straight Flush",
        family="suit",
        base_heat=100,
        base_mult=8.0,
        priority=11,
        short_desc="Straight and all dice share a suit.",
    ),
    "std_royal_flush": HandDef(
        id="std_royal_flush",
        name="Royal Flush",
        family="suit",
        base_heat=140,
        base_mult=12.0,
        priority=12,
        short_desc="9–10–J–Q–K all in one suit.",
    ),

    "royal_2pair": HandDef(
        id="royal_2pair",
        name="Royal Two Pair",
        family="royal",
        base_heat=50,
        base_mult=5.0,
        priority=13,
        short_desc="Two different pairs of Royals.",
    ),
    "royal_3kind": HandDef(
        id="royal_3kind",
        name="Royal Three of a Kind",
        family="royal",
        base_heat=75,
        base_mult=6.0,
        priority=14,
        short_desc="Three Royals of the same rank.",
    ),
    "royal_fullhouse": HandDef(
        id="royal_fullhouse",
        name="Royal Full House",
        family="royal",
        base_heat=105,
        base_mult=8.0,
        priority=15,
        short_desc="Three Royals of one rank plus a pair of another.",
    ),
    "royal_4kind": HandDef(
        id="royal_4kind",
        name="Royal Four of a Kind",
        family="royal",
        base_heat=150,
        base_mult=14.0,
        priority=16,
        short_desc="Four Royals of the same rank.",
    ),
    "royal_5kind": HandDef(
        id="royal_5kind",
        name="Royal Five of a Kind",
        family="royal",
        base_heat=200,
        base_mult=16.0,
        priority=17,
        short_desc="Five Royals of the same rank.",
    ),
}

