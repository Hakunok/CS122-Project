# engine.py
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import List, Tuple, Dict, Callable
import random, itertools
from collections import Counter

class Suit(str, Enum):
    HEARTS="H"; DIAMONDS="D"; CLUBS="C"; SPADES="S"

class Rank(IntEnum):
    TWO=2; THREE=3; FOUR=4; FIVE=5; SIX=6; SEVEN=7; EIGHT=8; NINE=9
    TEN=10; JACK=11; QUEEN=12; KING=13; ACE=14

RANK_TO_CHAR = {r: s for r, s in zip(
    [Rank.TWO,Rank.THREE,Rank.FOUR,Rank.FIVE,Rank.SIX,Rank.SEVEN,Rank.EIGHT,Rank.NINE,Rank.TEN,Rank.JACK,Rank.QUEEN,Rank.KING,Rank.ACE],
    list("23456789TJQKA")
)}

@dataclass(frozen=True, order=True)
class Card:
    rank: Rank
    suit: Suit
    tags: Tuple[str, ...] = field(default_factory=tuple)
    def __str__(self): return f"{RANK_TO_CHAR[self.rank]}{self.suit.value}"

class Deck:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        self.shuffle()
    def shuffle(self): self.rng.shuffle(self.cards)
    def draw(self, n: int) -> List[Card]:
        drawn, self.cards = self.cards[:n], self.cards[n:]; return drawn

HAND_RANK_ORDER = {"high":1,"pair":2,"two_pair":3,"three":4,"straight":5,"flush":6,"full_house":7,"four":8,"straight_flush":9}

def _is_straight(ranks: List[int]) -> Tuple[bool,int]:
    rset = set(ranks)
    if len(rset) < 5: return False, 0
    rs = sorted(rset)
    for i in range(len(rs)-4):
        win = rs[i:i+5]
        if win == list(range(win[0], win[0]+5)): return True, win[-1]
    if {14,2,3,4,5}.issubset(rset): return True, 5  # A-2-3-4-5
    return False, 0

def _eval_five(cards: List[Card]) -> Tuple[str, Tuple]:
    ranks = [c.rank for c in cards]; suits = [c.suit for c in cards]
    counts = Counter(ranks); sorted_counts = sorted(counts.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    is_flush = len(set(suits)) == 1
    straight, high = _is_straight([int(r) for r in ranks])
    if is_flush and straight: return "straight_flush", (HAND_RANK_ORDER["straight_flush"], high)
    if sorted_counts[0][1] == 4:
        four = int(sorted_counts[0][0]); kicker = max(int(r) for r,c in counts.items() if c==1)
        return "four", (HAND_RANK_ORDER["four"], four, kicker)
    if sorted_counts[0][1]==3 and sorted_counts[1][1]==2:
        t = int(sorted_counts[0][0]); p = int(sorted_counts[1][0])
        return "full_house", (HAND_RANK_ORDER["full_house"], t, p)
    if is_flush:
        return "flush", (HAND_RANK_ORDER["flush"], *sorted((int(r) for r in ranks), reverse=True))
    if straight: return "straight", (HAND_RANK_ORDER["straight"], high)
    if sorted_counts[0][1] == 3:
        t = int(sorted_counts[0][0]); ks = sorted((int(r) for r,c in counts.items() if c==1), reverse=True)
        return "three", (HAND_RANK_ORDER["three"], t, *ks)
    if sorted_counts[0][1]==2 and sorted_counts[1][1]==2:
        a,b = int(sorted_counts[0][0]), int(sorted_counts[1][0]); k = max(int(r) for r,c in counts.items() if c==1)
        hi, lo = max(a,b), min(a,b)
        return "two_pair", (HAND_RANK_ORDER["two_pair"], hi, lo, k)
    if sorted_counts[0][1]==2:
        p = int(sorted_counts[0][0]); ks = sorted((int(r) for r,c in counts.items() if c==1), reverse=True)
        return "pair", (HAND_RANK_ORDER["pair"], p, *ks)
    return "high", (HAND_RANK_ORDER["high"], *sorted((int(r) for r in ranks), reverse=True))

def evaluate_best_hand(pool: List[Card]) -> Tuple[str, Tuple, List[Card]]:
    best_key = None; best_combo=None; best_name=""
    for combo in itertools.combinations(pool, 5):
        name, key = _eval_five(list(combo))
        if best_key is None or key > best_key:
            best_key, best_combo, best_name = key, list(combo), name
    return best_name, best_key, best_combo

# Baseline chips/mult (tune these as you balance)
HAND_BASE_CHIPS = {"high":5,"pair":15,"two_pair":25,"three":40,"straight":45,"flush":50,"full_house":60,"four":100,"straight_flush":200}
HAND_BASE_MULT  = {"high":1,"pair":1,"two_pair":2,"three":2,"straight":3,"flush":3,"full_house":4,"four":4,"straight_flush":5}

@dataclass
class HandContext:
    rng: random.Random
    played_cards: List[Card]
    hand_name: str
    base_chips: int
    base_mult: int
    chips_delta: int = 0
    mult_delta: int = 0

class Joker:
    name="Base"; rarity="common"
    def apply(self, ctx: HandContext) -> None: ...

class PerFaceAddMult(Joker):
    name="Court Jester"
    def apply(self, ctx: HandContext) -> None:
        face = {Rank.JACK, Rank.QUEEN, Rank.KING}
        ctx.mult_delta += sum(c.rank in face for c in ctx.played_cards)

class FlushFan(Joker):
    name="Rain Dancer"
    def apply(self, ctx: HandContext) -> None:
        if ctx.hand_name == "flush": ctx.mult_delta += 2

def score_hand(pool: List[Card], jokers: List[Joker], rng: random.Random) -> dict:
    hand_name, _, chosen = evaluate_best_hand(pool)
    ctx = HandContext(rng, chosen, hand_name, HAND_BASE_CHIPS[hand_name], HAND_BASE_MULT[hand_name])
    for j in jokers: j.apply(ctx)
    total = (ctx.base_chips + ctx.chips_delta) * (ctx.base_mult + ctx.mult_delta)
    return {
        "hand": hand_name,
        "played": [str(c) for c in chosen],
        "chips": ctx.base_chips, "mult": ctx.base_mult,
        "chips_delta": ctx.chips_delta, "mult_delta": ctx.mult_delta,
        "score": total
    }

if __name__ == "__main__":
    rng = random.Random(123)
    deck = Deck(rng)
    pool = deck.draw(8)  # draw 8, play best 5 (for now)
    jokers = [PerFaceAddMult(), FlushFan()]
    print("Pool:", " ".join(map(str, pool)))
    print(score_hand(pool, jokers, rng))
