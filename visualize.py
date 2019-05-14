import arcade
from ecosystem import Ecosystem
from organisms import Type
import matplotlib.pyplot as plt
import argparse

SCREEN_WIDTH = 1200
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

    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        self.sprite_list = arcade.SpriteList()

        ecosystem_organisms = self.ecosystem.run()

        for organism in ecosystem_organisms:
            sprite = arcade.Sprite(organism.get_image(), 1)
            sprite.center_x = organism.x * CELL_WIDTH + CELL_WIDTH/2
            sprite.center_y = organism.y * CELL_HEIGHT + CELL_HEIGHT/2
            self.sprite_list.append(sprite)


def plot(steps):
    populations = {
        'rabbit': [],
        'bee': [],
        'fox': [],
        'flower': [],
        'grass': []
    }

    genetics_factors = {
        'rabbit': [],
        'fox': []
    }

    ecosystem = Ecosystem(int(SCREEN_WIDTH/CELL_WIDTH), int(SCREEN_HEIGHT/CELL_HEIGHT))

    # Iterate over time
    for i in range(steps):
        ecosystem_organisms = ecosystem.run()

        rabbits = 0
        foxes = 0
        bees = 0
        flowers = 0
        grass = 0

        rabbit_genetics_factor = 0
        fox_genetics_factor = 0

        for organism in ecosystem_organisms:
            # Observe animal populations
            if organism.type == Type.RABBIT:
                rabbits += 1
                rabbit_genetics_factor += organism.genetics_factor
            elif organism.type == Type.FOX:
                foxes += 1
                fox_genetics_factor += organism.genetics_factor
            elif organism.type == Type.BEE:
                bees += 1
            elif organism.type == Type.FLOWER:
                flowers += 1
            elif organism.type == Type.GRASS:
                grass += 1

        populations['rabbit'].append(rabbits)
        populations['fox'].append(foxes)
        populations['bee'].append(bees)
        populations['flower'].append(flowers)
        populations['grass'].append(grass)

        if not i % 100:
            print('Iteration %d: %d foxes left, %d rabbits left.' % (i, foxes, rabbits))

        if rabbits != 0:
            genetics_factors['rabbit'].append(rabbit_genetics_factor / rabbits)
        if foxes != 0:
            genetics_factors['fox'].append(fox_genetics_factor / foxes)

    # Plot the results
    plt.plot(populations['rabbit'], label='Rabbits')
    plt.plot(populations['fox'], label='Foxes')
    plt.plot(populations['bee'], label='Bees')
    plt.plot(populations['flower'], label='Flowers')
    plt.plot(populations['grass'], label='Grass')
    plt.xlabel('Time')
    plt.legend(loc='upper right')
    plt.ylabel('Population amount')
    plt.show()

    plt.plot(genetics_factors['rabbit'], label='Rabbits')
    plt.plot(genetics_factors['fox'], label='Foxes')
    plt.xlabel('Time')
    plt.legend(loc='upper right')
    plt.ylabel('Genetics factor')
    plt.show()


def main():

    parser = argparse.ArgumentParser(description='Simulates an ecosystem.')
    parser.add_argument(
        '--plot',
        dest='plot',
        help='Plot the population amount after a set amount of time steps instead ' +
        'of visualizing it (default False).',
        action='store_true'
    )
    parser.add_argument(
        '--steps',
        dest='steps',
        help='The number of steps to simulate for (if --plot is set). Default 100.',
        type=int,
        default=100
    )

    args = parser.parse_args()

    if args.plot:
        plot(args.steps)
    else:
        game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
        game.setup()
        arcade.run()


if __name__ == "__main__":
    main()
