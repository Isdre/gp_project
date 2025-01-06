import random
from enum import IntEnum
from copy import deepcopy
from Individual.Individual import *

class TinyGP:
    # parameters
    enum_max = 8
    max_TTL = 120  # seconds

    random_const_amount = 50
    random_const_min = -5
    random_const_max = 5

    generation = 100
    max_depth = 10
    population_size = 10

    mutation_rate = 0.05
    crossover_rate = 0.5
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
        self.max_TTL = TinyGP.max_TTL
        #---
        self.mutation_min_depth = 2
        self.mutation_max_depth = TinyGP.max_depth - 1

        self.crossover_min_depth = 2
        self.crossover_max_depthcrossover_max_depth = TinyGP.max_depth - 1


    def start_generation(self):
        for ind in self.population:
            ind.fitness = 0
            ind.live = True

    #returns true if simulation should be continued
    def step(self,dt:float) -> bool:
        for ind in self.population:
            float(ind.brain)
        self.calc_fitness()
        self.max_TTL -= dt
        return self.max_TTL > 0

    def calc_fitness(self):
        for ind in self.population:
            if ind.live: ind.fitness = ind.getDistance()

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
        # print(depth)
        if depth == 2:
            return current
        path = random.randint(0,1)
        if path == 0:
            return self.__get_random_node_at_depth(current.left,depth-1)
        else:
            return self.__get_random_node_at_depth(current.right,depth-1)

    def mutation(self,ind:Individual):
        depth = random.randint(self.mutation_min_depth, self.mutation_max_depth)
        # print(depth)
        parent = self.__get_random_node_at_depth(ind.brain,depth)
        to_remove = random.randint(0, 1)
        if to_remove == 0:
            parent.left = self.__create_random_tree(ind, TinyGP.max_depth - depth+1)
        else:
            parent.right = self.__create_random_tree(ind, TinyGP.max_depth - depth+1)

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
        ind1_c = deepcopy(ind1)
        ind2_c = deepcopy(ind2)
        depth = random.randint(self.crossover_min_depth, self.crossover_max_depth)
        parent1 = self.__get_random_node_at_depth(ind1_c.brain, depth)
        parent2 = self.__get_random_node_at_depth(ind2_c.brain, depth)
        leaf1 = None
        leaf2 = None

        to_change_1 = random.randint(0, 1)
        if to_change_1 == 0: leaf1 = parent1.left
        else: leaf1 = parent1.right

        to_change_2 = random.randint(0, 1)
        if to_change_2 == 0: leaf2 = parent2.left
        else:leaf2 = parent2.right

        self.__change_nodes_body(ind2_c, leaf1)
        self.__change_nodes_body(ind1_c, leaf2)

        if to_change_1 == 0: parent1.left = leaf2
        else: parent1.right = leaf2

        if to_change_2 == 0: parent2.left = leaf1
        else: parent2.right = leaf1

        return ind1_c, ind2_c

    def evolve(self):
        #crossover
        parents = self.tournament(self.crossover_rate)
        children = []
        for i in range(0,len(parents),2):
            kids = self.crossover(parents[i],parents[i+1])
            children.append(kids[0])
            children.append(kids[1])

        #mutation
        mutants = self.tournament(self.mutation_rate)
        for mutant in mutants:
            self.mutation(mutant)

        #merging

    #choose and get from population
    def tournament(self,rate:float) -> [Individual]:
        return random.choices(self.population,weights=[x.fitness for x in self.population],k=int(len(self.population)*rate))

    #choose and remove from population
    def negative_tournament(self,rate:float) -> None:
        pass