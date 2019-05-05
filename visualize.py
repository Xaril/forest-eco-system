import arcade
import random
import ecosystem

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_WIDTH = 20
CELL_HEIGHT = 20

class Game(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        super().__init__(width, height)

        self.sprite_list = None

        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.sprite_list = arcade.SpriteList()

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        self.sprite_list.draw()


    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        self.sprite_list = arcade.SpriteList()

        #TODO: Apply ecosystem to visualization
        #ecosystem_state = ecosystem.run()
        #for cell in ecosystem...


def main():
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
