import arcade

from ui.layout import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
from ui.views import MainMenuView


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    menu_view = MainMenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()

