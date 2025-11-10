from __future__ import annotations
import random
from dataclasses import dataclass
from typing import List, Tuple
from .jokers import roll_joker_choices, Joker

@dataclass
class ShopOffer:
    joker: Joker
    price: int

class Shop:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.offers: List[ShopOffer] = []

    def open(self) -> List[ShopOffer]:
        self.offers = [ShopOffer(j, j.cost) for j in roll_joker_choices(self.rng, k=3)]
        return self.offers

    def buy(self, idx: int, coins: int, inventory: List[Joker], limit: int = 5) -> Tuple[bool, int, str]:
        if idx < 0 or idx >= len(self.offers):
            return False, coins, "Invalid index."
        if len(inventory) >= limit:
            return False, coins, "Joker inventory full."
        offer = self.offers[idx]
        if coins < offer.price:
            return False, coins, "Not enough coins."
        inventory.append(offer.joker)
        coins -= offer.price
        return True, coins, f"Bought {offer.joker.name}."
