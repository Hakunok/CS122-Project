from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class AngleDef:
    id: str
    name: str
    description: str
    base_cost: int
    rarity: str


ANGLES: Dict[str, AngleDef] = {
    "rookie": AngleDef(
        id="rookie",
        name="Rookie",
        description="Gain +1 reroll each pot.",
        base_cost=20,
        rarity="common",
    ),
    "snake_eyes": AngleDef(
        id="snake_eyes",
        name="Snake Eyes",
        description="TODO. Each 1 in your scoring hand grants a +11 Additive Heat.",
        base_cost=25,
        rarity="common",
    ),
    "high_roller": AngleDef(
        id="high_roller",
        name="High Roller",
        description="TODO. Each value above 7 in your scoring hand grants +7 Additive Heat",
        base_cost=35,
        rarity="uncommon",
    ),
    "glass_knuckles": AngleDef(
        id="glass_knuckles",
        name="Glass Knuckles",
        description="TODO. Glass Faces gain +2.4 Base Mult and have a 1-in-3 chance of shattering.",
        base_cost=60,
        rarity="rare",
    ),
    "the_shill": AngleDef(
        id="the_shill",
        name="The Shill",
        description="TODO. Scoring a Pair grants +5 Chips.",
        base_cost=50,
        rarity="common",
    ),
    "the_shark": AngleDef(
        id="the_shark",
        name="The Shark",
        description="TODO. At the start of each Pot gain +0.1 Additive Mult for every 50 chips, up to a max of +0.5.",
        base_cost=100,
        rarity="rare"
    )
}
