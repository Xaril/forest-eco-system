from helpers import Direction
import random
from organisms import Type
from enum import Enum
import numpy as np

NUMBER_OF_RAINY_DAYS_IN_YEAR = 168

class RainType(Enum):
    LIGHT = {"probability": 0.75, "liter_per_hour": 0.1}
    MEDIUM = {"probability": 0.2, "liter_per_hour": 0.5}
    HEAVY = {"probability": 0.05, "liter_per_hour": 1}

class WindType(Enum):
    CALM = {"probability": 0.239, "speed": [0, 1], "direcion_change_probability": 0.4}
    BREEZE = {"probability": 0.75, "speed": [2,3], "direcion_change_probability": 0.3}
    GALE = {"probability": 0.01, "speed": [4,5,6], "direcion_change_probability": 0.1}
    STORM = {"probability": 0.001, "speed": [7,8,9,10] , "direcion_change_probability": 0}

class Weather():
    def __init__(self, ecosystem):
        self.__ecosystem = ecosystem
        self.__wind_velocity = (random.choice(list(Direction)), 1) # direciton and speed
        self.__hour = 0
        self.__is_rainy_day = False

    def get_wind_velocity(self):
        """Returns a tuple with wind diretion and speed"""
        return self.__wind_velocity

    def simulate_rain(self, type):
        for x in range(self.__ecosystem.width):
            for y in range(self.__ecosystem.height):
                if self.__ecosystem.plant_map[x][y] and (self.__ecosystem.plant_map[x][y].type == Type.EARTH or self.__ecosystem.plant_map[x][y].type == Type.GRASS):
                    self.__ecosystem.plant_map[x][y].water_amount += type.value['liter_per_hour']
                if self.__ecosystem.water_map[x][y]:
                    self.__ecosystem.water_map[x][y].water_amount += type.value['liter_per_hour']

    def simulate_weather(self):
        """Simulates weather changes and effects in one time step"""

        # Simulate rain
        self.__hour += 1
        self.__wind_velocity = (random.choice(list(Direction)), 2)

        if self.__hour == 24:
            self.__hour = 0
            self.__is_rainy_day = random.random() <= NUMBER_OF_RAINY_DAYS_IN_YEAR / 365

        if self.__is_rainy_day:
            if random.random() <= RainType.LIGHT.value["probability"]:
                self.simulate_rain(RainType.LIGHT)
            elif random.random() <= RainType.MEDIUM.value["probability"]:
                self.simulate_rain(RainType.MEDIUM)
            elif random.random() <= RainType.HEAVY.value["probability"]:
                self.simulate_rain(RainType.HEAVY)

        wind = np.random.choice(list(WindType), p=[type.value['probability'] for type in list(WindType)])
        wind_speed = random.choice(wind.value['speed'])
        wind_direciton = self.get_wind_velocity()[0]
        if random.random() <= wind.value['direcion_change_probability']:
            wind_direciton = random.choice(list(Direction))
        self.__wind_velocity = (wind_direciton, wind_speed)
        return
