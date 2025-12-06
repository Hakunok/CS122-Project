from __future__ import annotations
from dataclasses import dataclass
from typing import List
import random

from core.dice import DieState, RuleContext
from core.scoring import score_5dice, HandResult


@dataclass
class PotState:
    """
    A singular pot:
    - Fixed number of hands
    - Fixed number of rerolls per hand.
    - Target Heat to clear the pot.
    """

    dice_states: List[DieState]
    rule_ctx: RuleContext
    hands_per_pot: int
    base_rerolls: int
    pot_target: int
    rng: random.Random

    current_hand_index: int = 0
    rerolls_left: int = 0
    pot_heat: int = 0

    def start_first_hand(self) -> None:
        """Reset pot total and start the first hand."""
        self.current_hand_index = 0
        self.pot_heat = 0
        self.start_hand()

    def start_hand(self) -> None:
        """Start a new hand, reset rerolls and roll all dice."""
        self.rerolls_left = self.base_rerolls
        for ds in self.dice_states:
            ds.locked = False
            ds.roll(self.rng)

    def reroll_unlocked(self) -> bool:
        """Reroll all unlocked dice, if we have rerolls left."""
        if self.rerolls_left <= 0:
            return False
        for ds in self.dice_states:
            if not ds.locked:
                ds.roll(self.rng)
        self.rerolls_left -= 1
        return True

    def submit_hand(self) -> HandResult:
        """
        Score the current 5 dice, add to pot Heat, advance hand index.
        caller is responsible for starting the next hand or ending the pot.
            TODO although we should probably have the GameEngine handle all of this
                 find out ways to make this completely ui agnostic
                 cause right now the ui is responsibel for the flow of the game,
                 while game engine semienforces rules
        """
        faces = [ds.current_face for ds in self.dice_states]
        result = score_5dice(faces, self.rule_ctx)
        self.pot_heat += result.total_heat
        self.current_hand_index += 1
        return result

    @property
    def hands_remaining(self) -> int:
        return max(0, self.hands_per_pot - self.current_hand_index)

    @property
    def current_hand_number(self) -> int:
        if self.current_hand_index >= self.hands_per_pot:
            return self.hands_per_pot
        return self.current_hand_index + 1

    @property
    def is_pot_complete(self) -> bool:
        return self.current_hand_index >= self.hands_per_pot

    @property
    def is_pot_cleared(self) -> bool:
        return self.pot_heat >= self.pot_target

    def to_dict(self):
        return {
            "dice_states": [ds.to_dict() for ds in self.dice_states],
            "hands_per_pot": self.hands_per_pot,
            "base_rerolls": self.base_rerolls,
            "pot_target": self.pot_target,
            "current_hand_index": self.current_hand_index,
            "rerolls_left": self.rerolls_left,
            "pot_heat": self.pot_heat,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
        rng: random.Random,
        rule_ctx: RuleContext,
    ) -> "PotState":
        dice_states = [DieState.from_dict(ds) for ds in data["dice_states"]]
        return cls(
            dice_states=dice_states,
            rule_ctx=rule_ctx,
            hands_per_pot=data["hands_per_pot"],
            base_rerolls=data["base_rerolls"],
            pot_target=data["pot_target"],
            rng=rng,
            current_hand_index=data.get("current_hand_index", 0),
            rerolls_left=data.get("rerolls_left", 0),
            pot_heat=data.get("pot_heat", 0),
        )

