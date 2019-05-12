from helpers import Direction
import random
from organisms import Type
from enum import Enum

NUMBER_OF_RAINY_DAYS_IN_YEAR = 168

class RainType(Enum):
    LIGHT = {"probability": 0.75, "liter_per_hour": 0.1}
    MEDIUM = {"probability": 0.2, "liter_per_hour": 0.5}
    HEAVY = {"probability": 0.05, "liter_per_hour": 1}

class Weather():
    def __init__(self, ecosystem):
        self.__ecosystem = ecosystem
        self.__wind_velocity = (random.choice(list(Direction)), 2) # direciton and speed
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
        self.__hour += 1
        self.__wind_velocity = (random.choice(list(Direction)), 10)

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
        return
