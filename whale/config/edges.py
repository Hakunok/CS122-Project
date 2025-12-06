from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class EdgeDef:
    id: str
    name: str
    description: str
    base_cost: int
    hand_id: str
    rarity: str


EDGES: Dict[str, EdgeDef] = {
    "muck": EdgeDef(
        id="muck",
        name="The Muck",
        description="TODO. High Card now grants +10 Heat and +0.5 Mult.",
        base_cost=20,
        hand_id="std_highcard",
        rarity="common",
    ),
    "rookies_tell": EdgeDef(
        id="rookies_tell",
        name="Rookie's Tell",
        description="TODO. Pair now grants +5 Heat and +0.5 Mult.",
        base_cost=25,
        hand_id="std_pair",
        rarity="common",
    ),
    "double_down": EdgeDef(
        id="double_down",
        name="Double Down",
        description="TODO. Two Pair now grants +5 Heat and +0.5 Mult.",
        base_cost=30,
        hand_id="std_2pair",
        rarity="common",
    ),
    "threes": EdgeDef(
        id="threes",
        name="Triplets",
        description="TODO. Three of a Kind now grants +5 Heat and +0.5 Mult.",
        base_cost=35,
        hand_id="std_3kind",
        rarity="uncommon",
    ),
    "barons_buff": EdgeDef(
        id="barons_buff",
        name="Royal Triplets",
        description="TODO. Royal Three of a Kind now grants +10 Heat and +0.5 Mult.",
        base_cost=85,
        hand_id="royal_3kind",
        rarity="rare",
    ),
    "running_numbers": EdgeDef(
        id="running_numbers",
        name="Running the Numbers",
        description="TODO. Straight now grants +10 Heat and +0.5 Mult.",
        base_cost=50,
        hand_id="std_straight",
        rarity="uncommon",
    ),
    "full_boat": EdgeDef(
        id="full_boat",
        name="Full Boat",
        description="TODO. Full House now grants +10 Heat and +0.5 Mult.",
        base_cost=50,
        hand_id="std_fullhouse",
        rarity="uncommon",
    ),
    "four_horsemen": EdgeDef(
        id="four_horsemen",
        name="Four Horsemen",
        description="TODO. Four of a Kind now grants +10 Heat and +0.5 Mult.",
        base_cost=60,
        hand_id="std_4kind",
        rarity="rare",
    ),
    "quints": EdgeDef(
        id="quints",
        name="Quints",
        description="TODO. Five of a Kind now grants +15 Heat and +1.0 Mult.",
        base_cost=75,
        hand_id="std_5kind",
        rarity="rare",
    ),
    "whales_gambit": EdgeDef(
        id="whales_gambit",
        name="Whale's Gambit",
        description="TODO. Royal Five of a Kind now grants +15 Heat and +1.0 Mult.",
        base_cost=80,
        hand_id="royal_5kind",
        rarity="rare",
    ),
}
