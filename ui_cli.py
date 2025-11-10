from __future__ import annotations
import argparse
from typing import List
from .game import RunState, GameState
from .cards import format_cards

HELP = '''
Commands:
  d             Deal a new pool (draw 8)
  show          Show current pool
  pick i1..i5   Play 5 indices (0-based)
  auto          Auto-pick best 5, then play
  disc i..      Discard indices, draw replacements
  score         Show last hand breakdown
  shop          Open shop (after clearing a blind)
  buy n         Buy item n from shop (1-3)
  help          Show this help
  quit          Exit
'''

def main():
    parser = argparse.ArgumentParser(description="PyLatro - a Balatro-inspired terminal game")
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args()

    gs = GameState(RunState(rng_seed=args.seed))
    print("PyLatro — Balatro-inspired poker roguelite (terminal edition)")
    print(HELP)
    print(gs.summary())

    shop_open = False

    while True:
        try:
            cmd = input("> ").strip().split()
        except EOFError:
            print()
            break
        if not cmd:
            continue
        if cmd[0] in ("q","quit","exit"):
            break
        if cmd[0] in ("h","help"):
            print(HELP); continue
        if cmd[0] == "d":
            gs.deal()
            print("Pool:", format_cards(gs.current_pool))
            continue
        if cmd[0] == "show":
            print("Pool:", format_cards(gs.current_pool) if gs.current_pool else "(empty)")
            print(gs.summary())
            continue
        if cmd[0] == "disc":
            idx = sorted(set(int(i) for i in cmd[1:] if i.isdigit()))
            ok, msg = gs.discard_and_draw(idx)
            print(msg)
            if ok:
                print("Pool:", format_cards(gs.current_pool))
            continue
        if cmd[0] == "auto":
            if not gs.current_pool:
                print("Deal first with 'd'."); continue
            picks = gs.auto_pick()
            br, won, msg = gs.play_indices(picks)
            print(f"Played indices {picks}")
            print_breakdown(br)
            print(msg)
            print(gs.summary())
            shop_open = won
            continue
        if cmd[0] == "pick":
            if not gs.current_pool or len(cmd) < 6:
                print("Usage: pick i1 i2 i3 i4 i5 (0-based)"); continue
            picks = sorted(set(int(i) for i in cmd[1:6]))
            if len(picks) != 5:
                print("Need exactly 5 unique indices"); continue
            br, won, msg = gs.play_indices(picks)
            print_breakdown(br)
            print(msg)
            print(gs.summary())
            shop_open = won
            continue
        if cmd[0] == "score":
            if not gs.last_breakdown:
                print("No score yet."); continue
            print_breakdown(gs.last_breakdown); continue
        if cmd[0] == "shop":
            if not shop_open:
                print("Shop is only available right after clearing a blind.")
                continue
            lines = gs.open_shop()
            print("Shop offers:")
            for ln in lines: print("  " + ln)
            continue
        if cmd[0] == "buy":
            if len(cmd) < 2:
                print("Usage: buy N"); continue
            idx = int(cmd[1]) - 1
            print(gs.buy_from_shop(idx))
            print(gs.summary())
            shop_open = False
            continue
        print("Unknown command. Type 'help'.")

def print_breakdown(br):
    print("=== HAND RESULT ===")
    print(f"Hand: {br.hand_name}")
    print(f"Chips: {br.card_chips} + base {br.base_chips} + bonus {br.bonus_chips} = {br.total_chips}")
    print(f"Mult: base {br.base_mult} + bonus {br.bonus_mult} = {br.total_mult}")
    print(f"TOTAL: {br.total_score}")
    print("===================")

if __name__ == "__main__":
    main()
