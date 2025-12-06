from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Literal
import random

from config.angles import ANGLES, AngleDef
from config.edges import EDGES, EdgeDef

ItemKind = Literal["angle", "edge"]


@dataclass
class ShopItem:
    """
    One entry in the shop, either an Angle or an Edge.
    """
    kind: ItemKind
    id: str
    name: str
    description: str
    cost: int
    purchased: bool = False

    @property
    def is_angle(self) -> bool:
        return self.kind == "angle"

    @property
    def is_edge(self) -> bool:
        return self.kind == "edge"


@dataclass
class ShopState:
    """
    Shop inventory for a given floor.

    for now...
      - 2 angles
      - 1 edge
      - Stock 1 each per floor
    """
    floor: int
    items: List[ShopItem] = field(default_factory=list)


def roll_shop_for_floor(
    floor: int,
    rng: random.Random,
    angles_count: int = 2,
    edges_count: int = 1,
) -> ShopState:
    """
    Generate a new shop inventory for a floor.

    for now...
      - 2 random distinct angles
      - 1 random edge

    TODO
        - we need to implement item rarity
        - item cost based on dupes
        - also changing item chance based on other items
    """
    angle_defs: List[AngleDef] = list(ANGLES.values())
    edge_defs: List[EdgeDef] = list(EDGES.values())

    rng.shuffle(angle_defs)
    rng.shuffle(edge_defs)

    chosen_angles = angle_defs[:angles_count]
    chosen_edges = edge_defs[:edges_count]

    items: List[ShopItem] = []

    for a in chosen_angles:
        items.append(
            ShopItem(
                kind="angle",
                id=a.id,
                name=a.name,
                description=a.description,
                cost=a.base_cost,
            )
        )

    for e in chosen_edges:
        items.append(
            ShopItem(
                kind="edge",
                id=e.id,
                name=e.name,
                description=e.description,
                cost=e.base_cost,
            )
        )

    return ShopState(floor=floor, items=items)

