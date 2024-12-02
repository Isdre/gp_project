import random
from enum import Enum


class Operator(Enum):
    rotateAcLeft = 0,
    rotateBaLeft = 1,
    rotateAcRight = 2,
    rotateBaRight = 3,
    addDegree = 4,
    substractDegree = 5

class TinyGP:
    @staticmethod
    def __rotateAcLeft(x,y):
        return 0

    @staticmethod
    def __rotateBaLeft(x, y):
        return 0

    @staticmethod
    def __rotateAcRight(x, y):
        return 0

    @staticmethod
    def __rotateBaRight(x, y):
        return 0

    @staticmethod
    def __addDegree(x, y):
        return x + y

    @staticmethod
    def __substractDegree(x, y):
        return x - y

    def __init__(self):
        #parameters
        self.max_TTL = 60 #seconds
        self.random_variable_amount = 50
        self.random_variable_min = -5
        self.random_variable_max = 5
        self.max_depth = 10
        self.population_size = 100
        #-----------

        self.random_variable = [random.random() * (self.random_variable_max - self.random_variable_min) + self.random_variable_min for _ in range(self.random_variable_amount)]
        self.population = [self.create_random_individual() for _ in range(self.population_size)]

    def step(self):
        pass

    def calc_fitness(self):
        pass

    def create_random_individual(self):
        pass

    def mutation(self):
        pass

    def crossover(self):
        pass

    def tournament(self):
        pass

    def negative_tournament(self):
        pass