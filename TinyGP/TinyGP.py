import random
from enum import IntEnum
from Individual.Individual import Individual,Node

class OperatorGP(IntEnum):
    Variable = 0,
    Constant = 1,
    RotateAcLeft = 2,
    RotateBaLeft = 3,
    RotateAcRight = 4,
    RotateBaRight = 5,
    AddDegree = 6,
    SubstractDegree = 7

class TinyGP:
    # parameters
    enum_max = 7
    max_TTL = 60  # seconds
    random_const_amount = 50
    random_const_min = -5
    random_const_max = 5
    max_depth = 10
    population_size = 10

    # -----------

    def __init__(self,space,ground_y,fps):
        self.space = space
        self.ground_y = ground_y
        self.fps = fps

        #-----------
        self.best_ind = None
        self.best_fitness = 0
        self.random_consts = [random.random() * (TinyGP.random_const_max - TinyGP.random_const_min) + self.random_const_min for _ in range(self.random_const_amount)]
        self.population = [self.create_random_individual() for _ in range(TinyGP.population_size)]

    def step(self):
        for ind in self.population:
            f = float(ind.brain)

    def calc_fitness(self):
        for ind in self.population:
            bonus = 1
            if (ind.getSpread(0,0) < 0 and ind.crossed_legs) or (ind.getSpread(0,0) > 0 and not ind.crossed_legs):
                bonus = 1.5
            ind.fitness += (ind.getDistance() - ind.previous_distance) * bonus / self.fps
            ind.previous_distance = ind.getDistance()

    #full grow
    def __create_random_tree(self,body:Individual,depth:int) -> Node:
        node = Node()

        op = random.randint(2,TinyGP.enum_max)

        if depth == 0:
            op = random.randint(0, 1)
        else:
            node.left = self.__create_random_tree(body, depth - 1)
            node.right = self.__create_random_tree(body, depth - 1)
            
        match OperatorGP(op):
            case OperatorGP.Variable:
                v = random.randint(0,1)
                if v == 0:
                    node.func = body.getHeight
                else:
                    node.func = body.getSpread
            case OperatorGP.Constant:
                node.left = random.choice(self.random_consts)
            case OperatorGP.RotateAcLeft:
                node.func = body.rotateAcLeft
            case OperatorGP.RotateBaLeft:
                node.func = body.rotateBaLeft
            case OperatorGP.RotateAcRight:
                node.func = body.rotateAcRight
            case OperatorGP.RotateBaRight:
                node.func = body.rotateBaRight
            case OperatorGP.AddDegree:
                node.func = body.addDegree
            case OperatorGP.SubstractDegree:
                node.func = body.substractDegree

        return node

    def create_random_individual(self) -> Individual:
        ind = Individual(self.space,self.ground_y)
        ind.brain = self.__create_random_tree(ind,TinyGP.max_depth)
        return ind

    def mutation(self):
        pass

    def crossover(self):
        pass

    def tournament(self):
        pass

    def negative_tournament(self):
        pass