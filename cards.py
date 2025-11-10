from __future__ import annotations
import random
from dataclasses import dataclass
from typing import List, Iterable, Dict, Tuple

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
RANK_TO_VALUE = {r:i+2 for i,r in enumerate(RANKS)}  # 2..14

# chips attached to each rank (tunable; not Balatro's values)
RANK_CHIPS = {
    "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9,
    "10":10, "J":10, "Q":10, "K":10, "A":11,
}

@dataclass(frozen=True, order=True)
class Card:
    rank: str
    suit: str
    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self, rng: random.Random | None = None, include_jokers: bool = False):
        self.rng = rng or random.Random()
        self.include_jokers = include_jokers
        self.reset()

    def reset(self) -> None:
        self.cards: List[Card] = [Card(r, s) for s in SUITS for r in RANKS]
        self.rng.shuffle(self.cards)

    def draw(self, n: int) -> List[Card]:
        out = []
        for _ in range(n):
            if not self.cards:
                self.reset()
            out.append(self.cards.pop())
        return out

def counts_by_rank(cards: Iterable[Card]) -> Dict[str,int]:
    c: Dict[str,int] = {}
    for card in cards:
        c[card.rank] = c.get(card.rank, 0) + 1
    return c

def is_flush(cards: Iterable[Card]) -> bool:
    suits = {c.suit for c in cards}
    return len(suits) == 1

def is_straight(cards: Iterable[Card]) -> bool:
    vals = sorted(RANK_TO_VALUE[c.rank] for c in cards)
    # Handle A-low straight
    if vals == [2,3,4,5,14]:
        return True
    for i in range(4):
        if vals[i+1] - vals[i] != 1:
            return False
    return True

def format_cards(cards: Iterable[Card]) -> str:
    return " ".join(str(c) for c in cards)
