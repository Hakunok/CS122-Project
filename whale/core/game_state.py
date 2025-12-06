from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

from config.constants import (
    HANDS_PER_POT,
    REROLLS_PER_HAND,
    BASE_POT_TARGET,
    POT_GROWTH_FACTOR,
)
from core.dice import DieState, make_plain_d6, RuleContext
from core.run_state import PotState
from core.shop import ShopState, ShopItem, roll_shop_for_floor


POTS_PER_FLOOR = 3

SMALL_POT_MULT = 0.9
BIG_POT_MULT = 1.1
BOSS_POT_MULT = 1.4

BASE_CHIP_FRACTION = 0.025
UNUSED_HAND_CHIPS = 2
UNUSED_REROLL_CHIPS = 2
INTEREST_PER_100 = 5
MAX_INTEREST_PER_POT = 25

BOSS_RULES_DATA: list[tuple[str, str]] = [
    ("Security", "One die starts locked for this pot."),
    ("Low Ceiling", "Values above 10 count as 10."),
    ("The Eye", "All dice are hidden until you submit."),
]

@dataclass
class BossRuleInfo:
    name: str
    description: str


@dataclass
class GameState:
    """
    Pure game state, used for serializing game for saving and loading.
    """
    seed: int
    floor: int
    pot_in_floor: int
    global_pot_number: int
    chips: int
    max_angles: int
    angles_count: int
    pot_state: PotState
    boss_rule: Optional[BossRuleInfo] = None
    owned_angles: List[str] = field(default_factory=list)
    owned_edges: List[str] = field(default_factory=list)
    shop_state: Optional[ShopState] = None


@dataclass
class SubmitOutcome:
    """
    Result of submitting a hand from the engine's perspective.
    'result' is the field returned by PotState.submit_hand()
    """
    result: object
    pot_cleared: bool
    pot_failed: bool
    chips_gained: int


class GameEngine:
    """
    Engine that controls the game flow.
    - Owns rng seed, rule context, dice and their state, and current potstate
    - tracks floors and pots, boss rules and chips
    - tracks owned angles and edges and current floors shop inventory
    - provides methods for game flow
    """

    def __init__(self, rng: Optional[random.Random] = None, seed: Optional[int] = None):
        if rng is not None:
            # if rng not provided generate a seed
            # this only happens when starting a new run
            self.rng = rng
            self.seed = seed if seed is not None else random.randrange(1_000_000_000)
        else:
            # use given rng seed, mainly for continuing run with a saved seed
            self.seed = seed if seed is not None else random.randrange(1_000_000_000)
            self.rng = random.Random(self.seed)

        # current dice
        dice_states: List[DieState] = [
            DieState.from_die(make_plain_d6(), self.rng) for _ in range(5)
        ]
        rule_ctx = RuleContext()

        pot_state = PotState(
            dice_states=dice_states,
            rule_ctx=rule_ctx,
            hands_per_pot=HANDS_PER_POT,
            base_rerolls=REROLLS_PER_HAND,
            pot_target=0,
            rng=self.rng,
        )

        self.rule_ctx = rule_ctx

        self.state = GameState(
            seed=self.seed,
            floor=1,
            pot_in_floor=1,
            global_pot_number=1,
            chips=0,
            max_angles=5,
            angles_count=0,
            pot_state=pot_state,
            boss_rule=None,
        )

        # first floor's shop
        self.state.shop_state = roll_shop_for_floor(
            floor=self.state.floor,
            rng=self.rng,
        )

        self.last_submit_outcome: Optional[SubmitOutcome] = None

    def is_boss_pot(self) -> bool:
        return self.state.pot_in_floor == POTS_PER_FLOOR

    def _compute_pot_target(self) -> int:
        """
        Compute pot target based on floor and pot.

        Floor scaling: BASE_POT_TARGET * POT_GROWTH_FACTOR^(floor-1)
        Pot is determined by {SMALL,BIG,BOSS}_POT_MULT * pot_in_floor
        """
        base_for_floor = BASE_POT_TARGET * (POT_GROWTH_FACTOR ** (self.state.floor - 1))
        if self.state.pot_in_floor == 1:
            pot_mult = SMALL_POT_MULT
        elif self.state.pot_in_floor == 2:
            pot_mult = BIG_POT_MULT
        else:
            pot_mult = BOSS_POT_MULT
        return int(round(base_for_floor * pot_mult))

    def _roll_boss_rule(self) -> Optional[BossRuleInfo]:
        if not self.is_boss_pot():
            return None
        name, desc = self.rng.choice(BOSS_RULES_DATA)
        return BossRuleInfo(name=name, description=desc)

    # these are methods that the UI uses
    def start_pot(self) -> None:
        """
        Start, and possibly restart, the current pot from hand 1.

        UI calls this (1) once at the beginning of the run
                      (2) after advance_to_next_pot()
        """
        self.state.boss_rule = self._roll_boss_rule()

        ps = self.state.pot_state
        ps.pot_target = self._compute_pot_target()
        ps.hands_per_pot = HANDS_PER_POT
        ps.base_rerolls = REROLLS_PER_HAND

        # TODO: i did this as a lazy implementation of Rookie angle
        # we will need to implement a better way of implementing ange effects
        bonus_rerolls = self._bonus_rerolls_from_angles()
        ps.base_rerolls += bonus_rerolls

        ps.start_first_hand()

        self.last_submit_outcome = None

    def _bonus_rerolls_from_angles(self) -> int:
        """
        TODO:
            for now this is just +1 reroll if Rookie is owned.
            NEED TO FIX OWNED_ANGLES TO ALLOW DUPE ANGLES
        in the future we would want to implement a proper effect system
        """
        return self.state.owned_angles.count("rookie")

    def toggle_lock(self, die_index: int) -> None:
        ds = self.state.pot_state.dice_states[die_index]
        ds.locked = not ds.locked

    def roll(self) -> bool:
        """
        reroll all unlocked die in the current pool
        returns True if any dice actually changed, meaning rerolls were evailable
        """
        return self.state.pot_state.reroll_unlocked()

    def _award_chips_for_pot(self) -> int:
        """
        this is just the mvp chip forula, we need to tweak
        - base: fraction of pot target
        - +10 per unused hand
        - +2 per remaining reroll
        - +interest: +5 per 100 chips (up to +25)
        """
        ps = self.state.pot_state

        base = int(ps.pot_target * BASE_CHIP_FRACTION)
        unused_hands = max(0, ps.hands_per_pot - ps.current_hand_index)
        hands_bonus = UNUSED_HAND_CHIPS * unused_hands
        reroll_bonus = UNUSED_REROLL_CHIPS * ps.rerolls_left
        interest = min(MAX_INTEREST_PER_POT, (self.state.chips // 100) * INTEREST_PER_100)

        gained = max(0, base + hands_bonus + reroll_bonus + interest)
        self.state.chips += gained
        return gained

    def submit_hand(self) -> SubmitOutcome:
        """
        Submit the currently selected dice for scoring.

        - Always returns a SubmitOutcome containing:
            - scoring result, from PotState
            - flags for pot_cleared / pot_failed
            - chips gained
        - If pot is not over, it automatically advances to the next hand.
        """
        ps = self.state.pot_state
        result = ps.submit_hand()

        pot_cleared = ps.pot_heat >= ps.pot_target
        pot_failed = False
        chips_gained = 0

        if pot_cleared:
            chips_gained = self._award_chips_for_pot()
        elif ps.is_pot_complete:
            pot_failed = True
        else:
            ps.start_hand()

        outcome = SubmitOutcome(
            result=result,
            pot_cleared=pot_cleared,
            pot_failed=pot_failed,
            chips_gained=chips_gained,
        )

        self.last_submit_outcome = outcome
        return outcome

    def advance_to_next_pot(self) -> None:
        """
        Move to the next pot; after a boss pot, advance to the next floor.
        ui should only call this when pot_cleared=True
        """
        self.state.global_pot_number += 1
        self.state.pot_in_floor += 1

        if self.state.pot_in_floor > POTS_PER_FLOOR:
            self.state.pot_in_floor = 1
            self.state.floor += 1
            # Reroll shop inventory for the new floor
            self.state.shop_state = roll_shop_for_floor(
                floor=self.state.floor,
                rng=self.rng,
            )

        self.start_pot()

    def get_shop_items(self) -> List[ShopItem]:
        """
        Get current floor's shop inventory.
        """
        if self.state.shop_state is None:
            self.state.shop_state = roll_shop_for_floor(
                floor=self.state.floor,
                rng=self.rng,
            )
        return self.state.shop_state.items

    def buy_shop_item(self, index: int) -> Tuple[bool, str]:
        """
        Attempt to buy shop item at index.

        Returns (success, message) for UI to display.
        """
        shop = self.state.shop_state
        if shop is None:
            return False, "No shop available."

        if not (0 <= index < len(shop.items)):
            return False, "No item at that position."

        item = shop.items[index]
        if item.purchased:
            return False, "Already purchased."

        if self.state.chips < item.cost:
            return False, "Not enough chips."

        # spend chips and marked purchase
        # TODO: right now duplicate item effects dont work
        # neither do levels for edges
        self.state.chips -= item.cost
        item.purchased = True

        if item.is_angle and item.id not in self.state.owned_angles:
            self.state.owned_angles.append(item.id)
            self.state.angles_count = len(self.state.owned_angles)

        if item.is_edge and item.id not in self.state.owned_edges:
            self.state.owned_edges.append(item.id)

        return True, f"Bought {item.name} for {item.cost} chips."

    def to_dict(self):
        # HOLY COW FIX THE LSP
        return {
            "seed": self.state.seed,
            "floor": self.state.floor,
            "pot_in_floor": self.state.pot_in_floor,
            "global_pot_number": self.state.global_pot_number,
            "chips": self.state.chips,
            "max_angles": self.state.max_angles,
            "angles_count": self.state.angles_count,
            "owned_angles": list(self.state.owned_angles),
            "owned_edges": list(self.state.owned_edges),
            "boss_rule": (
                {
                    "name": self.state.boss_rule.name,
                    "description": self.state.boss_rule.description,
                }
                if self.state.boss_rule
                else None
            ),
            "shop_state": (
                {
                    "floor": self.state.shop_state.floor,
                    "items": [
                        {
                            "kind": it.kind,
                            "id": it.id,
                            "name": it.name,
                            "description": it.description,
                            "cost": it.cost,
                            "purchased": it.purchased,
                        }
                        for it in self.state.shop_state.items
                    ],
                }
                if self.state.shop_state
                else None
            ),
            "pot_state": self.state.pot_state.to_dict(),
            "rng_state": list(self.rng.getstate()),
        }


    @classmethod
    def from_dict(cls, data: dict) -> "GameEngine":
        """
        Rebuild a GameEngine from a saved dict.

        restores:
          - high level run data
          - current pot state (dice, heat, rerolls, etc.)
          - rng state, so future rolls follow the same sequence.
        """
        seed = data.get("seed", random.randrange(1_000_000_000))
        engine = cls(seed=seed)

        # restore rng state
        rng_state_data = data.get("rng_state")

        if rng_state_data is not None:
            def _tupleify(obj):
                if isinstance(obj, list):
                    return tuple(_tupleify(x) for x in obj)
                return obj
            engine.rng.setstate(_tupleify(rng_state_data))

        s = engine.state
        s.floor = data.get("floor", 1)
        s.pot_in_floor = data.get("pot_in_floor", 1)
        s.global_pot_number = data.get("global_pot_number", 1)
        s.chips = data.get("chips", 0)
        s.max_angles = data.get("max_angles", 5)
        s.angles_count = data.get("angles_count", 0)
        s.owned_angles = list(data.get("owned_angles", []))
        s.owned_edges = list(data.get("owned_edges", []))

        boss = data.get("boss_rule")
        if boss is not None:
            s.boss_rule = BossRuleInfo(
                name=boss["name"],
                description=boss["description"],
            )
        else:
            s.boss_rule = None

        shop_data = data.get("shop_state")
        if shop_data is not None:
            items: List[ShopItem] = []
            for it in shop_data.get("items", []):
                items.append(
                    ShopItem(
                        kind=it["kind"],
                        id=it["id"],
                        name=it["name"],
                        description=it["description"],
                        cost=it["cost"],
                        purchased=it["purchased"],
                    )
                )
            s.shop_state = ShopState(
                floor=shop_data.get("floor", s.floor),
                items=items,
            )
        else:
            s.shop_state = roll_shop_for_floor(
                floor=s.floor,
                rng=engine.rng,
            )

        pot_data = data.get("pot_state")
        if pot_data is not None:
            s.pot_state = PotState.from_dict(
                pot_data,
                rng=engine.rng,
                rule_ctx=engine.rule_ctx,
            )
        else:
            engine.start_pot()

        return engine

