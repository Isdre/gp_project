import random
from enum import IntEnum
from Individual.Individual import *


class TinyGP:
    # parameters
    enum_max = 8
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
        assert TinyGP.max_depth > 2
        assert TinyGP.population_size > 0

        TinyGP.enum_max = max(OperatorGP)
        self.best_ind = None
        self.best_fitness = 0
        self.random_consts = [random.random() * (TinyGP.random_const_max - TinyGP.random_const_min) + TinyGP.random_const_min for _ in range(TinyGP.random_const_amount)]
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

        if depth == 1:
            op = random.randint(0, 1)
        else:
            node.left = self.__create_random_tree(body, depth - 1)
            node.right = self.__create_random_tree(body, depth - 1)

        node.operator = OperatorGP(op)
        match node.operator:
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
            case OperatorGP.Condition:
                node.func = body.condition

        return node

    def create_random_individual(self) -> Individual:
        ind = Individual(self.space,self.ground_y)
        ind.brain = self.__create_random_tree(ind,TinyGP.max_depth)
        return ind

    #get random Node at particular depth
    def __get_random_node_at_depth(self,current:Node,depth:int) -> Node:
        if depth == 2:
            return current
        path = random.randint(0,1)
        if path == 0:
            return self.__get_random_node_at_depth(current.left,depth-1)
        else:
            return self.__get_random_node_at_depth(current.right,depth-1)

    def mutation(self,ind:Individual) -> Individual:
        depth = random.randint(2, TinyGP.max_depth-1)
        # print(depth)
        parent = self.__get_random_node_at_depth(ind.brain,depth)
        to_remove = random.randint(0, 1)
        if to_remove == 0:
            parent.left = self.__create_random_tree(ind, TinyGP.max_depth - depth+1)
        else:
            parent.right = self.__create_random_tree(ind, TinyGP.max_depth - depth+1)

        return ind

    def __change_nodes_body(self, new_body:Individual, node:Node):
        match node.operator:
            case OperatorGP.RotateAcLeft:
                node.func = new_body.rotateAcLeft
            case OperatorGP.RotateBaLeft:
                node.func = new_body.rotateBaLeft
            case OperatorGP.RotateAcRight:
                node.func = new_body.rotateAcRight
            case OperatorGP.RotateBaRight:
                node.func = new_body.rotateBaRight
            case OperatorGP.AddDegree:
                node.func = new_body.addDegree
            case OperatorGP.SubstractDegree:
                node.func = new_body.substractDegree
            case OperatorGP.Condition:
                node.func = new_body.condition

        if type(node.left) == Node:
            self.__change_nodes_body(new_body, node.left)
        if type(node.right) == Node:
            self.__change_nodes_body(new_body, node.right)

    def crossover(self,ind1:Individual,ind2:Individual) -> (Individual,Individual):
        depth = random.randint(2, TinyGP.max_depth - 1)
        parent1 = self.__get_random_node_at_depth(ind1.brain, depth)
        parent2 = self.__get_random_node_at_depth(ind2.brain, depth)
        leaf1 = None
        leaf2 = None

        to_change_1 = random.randint(0, 1)
        if to_change_1 == 0: leaf1 = parent1.left
        else: leaf1 = parent1.right

        to_change_2 = random.randint(0, 1)
        if to_change_2 == 0: leaf2 = parent2.left
        else:leaf2 = parent2.right

        self.__change_nodes_body(ind2, leaf1)
        self.__change_nodes_body(ind1, leaf2)

        if to_change_1 == 0: parent1.left = leaf2
        else: parent1.right = leaf2

        if to_change_2 == 0: parent2.left = leaf1
        else: parent2.right = leaf1

        return ind1, ind2

    def tournament(self):
        pass

    def negative_tournament(self):
        pass