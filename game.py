# game.py - Enhanced version with save/load and better state management
from __future__ import annotations
import random, itertools, json, os
from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from .cards import Deck, Card, format_cards
from .scoring import score_hand, ScoreBreakdown
from .jokers import Joker, ALL_JOKERS
from .blinds import target_for
from .shop import Shop

@dataclass
class RunState:
    """Configuration for a game run"""
    rng_seed: int = 123
    hands_per_blind: int = 3
    discards_per_blind: int = 2
    draw_size: int = 8
    hand_size: int = 5
    starting_coins: int = 5
    max_jokers: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RunState:
        return cls(**data)

@dataclass
class GameState:
    """Main game state with enhanced features"""
    config: RunState
    rng: random.Random = field(default_factory=random.Random)
    deck: Deck = field(init=False)
    coins: int = field(init=False)
    jokers: List[Joker] = field(default_factory=list)
    ante: int = 1
    blind_stage: int = 0  # 0=Small, 1=Big, 2=Boss
    hands_left: int = 0
    discards_left: int = 0
    current_pool: List[Card] = field(default_factory=list)
    target_score: int = 0
    last_breakdown: Optional[ScoreBreakdown] = None
    
    # Statistics tracking
    total_hands_played: int = 0
    total_score: int = 0
    blinds_cleared: int = 0
    highest_score: int = 0
    
    # Shop state
    _shop: Optional[Shop] = field(default=None, repr=False)
    _shop_open: bool = False

    def __post_init__(self):
        self.coins = self.config.starting_coins
        self.rng.seed(self.config.rng_seed)
        self.deck = Deck(self.rng)
        self.start_blind()

    @property
    def blind_type(self) -> str:
        return ["Small", "Big", "Boss"][self.blind_stage]
    
    @property
    def is_shop_available(self) -> bool:
        return self._shop_open
    
    @property
    def max_jokers(self) -> int:
        return self.config.max_jokers

    def start_blind(self):
        """Initialize a new blind"""
        self.hands_left = self.config.hands_per_blind
        self.discards_left = self.config.discards_per_blind
        self.current_pool = []
        self.target_score = target_for(self.ante, self.blind_type)
        self.last_breakdown = None
        self._shop_open = False

    def deal(self) -> List[Card]:
        """Deal new cards to the pool"""
        self.current_pool = self.deck.draw(self.config.draw_size)
        return self.current_pool

    def discard_and_draw(self, indices: List[int]) -> Tuple[bool, str]:
        """Discard selected cards and draw replacements"""
        if self.discards_left <= 0:
            return False, "No discards left."
        
        if not indices:
            return False, "No cards selected to discard."
        
        # Validate indices
        if any(i < 0 or i >= len(self.current_pool) for i in indices):
            return False, "Invalid card indices."
        
        keep = [c for i, c in enumerate(self.current_pool) if i not in indices]
        need = self.config.draw_size - len(keep)
        keep.extend(self.deck.draw(need))
        self.current_pool = keep
        self.discards_left -= 1
        return True, f"Discarded {len(indices)} card(s)."

    def auto_pick(self) -> List[int]:
        """Automatically select the best 5 cards"""
        if len(self.current_pool) < self.config.hand_size:
            return list(range(len(self.current_pool)))
        
        best_idx = list(range(self.config.hand_size))
        best_score = -1
        
        for comb in itertools.combinations(range(len(self.current_pool)), self.config.hand_size):
            played = [self.current_pool[i] for i in comb]
            br = score_hand(played, self.jokers, {"blind_type": self.blind_type})
            if br.total_score > best_score:
                best_score = br.total_score
                best_idx = list(comb)
        
        return best_idx

    def play_indices(self, indices: List[int]) -> Tuple[ScoreBreakdown, bool, str]:
        """Play selected cards"""
        if self.hands_left <= 0:
            return None, False, "No hands left."
        
        if len(indices) != self.config.hand_size:
            return None, False, f"Must play exactly {self.config.hand_size} cards."
        
        if any(i < 0 or i >= len(self.current_pool) for i in indices):
            return None, False, "Invalid card indices."
        
        played = [self.current_pool[i] for i in indices]
        self.hands_left -= 1
        self.total_hands_played += 1
        
        br = score_hand(played, self.jokers, {"blind_type": self.blind_type})
        self.last_breakdown = br
        self.total_score += br.total_score
        self.highest_score = max(self.highest_score, br.total_score)
        
        won = br.total_score >= self.target_score
        
        if won:
            self.blinds_cleared += 1
            # Award coins based on blind type and ante
            reward = self._calculate_reward()
            self.coins += reward
            
            # Advance stage
            self.blind_stage += 1
            if self.blind_stage >= 3:
                # Next ante
                self.ante += 1
                self.blind_stage = 0
            
            self.start_blind()
            self._shop_open = True
            return br, True, f"Blind cleared! +{reward} coins. Visit the shop."
        else:
            if self.hands_left == 0:
                return br, False, "Out of hands — run over."
            return br, False, f"Keep trying. Need {self.target_score - br.total_score} more points."
    
    def _calculate_reward(self) -> int:
        """Calculate coin reward for clearing a blind"""
        base = 3
        blind_bonus = {"Small": 0, "Big": 1, "Boss": 3}[self.blind_type]
        ante_bonus = self.ante // 2
        return base + blind_bonus + ante_bonus

    def open_shop(self) -> Tuple[bool, List[str]]:
        """Open the shop (only available after clearing a blind)"""
        if not self._shop_open:
            return False, ["Shop is only available after clearing a blind."]
        
        self._shop = Shop(self.rng)
        offers = self._shop.open()
        
        lines = []
        for i, o in enumerate(offers):
            lines.append(
                f"{i+1}. {o.joker.name} ({o.joker.rarity}) - ${o.price} :: {o.joker.describe()}"
            )
        return True, lines

    def buy_from_shop(self, idx: int) -> Tuple[bool, str]:
        """Purchase a joker from the shop"""
        if not self._shop:
            return False, "Shop is not open."
        
        ok, self.coins, msg = self._shop.buy(idx, self.coins, self.jokers, self.max_jokers)
        return ok, msg
    
    def close_shop(self):
        """Close the shop and continue to next blind"""
        self._shop_open = False
        self._shop = None

    def summary(self) -> str:
        """Get a summary of the current game state"""
        jnames = ", ".join(j.name for j in self.jokers) if self.jokers else "(none)"
        return (
            f"Ante {self.ante} | Blind: {self.blind_type} | Target: {self.target_score} | "
            f"Hands: {self.hands_left} Discards: {self.discards_left} | Coins: ${self.coins} | "
            f"Jokers [{len(self.jokers)}/{self.max_jokers}]: {jnames}"
        )
    
    def statistics(self) -> str:
        """Get game statistics"""
        return (
            f"=== Statistics ===\n"
            f"Ante: {self.ante}\n"
            f"Blinds Cleared: {self.blinds_cleared}\n"
            f"Total Hands Played: {self.total_hands_played}\n"
            f"Total Score: {self.total_score:,}\n"
            f"Highest Single Hand: {self.highest_score:,}\n"
            f"Coins: ${self.coins}"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize game state to dictionary"""
        return {
            "config": self.config.to_dict(),
            "rng_state": self.rng.getstate(),
            "coins": self.coins,
            "jokers": [j.name for j in self.jokers],
            "ante": self.ante,
            "blind_stage": self.blind_stage,
            "hands_left": self.hands_left,
            "discards_left": self.discards_left,
            "current_pool": [(c.rank, c.suit) for c in self.current_pool],
            "target_score": self.target_score,
            "total_hands_played": self.total_hands_played,
            "total_score": self.total_score,
            "blinds_cleared": self.blinds_cleared,
            "highest_score": self.highest_score,
            "deck_cards": [(c.rank, c.suit) for c in self.deck.cards],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GameState:
        """Deserialize game state from dictionary"""
        config = RunState.from_dict(data["config"])
        gs = cls.__new__(cls)
        gs.config = config
        gs.coins = data["coins"]
        
        # Restore RNG state
        gs.rng = random.Random()
        gs.rng.setstate(data["rng_state"])
        
        # Restore deck
        gs.deck = Deck(gs.rng)
        gs.deck.cards = [Card(r, s) for r, s in data["deck_cards"]]
        
        # Restore jokers
        joker_map = {j().name: j for j in ALL_JOKERS}
        gs.jokers = [joker_map[name]() for name in data["jokers"] if name in joker_map]
        
        gs.ante = data["ante"]
        gs.blind_stage = data["blind_stage"]
        gs.hands_left = data["hands_left"]
        gs.discards_left = data["discards_left"]
        gs.current_pool = [Card(r, s) for r, s in data["current_pool"]]
        gs.target_score = data["target_score"]
        gs.total_hands_played = data["total_hands_played"]
        gs.total_score = data["total_score"]
        gs.blinds_cleared = data["blinds_cleared"]
        gs.highest_score = data["highest_score"]
        gs.last_breakdown = None
        gs._shop = None
        gs._shop_open = False
        
        return gs
    
    def save_to_file(self, filepath: str | Path) -> bool:
        """Save game state to a file"""
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str | Path) -> Optional[GameState]:
        """Load game state from a file"""
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading game: {e}")
            return None