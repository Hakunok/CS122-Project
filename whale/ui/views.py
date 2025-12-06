from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional, List

import arcade

from ui.layout import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BACKGROUND_COLOR,
    DICE_SPACING,
    DICE_SIZE,
    FONT_NAME,
)
from core.game_state import GameEngine
from core.dice import DieState
from core.shop import ShopItem
from core.save import save_run, load_run, has_save, clear_save
from config.angles import ANGLES

CASINO_PURPLE_DARK = (10, 4, 24, 255)
CASINO_PURPLE_MED = (20, 10, 46, 255)
CASINO_PURPLE_LIGHT = (32, 16, 70, 255)

SOFT_GOLD = (238, 204, 120, 255)
SOFT_GOLD_DIM = (190, 160, 90, 255)

NEON_TEAL_SOFT = (120, 210, 230, 255)

NEON_MAGENTA = (255, 105, 210, 255)

OFF_WHITE = (244, 238, 255, 255)
TEXT_STRONG = OFF_WHITE
TEXT_SUBTLE = (176, 170, 214, 255)
TEXT_MUTED = (132, 124, 170, 255)

DICE_BG_LIGHT = (58, 50, 100, 255)
DICE_BG_LOCKED = (74, 60, 112, 255)
DICE_BORDER_NORMAL = (200, 190, 240, 255)
DICE_BORDER_LOCKED = SOFT_GOLD
DICE_VALUE_COLOR = (248, 244, 255, 255)

BUTTON_FILL = CASINO_PURPLE_LIGHT
BUTTON_BORDER = NEON_TEAL_SOFT
BUTTON_FILL_DISABLED = (55, 45, 80, 255)
BUTTON_BORDER_DISABLED = (90, 80, 120, 255)
BUTTON_TEXT = OFF_WHITE
BUTTON_TEXT_DISABLED = TEXT_SUBTLE

LEFT_PANEL_WIDTH = 260
MARGIN = 20
ANGLES_HEIGHT = 150
DICE_AREA_HEIGHT = 280
BOTTOM_BAR_Y = 72

NF_CLUB = "♣"
NF_DIAMOND = "♦"
NF_SPADE = "♠"
NF_HEART = "❤"

SUIT_SYMBOL = {
    "SPADE": NF_SPADE,
    "HEART": NF_HEART,
    "DIAMOND": NF_DIAMOND,
    "CLUB": NF_CLUB,
}

SUIT_COLOR = {
    "SPADE": (190, 195, 220, 255),
    "CLUB":  (190, 195, 220, 255),
    "HEART": arcade.color.RED,
    "DIAMOND": arcade.color.RED,
}

@dataclass
class RectButton:
    center_x: float
    center_y: float
    width: float
    height: float
    label: str
    enabled: bool = True
    visible: bool = True

    def draw(self):
        if not self.visible:
            return

        left = self.center_x - self.width / 2
        bottom = self.center_y - self.height / 2

        if self.enabled:
            fill_color = BUTTON_FILL
            border_color = BUTTON_BORDER
            text_color = BUTTON_TEXT
        else:
            fill_color = BUTTON_FILL_DISABLED
            border_color = BUTTON_BORDER_DISABLED
            text_color = BUTTON_TEXT_DISABLED

        arcade.draw_lbwh_rectangle_filled(left, bottom, self.width, self.height, fill_color)
        arcade.draw_lbwh_rectangle_outline(
            left, bottom, self.width, self.height, border_color, border_width=2
        )

        text_obj = arcade.Text(
            self.label,
            self.center_x,
            self.center_y,
            text_color,
            font_size=16,
            anchor_x="center",
            anchor_y="center",
            font_name=FONT_NAME,
        )
        text_obj.draw()

    def hit_test(self, x: float, y: float) -> bool:
        if not (self.visible and self.enabled):
            return False
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2
        return left <= x <= right and bottom <= y <= top


class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.title_text: Optional[arcade.Text] = None
        self.buttons: List[RectButton] = []
        self.info_text: Optional[arcade.Text] = None
        self._has_save: bool = False

    def on_show_view(self):
        arcade.set_background_color(BACKGROUND_COLOR)
        cx = WINDOW_WIDTH / 2

        self._has_save = has_save()

        self.title_text = arcade.Text(
            "Whale",
            cx,
            WINDOW_HEIGHT * 0.65,
            TEXT_STRONG,
            font_size=48,
            anchor_x="center",
            font_name=FONT_NAME,
        )

        btn_w, btn_h, gap = 220, 42, 16
        start_y = WINDOW_HEIGHT * 0.45

        self.buttons = [
            RectButton(cx, start_y, btn_w, btn_h, "New Run"),
            RectButton(cx, start_y - (btn_h + gap), btn_w, btn_h, "Seeded Run"),
            RectButton(
                cx,
                start_y - 2 * (btn_h + gap),
                btn_w,
                btn_h,
                "Continue Run",
                enabled=self._has_save,
            ),
        ]

    def on_draw(self):
        self.clear()
        if self.title_text:
            self.title_text.draw()
        for btn in self.buttons:
            btn.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.buttons[0].hit_test(x, y):
            game_view = GameView()
            self.window.show_view(game_view)
        elif self.buttons[1].hit_test(x, y):
            game_view = GameView()
            self.window.show_view(game_view)
        elif self.buttons[2].hit_test(x, y):
            # continue run from saved state
            engine = load_run()
            if engine is not None:
                game_view = GameView(engine)
                self.window.show_view(game_view)
            else:
                # save unreadable
                self.on_show_view()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ENTER:
            game_view = GameView()
            self.window.show_view(game_view)


class GameView(arcade.View):
    """
    Arcade layer that talks to GameEngine.
    """

    def __init__(self, engine: Optional[GameEngine] = None):
        super().__init__()

        # when no rng passed start new run
        self.rng = random.Random()
        if engine is None:
            self.engine = GameEngine(self.rng)
            # fresh run starts new pot
            self.engine.start_pot()
        else:
            # continuing saved run
            self.engine = engine

        self.mode: str = "playing" 

        self.last_hand_label: str = ""
        self.last_hand_equation: str = ""

        self.popup_message: Optional[str] = None

        right_x = LEFT_PANEL_WIDTH + MARGIN * 2
        right_width = WINDOW_WIDTH - right_x - MARGIN
        right_center_x = right_x + right_width / 2

        btn_w = 210
        btn_h = 42
        gap = 60

        left_x = right_center_x - (btn_w + gap) / 2
        right_x_btn = right_center_x + (btn_w + gap) / 2

        self.roll_button = RectButton(left_x, BOTTOM_BAR_Y, btn_w, btn_h, "Roll")
        self.submit_button = RectButton(right_x_btn, BOTTOM_BAR_Y, btn_w, btn_h, "Submit")

        self.visit_shop_button = RectButton(left_x, BOTTOM_BAR_Y, btn_w, btn_h, "Visit Shop", visible=False)
        self.next_pot_button = RectButton(right_x_btn, BOTTOM_BAR_Y, btn_w, btn_h, "Next Pot", visible=False)

        self.main_menu_button = RectButton(left_x, BOTTOM_BAR_Y, btn_w, btn_h, "Main Menu", visible=False)
        self.new_run_button = RectButton(right_x_btn, BOTTOM_BAR_Y, btn_w, btn_h, "New Run", visible=False)

        # new run / save and quit buttons
        # bottom of left bar
        side_btn_w, side_btn_h, side_gap = 170, 38, 10
        side_x = MARGIN + LEFT_PANEL_WIDTH / 2
        side_start_y = BOTTOM_BAR_Y + 20

        self.side_new_run_button = RectButton(
            side_x, side_start_y + side_btn_h + side_gap, side_btn_w, side_btn_h, "New Run"
        )
        self.side_save_button = RectButton(
            side_x, side_start_y, side_btn_w, side_btn_h, "Save and Quit"
        )

        self._set_playing_buttons()

    def on_show_view(self):
        arcade.set_background_color(BACKGROUND_COLOR)


    def _die_bounds(self, index: int):
        ps = self.engine.state.pot_state

        # play pane dimensions
        right_x = LEFT_PANEL_WIDTH + MARGIN * 2
        right_width = WINDOW_WIDTH - right_x - MARGIN

        # dice area
        dice_bottom = MARGIN + 110
        dice_top = dice_bottom + DICE_AREA_HEIGHT
        dice_center_y = (dice_bottom + dice_top) / 2

        # width of playable area
        available_width = right_width
        line_width = (len(ps.dice_states) - 1) * DICE_SPACING
        start_cx = right_x + (available_width - line_width) / 2

        x = start_cx + index * DICE_SPACING
        y = dice_center_y
        half = DICE_SIZE / 2
        return x, y, half, half

    def _hit_test_die(self, x: float, y: float) -> Optional[int]:
        ps = self.engine.state.pot_state
        for i in range(len(ps.dice_states)):
            cx, cy, hw, hh = self._die_bounds(i)
            if (cx - hw) <= x <= (cx + hw) and (cy - hh) <= y <= (cy + hh):
                return i
        return None


    def on_draw(self):
        self.clear()

        s = self.engine.state
        ps = s.pot_state

        # left sidebar
        arcade.draw_lbwh_rectangle_filled(
            MARGIN,
            MARGIN,
            LEFT_PANEL_WIDTH,
            WINDOW_HEIGHT - 2 * MARGIN,
            CASINO_PURPLE_DARK,
        )

        # pot info, content left sidebar
        left_x = MARGIN + 16
        top_y = WINDOW_HEIGHT - MARGIN - 28
        line_h = 26

        arcade.Text(
            f"Floor {s.floor}, Pot {s.pot_in_floor}",
            left_x,
            top_y,
            TEXT_STRONG,
            font_size=20,
            anchor_x="left",
            font_name=FONT_NAME,
        ).draw()

        pot_name = s.boss_rule.name if s.boss_rule is not None else "Standard Pot"
        pot_desc = s.boss_rule.description if s.boss_rule is not None else "No special house rules."

        arcade.Text(
            pot_name,
            left_x,
            top_y - line_h * 2,
            TEXT_STRONG,
            font_size=16,
            anchor_x="left",
            font_name=FONT_NAME,
        ).draw()

        arcade.Text(
            pot_desc,
            left_x,
            top_y - line_h * 3,
            TEXT_MUTED,
            font_size=11,
            anchor_x="left",
            font_name=FONT_NAME,
            multiline=True,
            width=LEFT_PANEL_WIDTH - 32,
        ).draw()

        arcade.Text(
            f"Need: {ps.pot_target}",
            left_x,
            top_y - line_h * 5,
            SOFT_GOLD,
            font_size=16,
            anchor_x="left",
            font_name=FONT_NAME,
        ).draw()

        arcade.Text(
            f"Heat: {ps.pot_heat}",
            left_x,
            top_y - line_h * 6,
            TEXT_STRONG,
            font_size=16,
            anchor_x="left",
            font_name=FONT_NAME,
        ).draw()

        if self.last_hand_label:
            arcade.Text(
                f"Last Hand: {self.last_hand_label}",
                left_x,
                top_y - line_h * 8,
                TEXT_SUBTLE,
                font_size=13,
                anchor_x="left",
                font_name=FONT_NAME,
                multiline=True,
                width=LEFT_PANEL_WIDTH - 32,
            ).draw()

            if self.last_hand_equation:
                arcade.Text(
                    self.last_hand_equation,
                    left_x + 8,
                    top_y - line_h * 9.5,
                    TEXT_MUTED,
                    font_size=11,
                    anchor_x="left",
                    font_name=FONT_NAME,
                    multiline=True,
                    width=LEFT_PANEL_WIDTH - 40,
                ).draw()

        arcade.Text(
            f"Chips: {s.chips}",
            left_x,
            top_y - line_h * 12,
            SOFT_GOLD,
            font_size=16,
            anchor_x="left",
            font_name=FONT_NAME,
        ).draw()

        self.side_new_run_button.draw()
        self.side_save_button.draw()

        # playing area (dice area)
        right_x = LEFT_PANEL_WIDTH + MARGIN * 2
        right_width = WINDOW_WIDTH - right_x - MARGIN

        # angles box
        # todo show owned angles info
        angles_bottom = WINDOW_HEIGHT - MARGIN - ANGLES_HEIGHT
        arcade.draw_lbwh_rectangle_filled(
            right_x,
            angles_bottom,
            right_width,
            ANGLES_HEIGHT,
            CASINO_PURPLE_MED,
        )
        arcade.draw_lbwh_rectangle_outline(
            right_x,
            angles_bottom,
            right_width,
            ANGLES_HEIGHT,
            TEXT_MUTED,
            border_width=2,
        )

        arcade.Text(
            "Angles",
            right_x + 16,
            angles_bottom + ANGLES_HEIGHT - 34,
            TEXT_STRONG,
            font_size=20,
            anchor_x="left",
            font_name=FONT_NAME,
        ).draw()
        arcade.Text(
            f"{s.angles_count}/{s.max_angles}",
            right_x + right_width - 16,
            angles_bottom + ANGLES_HEIGHT - 34,
            TEXT_SUBTLE,
            font_size=14,
            anchor_x="right",
            font_name=FONT_NAME,
        ).draw()

        if self.mode in ("pot_cleared", "busted"):
            label = "Pot Cleared!" if self.mode == "pot_cleared" else "Busted!"
            bg = (90, 160, 100, 255) if self.mode == "pot_cleared" else (160, 60, 80, 255)
            border = (160, 240, 180, 255) if self.mode == "pot_cleared" else (255, 140, 160, 255)
            text_color = OFF_WHITE

            pill_w, pill_h = 220, 48
            pill_cx = right_x + right_width / 2
            pill_cy = angles_bottom + ANGLES_HEIGHT / 2

            arcade.draw_lbwh_rectangle_filled(
                pill_cx - pill_w / 2,
                pill_cy - pill_h / 2,
                pill_w,
                pill_h,
                bg,
            )
            arcade.draw_lbwh_rectangle_outline(
                pill_cx - pill_w / 2,
                pill_cy - pill_h / 2,
                pill_w,
                pill_h,
                border,
                border_width=3,
            )
            arcade.Text(
                label,
                pill_cx,
                pill_cy,
                text_color,
                font_size=20,
                anchor_x="center",
                anchor_y="center",
                font_name=FONT_NAME,
            ).draw()

        # dice area box
        dice_bottom = MARGIN + 110
        arcade.draw_lbwh_rectangle_filled(
            right_x,
            dice_bottom,
            right_width,
            DICE_AREA_HEIGHT,
            CASINO_PURPLE_MED,
        )
        arcade.draw_lbwh_rectangle_outline(
            right_x,
            dice_bottom,
            right_width,
            DICE_AREA_HEIGHT,
            TEXT_MUTED,
            border_width=2,
        )

        hand_label_y = dice_bottom + DICE_AREA_HEIGHT - 34
        arcade.Text(
            f"Hand {ps.current_hand_index + 1}/{ps.hands_per_pot}",
            right_x + 16,
            hand_label_y,
            TEXT_SUBTLE,
            font_size=14,
            anchor_x="left",
            font_name=FONT_NAME,
        ).draw()
        arcade.Text(
            f"Rerolls {ps.rerolls_left}/{ps.base_rerolls}",
            right_x + right_width - 16,
            hand_label_y,
            TEXT_SUBTLE,
            font_size=14,
            anchor_x="right",
            font_name=FONT_NAME,
        ).draw()

        for i, ds in enumerate(ps.dice_states):
            self._draw_die(i, ds)

        # buttons onthe bottom of the dice area
        # roll/submit/visit_shop/next_pot/main menu/new run
        self.roll_button.draw()
        self.submit_button.draw()
        self.visit_shop_button.draw()
        self.next_pot_button.draw()
        self.main_menu_button.draw()
        self.new_run_button.draw()

        if self.popup_message:
            self._draw_popup(self.popup_message)

    def _draw_die(self, index: int, ds: DieState):
        cx, cy, hw, hh = self._die_bounds(index)

        if ds.locked:
            bg_color = DICE_BG_LOCKED
            border_color = DICE_BORDER_LOCKED
        else:
            bg_color = DICE_BG_LIGHT
            border_color = DICE_BORDER_NORMAL

        left = cx - hw
        bottom = cy - hh
        width = hw * 2
        height = hh * 2

        arcade.draw_lbwh_rectangle_filled(left, bottom, width, height, bg_color)
        arcade.draw_lbwh_rectangle_outline(
            left, bottom, width, height, border_color, border_width=3
        )

        face = ds.current_face
        v = face.base_value
        if v == 1:
            rank = "A"
        elif v == 11:
            rank = "J"
        elif v == 12:
            rank = "Q"
        elif v == 13:
            rank = "K"
        else:
            rank = str(v)

        rank_text = arcade.Text(
            rank,
            cx,
            cy + 10,
            DICE_VALUE_COLOR,
            font_size=24,
            anchor_x="center",
            anchor_y="center",
            font_name=FONT_NAME,
        )
        rank_text.draw()

        if face.suit is not None:
            suit_char = SUIT_SYMBOL.get(face.suit, "")
            suit_color = SUIT_COLOR.get(face.suit, TEXT_SUBTLE)

            suit_text = arcade.Text(
                suit_char,
                cx,
                cy - 20,
                suit_color,
                font_size=14,
                anchor_x="center",
                anchor_y="center",
                font_name=FONT_NAME,
            )
            suit_text.draw()

    def _draw_popup(self, text: str):
        box_w, box_h = 420, 80
        cx = WINDOW_WIDTH / 2
        cy = WINDOW_HEIGHT / 2 + 60

        arcade.draw_lbwh_rectangle_filled(
            cx - box_w / 2,
            cy - box_h / 2,
            box_w,
            box_h,
            CASINO_PURPLE_MED,
        )
        arcade.draw_lbwh_rectangle_outline(
            cx - box_w / 2,
            cy - box_h / 2,
            box_w,
            box_h,
            NEON_TEAL_SOFT,
            border_width=2,
        )
        arcade.Text(
            text,
            cx,
            cy,
            TEXT_STRONG,
            font_size=16,
            anchor_x="center",
            anchor_y="center",
            font_name=FONT_NAME,
            multiline=True,
            width=box_w - 32,
        ).draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.popup_message:
            self.popup_message = None
            return

        if self.side_new_run_button.hit_test(x, y):
            # starting a brand new run
            new_game = GameView()
            self.window.show_view(new_game)
            return

        if self.side_save_button.hit_test(x, y):
            try:
                save_run(self.engine)
                menu = MainMenuView()
                self.window.show_view(menu)
            except Exception as e:
                self.popup_message = f"Failed to save run: {e}"
            return

        if self.mode == "playing":
            if self.roll_button.hit_test(x, y):
                self._handle_roll()
                return
            if self.submit_button.hit_test(x, y):
                self._handle_submit()
                return

            idx = self._hit_test_die(x, y)
            if idx is not None:
                self.engine.toggle_lock(idx)

        elif self.mode == "pot_cleared":
            if self.visit_shop_button.hit_test(x, y):
                self._open_shop()
                return
            if self.next_pot_button.hit_test(x, y):
                self._advance_to_next_pot()
                return

        elif self.mode == "busted":
            if self.main_menu_button.hit_test(x, y):
                menu = MainMenuView()
                self.window.show_view(menu)
                return
            if self.new_run_button.hit_test(x, y):
                new_game = GameView()
                self.window.show_view(new_game)
                return

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            menu = MainMenuView()
            self.window.show_view(menu)

    # button handlers
    def _handle_roll(self):
        if self.mode != "playing":
            return
        changed = self.engine.roll()
        if not changed:
            self.popup_message = "No rerolls left this hand."

    def _handle_submit(self):
        if self.mode != "playing":
            return

        outcome = self.engine.submit_hand()
        result = outcome.result

        self.last_hand_label = f"{result.hand_def.name} ({result.total_heat} Heat)"
        sum_expr = "+".join(str(v) for v in result.sum_values)
        self.last_hand_equation = (
            f"({sum_expr}) + {result.base_heat_bonus} × {result.base_mult:.2f} = {result.total_heat} Heat"
        )
        self.popup_message = None

        if outcome.pot_cleared:
            self._enter_pot_cleared_state()
        elif outcome.pot_failed:
            self._enter_busted_state()
        else:
            pass

    def _set_playing_buttons(self):
        self.mode = "playing"
        self.roll_button.visible = True
        self.roll_button.enabled = True
        self.submit_button.visible = True
        self.submit_button.enabled = True

        self.visit_shop_button.visible = False
        self.next_pot_button.visible = False
        self.main_menu_button.visible = False
        self.new_run_button.visible = False

    def _enter_pot_cleared_state(self) -> None:
        self.mode = "pot_cleared"

        self.roll_button.visible = False
        self.submit_button.visible = False

        self.visit_shop_button.visible = True
        self.visit_shop_button.enabled = True
        self.next_pot_button.visible = True
        self.next_pot_button.enabled = True

        self.main_menu_button.visible = False
        self.new_run_button.visible = False

    def _enter_busted_state(self) -> None:
        self.mode = "busted"

        self.roll_button.visible = False
        self.submit_button.visible = False
        self.visit_shop_button.visible = False
        self.next_pot_button.visible = False

        self.main_menu_button.visible = True
        self.main_menu_button.enabled = True
        self.new_run_button.visible = True
        self.new_run_button.enabled = True

    def _advance_to_next_pot(self) -> None:
        self.engine.advance_to_next_pot()
        self.last_hand_label = ""
        self.last_hand_equation = ""
        self.popup_message = None
        self._set_playing_buttons()

    def _open_shop(self):
        shop_view = ShopView(self.engine, self)
        self.window.show_view(shop_view)


class ShopView(arcade.View):
    def __init__(self, engine: GameEngine, return_view: GameView):
        super().__init__()
        self.engine = engine
        self.return_view = return_view

        self.items: List[ShopItem] = []
        self.item_buttons: List[RectButton] = []
        self.exit_button: Optional[RectButton] = None

        self.message: Optional[str] = None

    def on_show_view(self):
        arcade.set_background_color(BACKGROUND_COLOR)
        self.items = self.engine.get_shop_items()
        self._build_buttons()

    def _build_buttons(self):
        self.item_buttons = []

        panel_w = WINDOW_WIDTH * 0.75
        panel_h = WINDOW_HEIGHT * 0.7
        panel_cx = WINDOW_WIDTH / 2
        panel_cy = WINDOW_HEIGHT / 2

        card_w = 220
        card_h = 260
        gap = 40

        total_cards_w = len(self.items) * card_w + (len(self.items) - 1) * gap if self.items else 0
        start_x = panel_cx - total_cards_w / 2
        card_bottom = panel_cy - card_h / 2 + 20

        for i, item in enumerate(self.items):
            center_x = start_x + i * (card_w + gap) + card_w / 2
            btn = RectButton(
                center_x=center_x,
                center_y=card_bottom + 26,
                width=card_w * 0.7,
                height=34,
                label="Purchased" if item.purchased else "Purchase",
                enabled=not item.purchased,
                visible=True,
            )
            self.item_buttons.append(btn)

        exit_btn_w, exit_btn_h = 170, 40
        self.exit_button = RectButton(
            center_x=panel_cx,
            center_y=panel_cy - panel_h / 2 + 40,
            width=exit_btn_w,
            height=exit_btn_h,
            label="Exit Shop",
        )

    def on_draw(self):
        self.clear()

        arcade.draw_lbwh_rectangle_filled(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (0, 0, 0, 160)
        )

        panel_w = WINDOW_WIDTH * 0.75
        panel_h = WINDOW_HEIGHT * 0.7
        panel_cx = WINDOW_WIDTH / 2
        panel_cy = WINDOW_HEIGHT / 2

        panel_left = panel_cx - panel_w / 2
        panel_bottom = panel_cy - panel_h / 2

        arcade.draw_lbwh_rectangle_filled(
            panel_left,
            panel_bottom,
            panel_w,
            panel_h,
            CASINO_PURPLE_DARK,
        )
        arcade.draw_lbwh_rectangle_outline(
            panel_left,
            panel_bottom,
            panel_w,
            panel_h,
            NEON_TEAL_SOFT,
            border_width=3,
        )

        arcade.Text(
            "Shop Offers",
            panel_cx,
            panel_bottom + panel_h - 50,
            TEXT_STRONG,
            font_size=28,
            anchor_x="center",
            font_name=FONT_NAME,
        ).draw()

        card_w = 220
        card_h = 260
        gap = 40
        total_cards_w = len(self.items) * card_w + (len(self.items) - 1) * gap if self.items else 0
        start_x = panel_cx - total_cards_w / 2
        card_bottom = panel_cy - card_h / 2 + 20

        for i, item in enumerate(self.items):
            cx = start_x + i * (card_w + gap) + card_w / 2
            left = cx - card_w / 2
            bottom = card_bottom
            top = bottom + card_h

            arcade.draw_lbwh_rectangle_filled(
                left,
                bottom,
                card_w,
                card_h,
                CASINO_PURPLE_MED,
            )
            arcade.draw_lbwh_rectangle_outline(
                left,
                bottom,
                card_w,
                card_h,
                TEXT_MUTED,
                border_width=2,
            )

            kind_label = "Angle" if item.is_angle else "Edge"
            arcade.Text(
                kind_label,
                cx,
                top + 18,
                TEXT_STRONG,
                font_size=16,
                anchor_x="center",
                anchor_y="center",
                font_name=FONT_NAME,
            ).draw()

            # name of item
            name_top_y = top - 20
            name_text = arcade.Text(
                item.name,
                cx,
                name_top_y,
                SOFT_GOLD,
                font_size=16,
                anchor_x="center",
                anchor_y="top",
                font_name=FONT_NAME,
                multiline=True,
                width=card_w - 24,
            )
            name_text.draw()

            # cost
            cost_y = name_top_y - name_text.content_height - 8
            cost_text = arcade.Text(
                f"Cost: {item.cost}",
                cx,
                cost_y,
                TEXT_SUBTLE,
                font_size=13,
                anchor_x="center",
                anchor_y="top",
                font_name=FONT_NAME,
            )
            cost_text.draw()

            # description
            desc_y = bottom + 150
            arcade.Text(
                item.description,
                left + 12,
                desc_y,
                TEXT_MUTED,
                font_size=11,
                anchor_x="left",
                font_name=FONT_NAME,
                multiline=True,
                width=card_w - 24,
            ).draw()

            # purchase/purchased
            self.item_buttons[i].draw()

        if self.exit_button:
            self.exit_button.draw()

        if self.message:
            msg_w, msg_h = panel_w - 60, 70
            mx = panel_cx
            my = panel_bottom + 80
            arcade.draw_lbwh_rectangle_filled(
                mx - msg_w / 2,
                my - msg_h / 2,
                msg_w,
                msg_h,
                CASINO_PURPLE_MED,
            )
            arcade.draw_lbwh_rectangle_outline(
                mx - msg_w / 2,
                my - msg_h / 2,
                msg_w,
                msg_h,
                NEON_TEAL_SOFT,
                border_width=2,
            )
            arcade.Text(
                self.message,
                mx,
                my,
                TEXT_STRONG,
                font_size=14,
                anchor_x="center",
                anchor_y="center",
                font_name=FONT_NAME,
                multiline=True,
                width=msg_w - 24,
            ).draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.message:
            self.message = None
            return

        for i, btn in enumerate(self.item_buttons):
            if btn.hit_test(x, y):
                success, msg = self.engine.buy_shop_item(i)
                self.message = msg
                self.items = self.engine.get_shop_items()
                self._build_buttons()
                return

        if self.exit_button and self.exit_button.hit_test(x, y):
            self.window.show_view(self.return_view)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.return_view)
