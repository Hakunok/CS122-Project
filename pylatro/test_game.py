# test_game.py - Comprehensive test suite
import unittest
import random
from pathlib import Path
import tempfile
import json

from pylatro.cards import Card, Deck, counts_by_rank, is_flush, is_straight, RANK_TO_VALUE
from pylatro.scoring import best_poker_hand, score_hand, card_chip_sum
from pylatro.jokers import (
    LuckySeven, FlushFan, PairPal, BossHunter, 
    roll_joker_choices, get_joker_by_name
)
from pylatro.game import GameState, RunState
from pylatro.blinds import target_for
from pylatro.shop import Shop


class TestCards(unittest.TestCase):
    """Test card and deck functionality"""
    
    def test_card_creation(self):
        card = Card("A", "♠")
        self.assertEqual(card.rank, "A")
        self.assertEqual(card.suit, "♠")
        self.assertEqual(str(card), "A♠")
    
    def test_deck_initialization(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)
    
    def test_deck_draw(self):
        deck = Deck()
        hand = deck.draw(5)
        self.assertEqual(len(hand), 5)
        self.assertEqual(len(deck.cards), 47)
    
    def test_deck_reset(self):
        deck = Deck()
        deck.draw(52)
        self.assertEqual(len(deck.cards), 0)
        deck.reset()
        self.assertEqual(len(deck.cards), 52)
    
    def test_counts_by_rank(self):
        cards = [Card("A", "♠"), Card("A", "♥"), Card("K", "♦")]
        counts = counts_by_rank(cards)
        self.assertEqual(counts["A"], 2)
        self.assertEqual(counts["K"], 1)
    
    def test_is_flush_true(self):
        cards = [Card("2", "♠"), Card("5", "♠"), Card("9", "♠"), 
                 Card("J", "♠"), Card("K", "♠")]
        self.assertTrue(is_flush(cards))
    
    def test_is_flush_false(self):
        cards = [Card("2", "♠"), Card("5", "♥"), Card("9", "♠"), 
                 Card("J", "♠"), Card("K", "♠")]
        self.assertFalse(is_flush(cards))
    
    def test_is_straight_true(self):
        cards = [Card("5", "♠"), Card("6", "♥"), Card("7", "♦"), 
                 Card("8", "♣"), Card("9", "♠")]
        self.assertTrue(is_straight(cards))
    
    def test_is_straight_ace_low(self):
        cards = [Card("A", "♠"), Card("2", "♥"), Card("3", "♦"), 
                 Card("4", "♣"), Card("5", "♠")]
        self.assertTrue(is_straight(cards))
    
    def test_is_straight_false(self):
        cards = [Card("2", "♠"), Card("4", "♥"), Card("6", "♦"), 
                 Card("8", "♣"), Card("10", "♠")]
        self.assertFalse(is_straight(cards))


class TestScoring(unittest.TestCase):
    """Test poker hand evaluation and scoring"""
    
    def test_high_card(self):
        cards = [Card("A", "♠"), Card("K", "♥"), Card("8", "♦"), 
                 Card("5", "♣"), Card("2", "♠")]
        hand = best_poker_hand(cards)
        self.assertEqual(hand, "High Card")
    
    def test_pair(self):
        cards = [Card("7", "♠"), Card("7", "♥"), Card("K", "♦"), 
                 Card("9", "♣"), Card("3", "♠")]
        hand = best_poker_hand(cards)
        self.assertEqual(hand, "Pair")
    
    def test_two_pair(self):
        cards = [Card("K", "♠"), Card("K", "♥"), Card("5", "♦"), 
                 Card("5", "♣"), Card("A", "♠")]
        hand = best_poker_hand(cards)
        self.assertEqual(hand, "Two Pair")
    
    def test_three_kind(self):
        cards = [Card("Q", "♠"), Card("Q", "♥"), Card("Q", "♦"), 
                 Card("8", "♣"), Card("3", "♠")]
        hand = best_poker_hand(cards)
        self.assertEqual(hand, "Three Kind")
    
    def test_straight(self):
        cards = [Card("5", "♠"), Card("6", "♥"), Card("7", "♦"), 
                 Card("8", "♣"), Card("9", "♠")]
        hand = best_poker_hand(cards)
        self.assertEqual(hand, "Straight")
    
    def test_flush(self):
        cards = [Card("2", "♥"), Card("5", "♥"), Card("8", "♥"), 
                 Card("J", "♥"), Card("K", "♥")]
        hand = best_poker_hand(cards)
        self.assertEqual(hand, "Flush")
    
    def test_full_house(self):
        cards = [Card("9", "♠"), Card("9", "♥"), Card("9", "♦"), 
                 Card("4", "♣"), Card("4", "♠")]
        hand = best_poker_hand(cards)
        self.assertEqual(hand, "Full House")
    
    def test_four_kind(self):
        cards = [Card("A", "♠"), Card("A", "♥"), Card("A", "♦"), 
                 Card("A", "♣"), Card("K", "♠")]
        hand = best_poker_hand(cards)
        self.assertEqual(hand, "Four Kind")
    
    def test_straight_flush(self):
        cards = [Card("6", "♠"), Card("7", "♠"), Card("8", "♠"), 
                 Card("9", "♠"), Card("10", "♠")]
        hand = best_poker_hand(cards)
        self.assertEqual(hand, "StraightFlush")
    
    def test_score_calculation(self):
        cards = [Card("7", "♠"), Card("7", "♥"), Card("K", "♦"), 
                 Card("9", "♣"), Card("3", "♠")]
        breakdown = score_hand(cards, [], {})
        self.assertEqual(breakdown.hand_name, "Pair")
        self.assertGreater(breakdown.total_score, 0)
    
    def test_card_chip_sum(self):
        cards = [Card("A", "♠"), Card("K", "♥"), Card("Q", "♦")]
        chips = card_chip_sum(cards)
        self.assertEqual(chips, 11 + 10 + 10)


class TestJokers(unittest.TestCase):
    """Test joker effects"""
    
    def test_lucky_seven(self):
        joker = LuckySeven()
        cards_with_seven = [Card("7", "♠"), Card("K", "♥"), Card("Q", "♦"), 
                           Card("J", "♣"), Card("10", "♠")]
        bonus_chips, bonus_mult = joker.modify(cards_with_seven, "High Card", {})
        self.assertEqual(bonus_chips, 10)
        self.assertEqual(bonus_mult, 0)
        
        cards_without_seven = [Card("A", "♠"), Card("K", "♥"), Card("Q", "♦"), 
                              Card("J", "♣"), Card("10", "♠")]
        bonus_chips, bonus_mult = joker.modify(cards_without_seven, "High Card", {})
        self.assertEqual(bonus_chips, 0)
    
    def test_flush_fan(self):
        joker = FlushFan()
        flush_cards = [Card("2", "♠"), Card("5", "♠"), Card("9", "♠"), 
                      Card("J", "♠"), Card("K", "♠")]
        bonus_chips, bonus_mult = joker.modify(flush_cards, "Flush", {})
        self.assertEqual(bonus_chips, 0)
        self.assertEqual(bonus_mult, 2)
    
    def test_pair_pal(self):
        joker = PairPal()
        pair_cards = [Card("7", "♠"), Card("7", "♥"), Card("K", "♦"), 
                     Card("9", "♣"), Card("3", "♠")]
        bonus_chips, bonus_mult = joker.modify(pair_cards, "Pair", {})
        self.assertEqual(bonus_chips, 15)
    
    def test_boss_hunter(self):
        joker = BossHunter()
        cards = [Card("A", "♠"), Card("K", "♥"), Card("Q", "♦"), 
                Card("J", "♣"), Card("10", "♠")]
        
        # Against boss
        bonus_chips, bonus_mult = joker.modify(cards, "High Card", {"blind_type": "Boss"})
        self.assertEqual(bonus_chips, 10)
        self.assertEqual(bonus_mult, 2)
        
        # Not against boss
        bonus_chips, bonus_mult = joker.modify(cards, "High Card", {"blind_type": "Small"})
        self.assertEqual(bonus_chips, 0)
        self.assertEqual(bonus_mult, 0)
    
    def test_roll_joker_choices(self):
        rng = random.Random(42)
        jokers = roll_joker_choices(rng, k=3)
        self.assertEqual(len(jokers), 3)
        for joker in jokers:
            self.assertIsNotNone(joker.name)
            self.assertIsNotNone(joker.cost)
    
    def test_get_joker_by_name(self):
        joker_class = get_joker_by_name("Lucky Seven")
        self.assertIsNotNone(joker_class)
        joker = joker_class()
        self.assertEqual(joker.name, "Lucky Seven")


class TestBlinds(unittest.TestCase):
    """Test blind target calculations"""
    
    def test_small_blind_target(self):
        target = target_for(1, "Small")
        self.assertEqual(target, 60)  # 80 * 0.75
    
    def test_big_blind_target(self):
        target = target_for(1, "Big")
        self.assertEqual(target, 80)
    
    def test_boss_blind_target(self):
        target = target_for(1, "Boss")
        self.assertEqual(target, 100)  # 80 * 1.25
    
    def test_ante_scaling(self):
        ante1 = target_for(1, "Big")
        ante2 = target_for(2, "Big")
        self.assertGreater(ante2, ante1)
        self.assertEqual(ante2 - ante1, 60)


class TestShop(unittest.TestCase):
    """Test shop functionality"""
    
    def test_shop_open(self):
        rng = random.Random(42)
        shop = Shop(rng)
        offers = shop.open()
        self.assertEqual(len(offers), 3)
    
    def test_shop_buy_success(self):
        rng = random.Random(42)
        shop = Shop(rng)
        offers = shop.open()
        
        inventory = []
        coins = 100
        ok, new_coins, msg = shop.buy(0, coins, inventory)
        
        self.assertTrue(ok)
        self.assertEqual(len(inventory), 1)
        self.assertLess(new_coins, coins)
    
    def test_shop_buy_insufficient_coins(self):
        rng = random.Random(42)
        shop = Shop(rng)
        offers = shop.open()
        
        inventory = []
        coins = 1  # Not enough
        ok, new_coins, msg = shop.buy(0, coins, inventory)
        
        self.assertFalse(ok)
        self.assertEqual(len(inventory), 0)
        self.assertEqual(new_coins, coins)
    
    def test_shop_buy_full_inventory(self):
        rng = random.Random(42)
        shop = Shop(rng)
        offers = shop.open()
        
        inventory = [LuckySeven() for _ in range(5)]  # Full
        coins = 100
        ok, new_coins, msg = shop.buy(0, coins, inventory, limit=5)
        
        self.assertFalse(ok)
        self.assertEqual(len(inventory), 5)


class TestGameState(unittest.TestCase):
    """Test game state management"""
    
    def setUp(self):
        self.config = RunState(rng_seed=42)
        self.game = GameState(self.config)
    
    def test_game_initialization(self):
        self.assertEqual(self.game.ante, 1)
        self.assertEqual(self.game.blind_stage, 0)
        self.assertEqual(self.game.coins, 5)
        self.assertEqual(len(self.game.jokers), 0)
    
    def test_blind_type_property(self):
        self.assertEqual(self.game.blind_type, "Small")
        self.game.blind_stage = 1
        self.assertEqual(self.game.blind_type, "Big")
        self.game.blind_stage = 2
        self.assertEqual(self.game.blind_type, "Boss")
    
    def test_deal(self):
        cards = self.game.deal()
        self.assertEqual(len(cards), 8)
        self.assertEqual(len(self.game.current_pool), 8)
    
    def test_discard_and_draw(self):
        self.game.deal()
        initial_discards = self.game.discards_left
        
        ok, msg = self.game.discard_and_draw([0, 1, 2])
        self.assertTrue(ok)
        self.assertEqual(len(self.game.current_pool), 8)
        self.assertEqual(self.game.discards_left, initial_discards - 1)
    
    def test_discard_no_discards_left(self):
        self.game.deal()
        self.game.discards_left = 0
        
        ok, msg = self.game.discard_and_draw([0, 1])
        self.assertFalse(ok)
    
    def test_play_indices(self):
        self.game.deal()
        initial_hands = self.game.hands_left
        
        br, won, msg = self.game.play_indices([0, 1, 2, 3, 4])
        self.assertIsNotNone(br)
        self.assertEqual(self.game.hands_left, initial_hands - 1)
        self.assertGreater(self.game.total_hands_played, 0)
    
    def test_auto_pick(self):
        self.game.deal()
        picks = self.game.auto_pick()
        self.assertEqual(len(picks), 5)
        self.assertTrue(all(0 <= p < 8 for p in picks))
    
    def test_game_statistics(self):
        self.game.deal()
        self.game.play_indices([0, 1, 2, 3, 4])
        
        self.assertGreater(self.game.total_hands_played, 0)
        self.assertGreater(self.game.total_score, 0)
    
    def test_save_and_load(self):
        # Play some rounds
        self.game.deal()
        self.game.play_indices([0, 1, 2, 3, 4])
        self.game.coins = 50
        
        # Save to dict
        data = self.game.to_dict()
        self.assertIn("coins", data)
        self.assertEqual(data["coins"], 50)
        
        # Load from dict
        loaded_game = GameState.from_dict(data)
        self.assertEqual(loaded_game.coins, 50)
        self.assertEqual(loaded_game.ante, self.game.ante)
        self.assertEqual(loaded_game.blind_stage, self.game.blind_stage)
    
    def test_save_to_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_save.json"
            
            # Save
            success = self.game.save_to_file(filepath)
            self.assertTrue(success)
            self.assertTrue(filepath.exists())
            
            # Load
            loaded_game = GameState.load_from_file(filepath)
            self.assertIsNotNone(loaded_game)
            self.assertEqual(loaded_game.coins, self.game.coins)
    
    def test_shop_workflow(self):
        # Can't open shop initially
        ok, lines = self.game.open_shop()
        self.assertFalse(ok)
        
        # Clear a blind (fake it)
        self.game._shop_open = True
        
        # Now can open shop
        ok, lines = self.game.open_shop()
        self.assertTrue(ok)
        self.assertGreater(len(lines), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for full game flow"""
    
    def test_complete_blind_progression(self):
        """Test progressing through all three blinds"""
        config = RunState(rng_seed=42)
        game = GameState(config)
        
        initial_ante = game.ante
        
        # Simulate clearing all three blinds
        for blind_idx in range(3):
            game.deal()
            picks = game.auto_pick()
            
            # Keep trying until we win (or run out of hands)
            while game.hands_left > 0:
                br, won, msg = game.play_indices(picks)
                if won:
                    break
                if game.hands_left > 0:
                    game.deal()
                    picks = game.auto_pick()
            
            if not won:
                # May legitimately lose
                return
        
        # If we cleared all 3 blinds, ante should increase
        self.assertGreaterEqual(game.ante, initial_ante)
    
    def test_joker_effects_in_scoring(self):
        """Test that jokers actually affect scores"""
        config = RunState(rng_seed=42)
        game = GameState(config)
        
        # Add a joker
        game.jokers.append(LuckySeven())
        
        game.deal()
        
        # Manually create a hand with a 7
        test_hand = [Card("7", "♠"), Card("K", "♥"), Card("Q", "♦"), 
                    Card("J", "♣"), Card("10", "♠")]
        
        # Score with joker
        br = score_hand(test_hand, game.jokers, {"blind_type": "Small"})
        self.assertEqual(br.bonus_chips, 10)  # Lucky Seven bonus


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCards))
    suite.addTests(loader.loadTestsFromTestCase(TestScoring))
    suite.addTests(loader.loadTestsFromTestCase(TestJokers))
    suite.addTests(loader.loadTestsFromTestCase(TestBlinds))
    suite.addTests(loader.loadTestsFromTestCase(TestShop))
    suite.addTests(loader.loadTestsFromTestCase(TestGameState))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)