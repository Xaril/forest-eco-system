import arcade
from ecosystem import Ecosystem

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_WIDTH = 20
CELL_HEIGHT = 20

class Game(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        super().__init__(width, height, 'Ecosystem Simulation')

        self.sprite_list = None

        self.ecosystem = None

        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.sprite_list = arcade.SpriteList()

        self.ecosystem = Ecosystem(int(SCREEN_WIDTH/CELL_WIDTH), int(SCREEN_HEIGHT/CELL_HEIGHT))

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        self.sprite_list.draw()
        #arcade.finish_render()

    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        self.sprite_list = arcade.SpriteList()

        ecosystem_organisms = self.ecosystem.run()
        for organism in ecosystem_organisms:
            sprite = arcade.Sprite(organism.get_image(), 1)
            sprite.center_x = organism.x * CELL_WIDTH + CELL_WIDTH/2
            sprite.center_y = organism.y * CELL_HEIGHT + CELL_HEIGHT/2
            self.sprite_list.append(sprite)


def main():
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
