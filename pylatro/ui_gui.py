# ui_gui.py - Graphical User Interface for PyLatro using Tkinter
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import List, Optional
import random

from .game import GameState, RunState
from .cards import Card, format_cards

# Color scheme inspired by Balatro
COLORS = {
    'bg': '#1a1a2e',
    'card_bg': '#16213e',
    'accent': '#0f3460',
    'highlight': '#e94560',
    'text': '#eaeaea',
    'gold': '#ffd700',
    'green': '#2ecc71',
    'red': '#e74c3c',
    'blue': '#3498db',
}

SUITS_COLORS = {
    '♠': '#000000',
    '♥': '#e74c3c',
    '♦': '#e74c3c',
    '♣': '#000000',
}


class CardWidget(tk.Frame):
    """A visual representation of a playing card"""
    
    def __init__(self, parent, card: Card, index: int, selected_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.card = card
        self.index = index
        self.selected = False
        self.selected_callback = selected_callback
        
        # Configure card appearance
        self.configure(
            bg=COLORS['card_bg'],
            relief=tk.RAISED,
            borderwidth=2,
            width=80,
            height=110
        )
        
        # Card rank
        rank_label = tk.Label(
            self,
            text=card.rank,
            font=('Arial', 20, 'bold'),
            bg=COLORS['card_bg'],
            fg=SUITS_COLORS.get(card.suit, COLORS['text'])
        )
        rank_label.pack(pady=(5, 0))
        
        # Card suit
        suit_label = tk.Label(
            self,
            text=card.suit,
            font=('Arial', 24),
            bg=COLORS['card_bg'],
            fg=SUITS_COLORS.get(card.suit, COLORS['text'])
        )
        suit_label.pack()
        
        # Index label
        index_label = tk.Label(
            self,
            text=f"[{index}]",
            font=('Arial', 8),
            bg=COLORS['card_bg'],
            fg=COLORS['text']
        )
        index_label.pack(pady=(5, 5))
        
        # Bind click event
        self.bind('<Button-1>', self.on_click)
        for child in self.winfo_children():
            child.bind('<Button-1>', self.on_click)
    
    def on_click(self, event=None):
        """Toggle card selection"""
        self.selected = not self.selected
        if self.selected:
            self.configure(relief=tk.SUNKEN, borderwidth=3, bg=COLORS['highlight'])
            for child in self.winfo_children():
                child.configure(bg=COLORS['highlight'])
        else:
            self.configure(relief=tk.RAISED, borderwidth=2, bg=COLORS['card_bg'])
            for child in self.winfo_children():
                child.configure(bg=COLORS['card_bg'])
        
        if self.selected_callback:
            self.selected_callback()


class PyLatroGUI:
    """Main GUI application for PyLatro"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PyLatro - Poker Roguelite")
        self.root.geometry("1200x800")
        self.root.configure(bg=COLORS['bg'])
        
        # Game state
        self.game: Optional[GameState] = None
        self.card_widgets: List[CardWidget] = []
        
        # Setup UI
        self.setup_ui()
        
        # Start new game
        self.new_game()
    
    def setup_ui(self):
        """Create the UI layout"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_command(label="Save Game", command=self.save_game)
        game_menu.add_command(label="Load Game", command=self.load_game)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Play", command=self.show_help)
        help_menu.add_command(label="Statistics", command=self.show_stats)
        
        # Top panel - Game info
        self.top_frame = tk.Frame(self.root, bg=COLORS['accent'], height=80)
        self.top_frame.pack(fill=tk.X, padx=10, pady=10)
        self.top_frame.pack_propagate(False)
        
        self.info_label = tk.Label(
            self.top_frame,
            text="",
            font=('Arial', 12, 'bold'),
            bg=COLORS['accent'],
            fg=COLORS['text'],
            justify=tk.LEFT
        )
        self.info_label.pack(pady=10, padx=10)
        
        # Middle panel - Cards
        self.middle_frame = tk.Frame(self.root, bg=COLORS['bg'])
        self.middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Card area
        card_frame_container = tk.Frame(self.middle_frame, bg=COLORS['bg'])
        card_frame_container.pack(fill=tk.BOTH, expand=True)
        
        card_label = tk.Label(
            card_frame_container,
            text="Your Hand",
            font=('Arial', 14, 'bold'),
            bg=COLORS['bg'],
            fg=COLORS['text']
        )
        card_label.pack(pady=5)
        
        self.card_frame = tk.Frame(card_frame_container, bg=COLORS['bg'])
        self.card_frame.pack(pady=10)
        
        # Result area
        self.result_frame = tk.Frame(self.middle_frame, bg=COLORS['accent'], relief=tk.SUNKEN, borderwidth=2)
        self.result_frame.pack(fill=tk.X, pady=10)
        
        self.result_label = tk.Label(
            self.result_frame,
            text="Welcome to PyLatro! Click 'Deal' to start.",
            font=('Arial', 11),
            bg=COLORS['accent'],
            fg=COLORS['text'],
            justify=tk.LEFT,
            wraplength=1000
        )
        self.result_label.pack(pady=10, padx=10)
        
        # Bottom panel - Controls
        self.bottom_frame = tk.Frame(self.root, bg=COLORS['accent'])
        self.bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.bottom_frame, bg=COLORS['accent'])
        button_frame.pack(pady=10)
        
        # Create buttons
        self.create_button(button_frame, "Deal", self.deal_cards, COLORS['blue'])
        self.create_button(button_frame, "Play Selected", self.play_selected, COLORS['green'])
        self.create_button(button_frame, "Auto Play", self.auto_play, COLORS['highlight'])
        self.create_button(button_frame, "Discard Selected", self.discard_selected, COLORS['red'])
        self.create_button(button_frame, "Shop", self.open_shop, COLORS['gold'])
        
        # Selection info
        self.selection_label = tk.Label(
            self.bottom_frame,
            text="Select 5 cards to play",
            font=('Arial', 10),
            bg=COLORS['accent'],
            fg=COLORS['text']
        )
        self.selection_label.pack(pady=5)
    
    def create_button(self, parent, text, command, color):
        """Create a styled button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Arial', 11, 'bold'),
            bg=color,
            fg='white',
            activebackground=color,
            activeforeground='white',
            relief=tk.RAISED,
            borderwidth=2,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        btn.pack(side=tk.LEFT, padx=5)
        return btn
    
    def new_game(self):
        """Start a new game"""
        seed = random.randint(1, 1000000)
        self.game = GameState(RunState(rng_seed=seed))
        self.update_display()
        self.clear_cards()
        self.result_label.config(text=f"New game started! (Seed: {seed})\nClick 'Deal' to draw cards.")
    
    def update_display(self):
        """Update the game info display"""
        if not self.game:
            return
        
        joker_names = ", ".join(j.name for j in self.game.jokers) if self.game.jokers else "None"
        
        info_text = (
            f"🎲 Ante {self.game.ante} | "
            f"🎯 Blind: {self.game.blind_type} | "
            f"📊 Target: {self.game.target_score:,} | "
            f"🃏 Hands: {self.game.hands_left} | "
            f"♻️ Discards: {self.game.discards_left} | "
            f"💰 Coins: ${self.game.coins}\n"
            f"🃏 Jokers [{len(self.game.jokers)}/{self.game.max_jokers}]: {joker_names}"
        )
        
        self.info_label.config(text=info_text)
    
    def clear_cards(self):
        """Clear all card widgets"""
        for widget in self.card_widgets:
            widget.destroy()
        self.card_widgets.clear()
    
    def display_cards(self):
        """Display the current pool of cards"""
        self.clear_cards()
        
        if not self.game or not self.game.current_pool:
            return
        
        for i, card in enumerate(self.game.current_pool):
            card_widget = CardWidget(
                self.card_frame,
                card,
                i,
                selected_callback=self.update_selection_info
            )
            card_widget.pack(side=tk.LEFT, padx=5, pady=5)
            self.card_widgets.append(card_widget)
    
    def get_selected_indices(self) -> List[int]:
        """Get indices of selected cards"""
        return [w.index for w in self.card_widgets if w.selected]
    
    def update_selection_info(self):
        """Update the selection info label"""
        selected = self.get_selected_indices()
        count = len(selected)
        
        if count == 0:
            self.selection_label.config(text="Select cards to play or discard")
        elif count < 5:
            self.selection_label.config(text=f"Selected {count}/5 cards for playing")
        elif count == 5:
            self.selection_label.config(
                text=f"✓ 5 cards selected! Click 'Play Selected'",
                fg=COLORS['green']
            )
        else:
            self.selection_label.config(
                text=f"Selected {count} cards (5 for playing, any for discarding)",
                fg=COLORS['gold']
            )
        
        # Reset color if not highlighting
        if count != 5 or count == 0:
            self.selection_label.config(fg=COLORS['text'])
    
    def deal_cards(self):
        """Deal new cards"""
        if not self.game:
            return
        
        self.game.deal()
        self.display_cards()
        self.update_display()
        self.result_label.config(text=f"Dealt {len(self.game.current_pool)} cards. Select 5 to play!")
    
    def play_selected(self):
        """Play the selected cards"""
        if not self.game:
            return
        
        selected = self.get_selected_indices()
        
        if len(selected) != 5:
            messagebox.showwarning("Invalid Selection", "Please select exactly 5 cards to play.")
            return
        
        br, won, msg = self.game.play_indices(selected)
        
        if br:
            result_text = (
                f"🎯 Hand: {br.hand_name}\n"
                f"💎 Chips: {br.card_chips} (cards) + {br.base_chips} (base) + {br.bonus_chips} (bonus) = {br.total_chips}\n"
                f"✖️ Mult: {br.base_mult} (base) + {br.bonus_mult} (bonus) = {br.total_mult}\n"
                f"⭐ SCORE: {br.total_score:,}\n\n"
                f"{msg}"
            )
            self.result_label.config(text=result_text)
            
            if won and self.game.is_shop_available:
                self.result_label.config(
                    text=result_text + "\n\n💰 Shop is available! Click 'Shop' button."
                )
        else:
            self.result_label.config(text=msg)
        
        self.clear_cards()
        self.update_display()
    
    def auto_play(self):
        """Automatically select and play the best hand"""
        if not self.game or not self.game.current_pool:
            messagebox.showinfo("No Cards", "Deal cards first!")
            return
        
        picks = self.game.auto_pick()
        br, won, msg = self.game.play_indices(picks)
        
        if br:
            played_cards = [self.game.current_pool[i] for i in picks]
            result_text = (
                f"🤖 Auto-played: {format_cards(played_cards)}\n\n"
                f"🎯 Hand: {br.hand_name}\n"
                f"💎 Chips: {br.card_chips} + {br.base_chips} + {br.bonus_chips} = {br.total_chips}\n"
                f"✖️ Mult: {br.base_mult} + {br.bonus_mult} = {br.total_mult}\n"
                f"⭐ SCORE: {br.total_score:,}\n\n"
                f"{msg}"
            )
            self.result_label.config(text=result_text)
            
            if won and self.game.is_shop_available:
                self.result_label.config(
                    text=result_text + "\n\n💰 Shop is available! Click 'Shop' button."
                )
        else:
            self.result_label.config(text=msg)
        
        self.clear_cards()
        self.update_display()
    
    def discard_selected(self):
        """Discard selected cards and draw new ones"""
        if not self.game:
            return
        
        selected = self.get_selected_indices()
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select cards to discard.")
            return
        
        ok, msg = self.game.discard_and_draw(selected)
        
        if ok:
            self.display_cards()
            self.update_display()
            self.result_label.config(text=msg)
        else:
            messagebox.showerror("Cannot Discard", msg)
    
    def open_shop(self):
        """Open the shop window"""
        if not self.game:
            return
        
        ok, lines = self.game.open_shop()
        
        if not ok:
            messagebox.showinfo("Shop Closed", lines[0])
            return
        
        # Create shop window
        shop_window = tk.Toplevel(self.root)
        shop_window.title("🏪 Shop")
        shop_window.geometry("600x500")
        shop_window.configure(bg=COLORS['bg'])
        shop_window.transient(self.root)
        shop_window.grab_set()
        
        # Title
        title = tk.Label(
            shop_window,
            text=f"🏪 Shop (You have ${self.game.coins})",
            font=('Arial', 16, 'bold'),
            bg=COLORS['bg'],
            fg=COLORS['gold']
        )
        title.pack(pady=10)
        
        # Offers frame
        offers_frame = tk.Frame(shop_window, bg=COLORS['bg'])
        offers_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for i, line in enumerate(lines):
            # Parse the line
            parts = line.split(" - ")
            name_rarity = parts[0].split(". ")[1]
            cost_desc = parts[1].split(" :: ")
            cost = cost_desc[0]
            desc = cost_desc[1]
            
            # Create offer frame
            offer_frame = tk.Frame(offers_frame, bg=COLORS['card_bg'], relief=tk.RAISED, borderwidth=2)
            offer_frame.pack(fill=tk.X, pady=5)
            
            # Joker info
            info_frame = tk.Frame(offer_frame, bg=COLORS['card_bg'])
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            name_label = tk.Label(
                info_frame,
                text=name_rarity,
                font=('Arial', 12, 'bold'),
                bg=COLORS['card_bg'],
                fg=COLORS['gold'],
                anchor=tk.W
            )
            name_label.pack(fill=tk.X)
            
            desc_label = tk.Label(
                info_frame,
                text=desc,
                font=('Arial', 10),
                bg=COLORS['card_bg'],
                fg=COLORS['text'],
                wraplength=400,
                anchor=tk.W,
                justify=tk.LEFT
            )
            desc_label.pack(fill=tk.X, pady=(5, 0))
            
            # Buy button
            buy_btn = tk.Button(
                offer_frame,
                text=f"Buy\n{cost}",
                command=lambda idx=i: self.buy_joker(idx, shop_window),
                font=('Arial', 10, 'bold'),
                bg=COLORS['green'],
                fg='white',
                width=8,
                height=2,
                cursor='hand2'
            )
            buy_btn.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Skip button
        skip_btn = tk.Button(
            shop_window,
            text="Skip Shop",
            command=lambda: self.skip_shop(shop_window),
            font=('Arial', 12, 'bold'),
            bg=COLORS['red'],
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        skip_btn.pack(pady=10)
    
    def buy_joker(self, idx: int, shop_window: tk.Toplevel):
        """Buy a joker from the shop"""
        ok, msg = self.game.buy_from_shop(idx)
        
        if ok:
            messagebox.showinfo("Purchase Successful", msg)
            self.update_display()
            shop_window.destroy()
        else:
            messagebox.showerror("Purchase Failed", msg)
    
    def skip_shop(self, shop_window: tk.Toplevel):
        """Skip the shop"""
        self.game.close_shop()
        shop_window.destroy()
        self.result_label.config(text="Skipped shop. Continuing to next blind...")
        self.update_display()
    
    def save_game(self):
        """Save the game to a file"""
        if not self.game:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=Path.home() / ".pylatro" / "saves"
        )
        
        if filename:
            if self.game.save_to_file(filename):
                messagebox.showinfo("Save Successful", f"Game saved to:\n{filename}")
            else:
                messagebox.showerror("Save Failed", "Failed to save game.")
    
    def load_game(self):
        """Load a game from a file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=Path.home() / ".pylatro" / "saves"
        )
        
        if filename:
            loaded_game = GameState.load_from_file(filename)
            if loaded_game:
                self.game = loaded_game
                self.update_display()
                self.clear_cards()
                self.result_label.config(text=f"Game loaded from:\n{filename}")
                messagebox.showinfo("Load Successful", "Game loaded successfully!")
            else:
                messagebox.showerror("Load Failed", "Failed to load game.")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
🎮 HOW TO PLAY

1. Click 'Deal' to draw 8 cards
2. Select 5 cards by clicking them
3. Click 'Play Selected' to score your hand
4. Try to reach the target score before running out of hands!

💡 TIPS
• Use 'Auto Play' to let the game pick the best hand
• Discard unwanted cards to draw new ones
• Visit the shop after clearing blinds to buy jokers
• Jokers give you powerful bonuses!

🎯 OBJECTIVE
Beat all three blinds (Small, Big, Boss) to advance to the next Ante.
The difficulty increases with each Ante!

🃏 POKER HANDS (from lowest to highest)
High Card < Pair < Two Pair < Three of a Kind < Straight
< Flush < Full House < Four of a Kind < Straight Flush
        """
        
        messagebox.showinfo("How to Play", help_text)
    
    def show_stats(self):
        """Show game statistics"""
        if not self.game:
            messagebox.showinfo("Statistics", "No game in progress.")
            return
        
        stats = self.game.statistics()
        messagebox.showinfo("Game Statistics", stats)


def main():
    """Entry point for the GUI application"""
    root = tk.Tk()
    app = PyLatroGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()