import arcade

from ui.layout import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FONT_PATH
from ui.views import MainMenuView


def main():
    arcade.load_font(FONT_PATH)
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    menu_view = MainMenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()

