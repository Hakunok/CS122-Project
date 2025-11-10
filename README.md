# CS-122 Project: PyLatro - Balatro-Inspired Poker Roguelite

A Python-based poker roguelite game inspired by Balatro, featuring strategic deck-building, joker synergies, and progressively challenging blinds.

## 🎮 Game Overview

PyLatro is a terminal-based poker game where you:
- Play poker hands to defeat escalating "blinds" (score targets)
- Collect powerful jokers that modify your scoring
- Manage coins to buy strategic jokers from the shop
- Progress through antes with increasing difficulty

### Game Objective

Score enough points with your poker hands to defeat each blind. The game has three blind types per ante:
- **Small Blind** (75% difficulty)
- **Big Blind** (100% difficulty)  
- **Boss Blind** (125% difficulty)

After clearing all three blinds, you advance to the next ante with higher targets!

## 📦 Installation

```bash
# Clone or download the project
cd pylatro

# No external dependencies required - uses only Python standard library!
python -m pylatro.ui_cli
```

## 🎯 How to Play

### Starting a Game

```bash
# Start new game with default seed
python -m pylatro.ui_cli

# Start with custom seed
python -m pylatro.ui_cli --seed 42

# Load a saved game
python -m pylatro.ui_cli --load mysave.json
```

### Basic Gameplay Loop

1. **Deal cards**: Type `deal` to draw 8 cards
2. **Discard** (optional): Type `disc 0 2 5` to discard unwanted cards
3. **Play hand**: Type `pick 0 1 2 3 4` to play 5 cards, or `auto` to auto-select best
4. **Score points**: Try to reach the target score!
5. **Shop**: After clearing a blind, visit the shop to buy jokers
6. **Repeat**: Continue through Small → Big → Boss blinds

### Commands Reference

#### Game Actions
- `deal` / `d` - Deal 8 new cards to your pool
- `show` - Display current cards and game state
- `pick <i1> <i2> <i3> <i4> <i5>` - Play 5 cards by index (0-based)
- `auto` - Automatically select and play the best 5 cards
- `disc <i1> <i2> ...` - Discard cards and draw replacements

#### Shop & Strategy
- `shop` - Open the shop (available after clearing blinds)
- `buy <n>` - Purchase joker #n from shop (1-3)
- `skip` - Skip shop and continue to next blind

#### Information
- `score` - Show breakdown of your last hand
- `stats` - Display game statistics
- `help` / `h` - Show command list

#### Save/Load
- `save [filename]` - Save game (default: autosave.json)
- `load [filename]` - Load game (default: autosave.json)
- `saves` - List all available save files

#### Other
- `quit` / `q` - Exit game

## 🃏 Poker Hands

Hands are scored from lowest to highest:

| Hand | Example | Base Chips | Base Mult |
|------|---------|------------|-----------|
| High Card | A♠ K♥ 8♦ 5♣ 2♠ | 0 | 1 |
| Pair | 7♥ 7♠ K♦ 9♣ 3♠ | 10 | 1 |
| Two Pair | K♠ K♥ 5♦ 5♣ A♠ | 20 | 2 |
| Three of a Kind | Q♠ Q♥ Q♦ 8♣ 3♠ | 30 | 2 |
| Straight | 5♥ 6♠ 7♦ 8♣ 9♠ | 40 | 3 |
| Flush | 2♥ 5♥ 8♥ J♥ K♥ | 50 | 3 |
| Full House | 9♠ 9♥ 9♦ 4♣ 4♠ | 60 | 4 |
| Four of a Kind | A♠ A♥ A♦ A♣ K♠ | 80 | 5 |
| Straight Flush | 6♠ 7♠ 8♠ 9♠ 10♠ | 120 | 6 |

### Scoring Formula

```
Total Score = (Base Chips + Card Chips + Bonus Chips) × (Base Mult + Bonus Mult)
```

- **Base Chips/Mult**: From the poker hand type
- **Card Chips**: Sum of individual card values
- **Bonus Chips/Mult**: Added by jokers!

## 🃏 Jokers

Jokers are powerful modifiers that boost your scoring potential. Collect them from the shop!

### Common Jokers (70% shop rate)
- **Lucky Seven** ($3) - +10 chips if hand contains a 7
- **Pair Pal** ($3) - +15 chips for Pairs and Two Pairs
- **Flush Fan** ($4) - +2 mult for Flushes
- **Heartfelt** ($4) - +3 chips per ♥ card
- **Spade Master** ($4) - +3 chips per ♠ card
- **Royal Court** ($4) - +5 chips per face card (J/Q/K)
- **Numbers Game** ($3) - +2 chips per numbered card (2-10)
- **Odd Fellow** ($4) - +8 chips if all cards have odd ranks

### Uncommon Jokers (25% shop rate)
- **Variety Show** ($5) - +1 mult per 2 distinct ranks
- **Boss Hunter** ($6) - +10 chips, +2 mult vs Boss blinds
- **Straightedge** ($6) - +15 chips, +2 mult for Straights
- **Triple Agent** ($6) - +20 chips for Three of a Kind or better
- **Suit Collector** ($5) - +5 chips per unique suit
- **Multiplier Man** ($7) - +3 mult (pure boost)
- **Chip Champion** ($7) - +25 chips (pure boost)

### Rare Jokers (5% shop rate)
- **Rainbow Rush** ($10) - +10 chips, +3 mult if all 4 suits present
- **Ace in the Hole** ($8) - +30 chips, +3 mult if hand has an Ace
- **High Roller** ($10) - +1 mult per high card (10/J/Q/K/A)
- **Flush King** ($9) - +40 chips, +4 mult for Flushes
- **Poker Pro** ($12) - +5 mult for any scoring hand

## 💾 Save System

Your game automatically saves to `~/.pylatro/saves/` directory.

```bash
# Save your current game
> save mygame

# Load it later
python -m pylatro.ui_cli --load mygame

# Or from within the game
> load mygame

# List all saves
> saves
```

Save files contain:
- Current ante and blind stage
- Your joker collection
- Coins and statistics
- Deck state and RNG state (for consistency)

## 📊 Game Progression

### Blind Difficulty

Targets scale with ante progression:

```
Base Target = 80 + (Ante - 1) × 60

Small Blind = Base × 0.75
Big Blind = Base × 1.00
Boss Blind = Base × 1.25
```

Example progression:
- **Ante 1**: Small: 60, Big: 80, Boss: 100
- **Ante 2**: Small: 105, Big: 140, Boss: 175
- **Ante 3**: Small: 150, Big: 200, Boss: 250

### Rewards

- **Small Blind**: 3 coins + ante bonus
- **Big Blind**: 4 coins + ante bonus
- **Boss Blind**: 6 coins + ante bonus

Ante bonus = `ante // 2` coins

## 🎲 Strategy Tips

1. **Build synergies**: Combine jokers that work well together
2. **Plan ahead**: Think about which hands you can make consistently
3. **Manage discards**: Use them wisely to fish for better hands
4. **Boss preparation**: Save coins to buy powerful jokers before Boss blinds
5. **Know when to skip shop**: Don't waste coins on weak jokers
6. **Auto-pick vs manual**: Auto-pick is good, but manual gives you control
7. **Track your stats**: Use `stats` to see your progress

## 🏗️ Project Structure

```
pylatro/
├── __init__.py          # Package initialization
├── cards.py             # Card and deck management
├── scoring.py           # Poker hand evaluation and scoring
├── jokers.py            # Joker definitions and effects
├── blinds.py            # Blind target calculations
├── shop.py              # Shop system
├── game.py              # Core game state and logic
├── ui_cli.py            # Command-line interface
└── utils.py             # Utility classes
```

## 🔧 Code Architecture Improvements

### What's Been Improved

1. **Save/Load System**
   - Full game state serialization
   - Saves to user directory
   - RNG state preservation for consistency

2. **Better State Management**
   - Statistics tracking
   - Shop state handling
   - Cleaner separation of concerns

3. **Enhanced UX**
   - Colored output with emojis
   - Better error messages
   - Indexed card display
   - Auto-play feature

4. **Expanded Content**
   - 20+ unique jokers
   - Rarity system (common/uncommon/rare)
   - Weighted shop rolls

5. **Robust Error Handling**
   - Input validation
   - Graceful error recovery
   - Clear user feedback

6. **Code Quality**
   - Type hints throughout
   - Comprehensive docstrings
   - Clean separation of concerns
   - Easy to extend

## 🚀 Future Enhancement Ideas

- [ ] More joker types and synergies
- [ ] Special blind modifiers (e.g., "No Hearts allowed")
- [ ] Deck customization and unlocks
- [ ] Achievement system
- [ ] Leaderboards (high scores)
- [ ] Web-based UI
- [ ] Sound effects and animations
- [ ] Multiplayer modes
- [ ] Daily challenges

## 🤝 Contributing

Feel free to extend the game! Some ideas:
- Add new joker effects in `jokers.py`
- Create special blind modifiers in `blinds.py`
- Implement new scoring mechanics
- Build alternative UIs (web, GUI)

## 📝 License

This is a fan project inspired by Balatro. All poker and joker mechanics are original implementations.

## 🎮 Example Session

```
🃏 PyLatro — Balatro-inspired poker roguelite

> deal
🎴 Pool: 7♥ K♠ 3♦ Q♣ 8♠ 2♥ J♦ A♠
     [0] [1] [2] [3] [4] [5] [6] [7]

> pick 0 1 3 6 7
🎯 Played: 7♥ K♠ Q♣ J♦ A♠

=== HAND RESULT ===
🃏 Hand: Straight
🎯 Chips: 41 (cards) + 40 (base) + 0 (bonus) = 81
✖️  Mult: 3 (base) + 0 (bonus) = 3
⭐ TOTAL SCORE: 243
===================

Blind cleared! +3 coins. Visit the shop.
Ante 1 | Blind: Big | Target: 80 | Hands: 3 Discards: 2 | Coins: $8

💰 Shop is now available! Type 'shop' to browse.

> shop
🏪 === SHOP ===
  1. Flush Fan (common) - $4 :: +2 mult for Flush or Straight Flush
  2. Boss Hunter (uncommon) - $6 :: +10 chips and +2 mult against Boss blinds
  3. Lucky Seven (common) - $3 :: +10 chips if played hand contains a 7

You have $8
Type 'buy <n>' to purchase, or 'skip' to continue.

> buy 2
✅ Bought Boss Hunter.
Ante 1 | Blind: Boss | Target: 100 | Hands: 3 Discards: 2 | Coins: $2 | Jokers [1/5]: Boss Hunter
```

---

**Have fun and may the cards be ever in your favor! 🎰**


