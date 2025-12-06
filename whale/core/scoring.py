from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

from core.dice import Face, RuleContext
from config.hands import HAND_DEFS, HandDef


@dataclass(slots=True)
class HandResult:
    """
    used for displaying formula for calculate dheat
    """
    hand_id: str
    hand_def: HandDef

    pattern_values: List[int]
    sum_values: List[int]

    sum_term: int
    base_heat_bonus: int
    heat_before_mult: int
    base_mult: float

    total_heat: int


def _value_counts(values: List[int]) -> Dict[int, int]:
    counts: Dict[int, int] = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return counts


def _is_flush(faces: List[Face]) -> bool:
    suits = [f.suit for f in faces]
    if any(s is None for s in suits):
        return False
    return len(set(suits)) == 1


def _detect_straight(values: List[int]) -> Tuple[bool, bool]:
    """
    returns (is_straight, is_ace_high_straight).

    Values are pattern values, after all rules are applied.  A = 1.
      - normal straights (e.g. 2,3,4,5,6)
      - ace low (1,2,3,4,5)
      - ace high (10,11,12,13,1)
    """
    uniq = sorted(set(values))
    if len(uniq) != 5:
        return False, False

    if set(uniq) == {1, 10, 11, 12, 13}:
        return True, True

    if max(uniq) - min(uniq) == 4 and len(uniq) == 5:
        return True, False

    return False, False


def _all_royal_family(faces: List[Face], ctx: RuleContext) -> bool:
    """
    Royal family: all faces are J/Q/K or wild, under current rules.
    Dead faces still qualify for royal-hand classification.
        # THIS IS NEVER CALLED BECAUSE WE ONLY HAVE d6 and no royal loaded faces
    """
    for f in faces:
        if not f.is_royal_for_hand(ctx):
            return False
    return True


def _classify_royal_family(pattern_values: List[int]) -> str:
    """
    Given 5 royal-family pattern values, return which royal_* hand_id applies.
    """
    counts = _value_counts(pattern_values)
    freqs = sorted(counts.values(), reverse=True)

    if freqs == [5]:
        return "royal_5kind"
    if freqs == [4, 1]:
        return "royal_4kind"
    if freqs == [3, 2]:
        return "royal_fullhouse"
    if freqs == [3, 1, 1]:
        return "royal_3kind"
    if freqs == [2, 2, 1]:
        return "royal_2pair"

    # this should basically never hit
    return "std_highcard"


def _classify_standard(faces: List[Face], ctx: RuleContext) -> str:
    # THESE FOLLOW THE PRIORITY LISTED IN HANDDEFS, but we should proabbly also
    # enforce this in these hand scoring functions
    pattern_values = [f.pattern_value(ctx) for f in faces]
    counts = _value_counts(pattern_values)
    freqs = sorted(counts.values(), reverse=True)

    is_flush = _is_flush(faces)
    is_straight, is_ace_high = _detect_straight(pattern_values)

    # this is a straight containing all three royals, NOT A ROYAL HAND
    if is_flush and is_straight and set(pattern_values) == {9, 10, 11, 12, 13}:
        return "std_royal_flush"

    # Straight flush
    if is_flush and is_straight:
        return "std_straight_flush"

    # Five/four/full house
    if freqs == [5]:
        return "std_5kind"
    if freqs == [4, 1]:
        return "std_4kind"
    if freqs == [3, 2]:
        return "std_fullhouse"

    # Flush
    if is_flush:
        return "std_flush"

    # Straight
    if is_straight:
        # ace high straight (10, J, Q, K, A)
        if is_ace_high:
            return "std_high_straight"
        return "std_straight"

    # 3-kind, 2-pair, pair, high card
    if freqs == [3, 1, 1]:
        return "std_3kind"
    if freqs == [2, 2, 1]:
        return "std_2pair"
    if freqs == [2, 1, 1, 1]:
        return "std_pair"

    return "std_highcard"


def score_5dice(faces: List[Face], ctx: Optional[RuleContext] = None) -> HandResult:
    """
    Score exactly five dice and return HandResult which contains the scored hant and
        the scoring breakdown

    for now....
        heat_before_mult = sum(sum_values) + base_heat_bonus
        total_heat = round(heat_before_mult * base_mult)
    """
    if ctx is None:
        ctx = RuleContext()

    pattern_values = [f.pattern_value(ctx) for f in faces]
    sum_values = [f.sum_value(ctx) for f in faces]

    # royal first rule
    if _all_royal_family(faces, ctx):
        hand_id = _classify_royal_family(pattern_values)
    else:
        hand_id = _classify_standard(faces, ctx)

    hand_def = HAND_DEFS[hand_id]

    sum_term = sum(sum_values)
    base_heat_bonus = hand_def.base_heat
    heat_before_mult = sum_term + base_heat_bonus
    base_mult = hand_def.base_mult
    total_heat = int(round(heat_before_mult * base_mult))

    return HandResult(
        hand_id=hand_id,
        hand_def=hand_def,
        pattern_values=pattern_values,
        sum_values=sum_values,
        sum_term=sum_term,
        base_heat_bonus=base_heat_bonus,
        heat_before_mult=heat_before_mult,
        base_mult=base_mult,
        total_heat=total_heat,
    )

