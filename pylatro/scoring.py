from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Iterable, Tuple
from .cards import Card, counts_by_rank, is_flush, is_straight, RANK_CHIPS

# Not Balatro's exact numbers; just vibes.
HAND_BASE = {
    "High Card":   (0, 1),
    "Pair":        (10, 1),
    "Two Pair":    (20, 2),
    "Three Kind":  (30, 2),
    "Straight":    (40, 3),
    "Flush":       (50, 3),
    "Full House":  (60, 4),
    "Four Kind":   (80, 5),
    "StraightFlush": (120, 6),
}

@dataclass
class ScoreBreakdown:
    hand_name: str
    base_chips: int
    base_mult: int
    card_chips: int
    bonus_chips: int
    bonus_mult: int
    total_chips: int
    total_mult: int
    total_score: int

def best_poker_hand(cards: List[Card]) -> str:
    c = counts_by_rank(cards).values()
    flush = is_flush(cards)
    straight = is_straight(cards)
    if flush and straight:
        return "StraightFlush"
    if 4 in c:
        return "Four Kind"
    if 3 in c and 2 in c:
        return "Full House"
    if flush:
        return "Flush"
    if straight:
        return "Straight"
    if 3 in c:
        return "Three Kind"
    if list(c).count(2) == 2:
        return "Two Pair"
    if 2 in c:
        return "Pair"
    return "High Card"

def card_chip_sum(cards: Iterable[Card]) -> int:
    return sum(RANK_CHIPS[c.rank] for c in cards)

def score_hand(played: List[Card], joker_effects: Iterable, context: Dict | None = None) -> ScoreBreakdown:
    hand_name = best_poker_hand(played)
    base_chips, base_mult = HAND_BASE[hand_name]
    cchips = card_chip_sum(played)
    bonus_chips = 0
    bonus_mult = 0
    # Apply jokers (simple interface: each contributes chip_delta and mult_delta)
    for j in joker_effects:
        bc, bm = j.modify(played=played, hand_name=hand_name, context=context or {})
        bonus_chips += bc
        bonus_mult += bm
    total_chips = base_chips + cchips + bonus_chips
    total_mult = max(0, base_mult + bonus_mult)
    total_score = total_chips * max(1, total_mult)
    return ScoreBreakdown(
        hand_name, base_chips, base_mult, cchips, bonus_chips, bonus_mult,
        total_chips, total_mult, total_score
    )
