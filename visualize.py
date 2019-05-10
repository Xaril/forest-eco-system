import arcade
from ecosystem import Ecosystem
from organisms import Type
import matplotlib.pyplot as plt

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

        self.populations = {
            'rabbit': [],
            'bee': [],
            'fox': [],
            'flower': []
        }

        self.steps = 15000
        self.step = 0

        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.sprite_list = arcade.SpriteList()

        self.ecosystem = Ecosystem(int(SCREEN_WIDTH/CELL_WIDTH), int(SCREEN_HEIGHT/CELL_HEIGHT))

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        self.sprite_list.draw()

    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        if self.step < self.steps:
            self.step += 1

            self.sprite_list = arcade.SpriteList()

            ecosystem_organisms = self.ecosystem.run()
            rabbits = 0
            foxes = 0
            bees = 0
            flowers = 0

            for organism in ecosystem_organisms:
                sprite = arcade.Sprite(organism.get_image(), 1)
                sprite.center_x = organism.x * CELL_WIDTH + CELL_WIDTH/2
                sprite.center_y = organism.y * CELL_HEIGHT + CELL_HEIGHT/2
                self.sprite_list.append(sprite)

                # Observe animal populations
                if organism.type == Type.RABBIT:
                    rabbits += 1
                elif organism.type == Type.FOX:
                    foxes += 1
                elif organism.type == Type.BEE:
                    bees += 1
                elif organism.type == Type.FLOWER:
                    flowers += 1

            self.populations['rabbit'].append(rabbits)
            self.populations['fox'].append(foxes)
            self.populations['bee'].append(bees)
            self.populations['flower'].append(flowers)
        else:
            plt.plot(self.populations['rabbit'], label='Rabbits')
            plt.plot(self.populations['fox'], label='Foxes')
            plt.plot(self.populations['bee'], label='Bees')
            plt.plot(self.populations['flower'], label='Flowers')
            plt.xlabel('Time')
            plt.legend(loc='upper right')
            plt.ylabel('Population amount')
            plt.show()
            exit()




def main():
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
