from __future__ import annotations
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict
from .cards import Card, counts_by_rank

class Joker:
    name: str = "Joker"
    cost: int = 3
    rarity: str = "common"

    def modify(self, played: List[Card], hand_name: str, context: Dict) -> Tuple[int,int]:
        return (0,0)

    def describe(self) -> str:
        return self.name

# Some simple, original effects (not copied from Balatro)
class LuckySeven(Joker):
    name = "Lucky Seven"
    cost = 3
    def modify(self, played, hand_name, context):
        return (10 if any(c.rank == "7" for c in played) else 0, 0)

class FlushFan(Joker):
    name = "Flush Fan"
    cost = 4
    def modify(self, played, hand_name, context):
        return (0, 2 if hand_name in ("Flush","StraightFlush") else 0)

class PairPal(Joker):
    name = "Pair Pal"
    cost = 3
    def modify(self, played, hand_name, context):
        return (15 if hand_name in ("Pair","Two Pair") else 0, 0)

class PerHeartChips(Joker):
    name = "Heartfelt"
    cost = 5
    def modify(self, played, hand_name, context):
        hearts = sum(1 for c in played if c.suit == "♥")
        return (3 * hearts, 0)

class VarietyShow(Joker):
    name = "Variety Show"
    cost = 5
    rarity = "uncommon"
    # +1 mult per distinct rank in played
    def modify(self, played, hand_name, context):
        ranks = {c.rank for c in played}
        return (0, len(ranks) // 2)  # gentler than 1:1

class BossHunter(Joker):
    name = "Boss Hunter"
    cost = 6
    rarity = "uncommon"
    def modify(self, played, hand_name, context):
        if context.get("blind_type") == "Boss":
            return (10, 2)
        return (0,0)

ALL_JOKERS = [LuckySeven, FlushFan, PairPal, PerHeartChips, VarietyShow, BossHunter]

def roll_joker_choices(rng: random.Random, k: int = 3):
    cls = rng.sample(ALL_JOKERS, k=min(k, len(ALL_JOKERS)))
    return [c() for c in cls]
