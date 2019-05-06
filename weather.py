from helpers import Direction
import random

class Weather():
    def __init__(self, ecosystem):
        self.__ecosystem = ecosystem
        self.__wind_velocity = (random.choice(list(Direction)), 1) # direciton and speed

    def get_wind_velocity(self):
        """Returns a tuple with wind dicetions and speed"""
        return self.__wind_velocity

    def simulate_weather(self):
        """Simulates weather changes and effects in one time step"""
        return
