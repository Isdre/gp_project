import random
from enum import IntEnum
from copy import deepcopy
from typing import List
from pygame import math

from Individual.Individual import *

class TinyGP:
    # parameters
    enum_max = 8
    max_TTL = 10  # seconds

    random_const_amount = 50
    random_const_min = -5
    random_const_max = 5

    generation = 100
    max_depth = 7
    population_size = 12

    mutation_rate = 0.25
    crossover_rate = 0.25
    # -----------

    def __init__(self,space,ground_y,fps):
        self.space = space
        self.ground_y = ground_y
        self.fps = fps
        #-----------
        assert TinyGP.max_depth > 2
        assert TinyGP.population_size > 0

        TinyGP.enum_max = max(OperatorGP)
        self.best_brain = ""
        self.best_fitness = 0
        self.best_size = pow(2, TinyGP.max_depth)
        self.random_consts = [random.random() * (TinyGP.random_const_max - TinyGP.random_const_min) + TinyGP.random_const_min for _ in range(TinyGP.random_const_amount)]
        self.population = [self.create_random_individual() for _ in range(TinyGP.population_size)]

        self.generation = 1
        self.generation_timer = TinyGP.max_TTL
        #---

        self.mutation_min_depth = 2
        self.mutation_max_depth = TinyGP.max_depth - self.mutation_min_depth

        self.crossover_min_depth = 2
        self.crossover_max_depth = TinyGP.max_depth - self.crossover_min_depth

        self.__weights = []
        print("TinyGP created")


    def start_generation(self):
        print(f"TinyGP generation: {self.generation}")
        print(f"Size of population: {len(self.population)}")
        self.generation_timer = TinyGP.max_TTL
        for ind in self.population:
            ind.reset_individual()

    #returns true if simulation should be continued
    def step(self,dt:float) -> bool:
        for ind in self.population:
            float(ind.brain)
        self.calc_fitness()
        self.generation_timer -= dt
        # print(self.generation_timer)
        return self.generation_timer > 0

    def next_generation(self):
        self.find_save_best()
        self.evolve()
        self.generation += 1

        self.start_generation()

    def calc_fitness(self):
        for ind in self.population:
            if ind.live: ind.fitness = max(1,ind.getDistance())

    def find_save_best(self):
        maybe_best = max(self.population, key=lambda x: x.fitness)
        if maybe_best.fitness > self.best_fitness or (maybe_best.fitness == self.best_fitness and maybe_best.brain.size < self.best_size):
            self.best_brain = str(maybe_best.brain)
            self.best_fitness = maybe_best.fitness
            self.best_size = maybe_best.brain.size

        print(f"Best fitness: {self.best_fitness}")
        print(f"Best size: {self.best_size}")
        print(f"Best brain: {self.best_brain}")
        fitness_sum = 0
        size_sum = 0
        for p in self.population:
            fitness_sum += p.fitness
            size_sum += p.brain.size
        print(f"Average fitness: {fitness_sum/self.population_size}")
        print(f"Average size: {size_sum / self.population_size}")


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
        if depth <= 2:
            return current
        if random.random() < 0.5:
            return self.__get_random_node_at_depth(current.left,depth-1)
        else:
            return self.__get_random_node_at_depth(current.right,depth-1)

    def mutation(self,ind:Individual):
        depth = random.randint(self.mutation_min_depth, self.mutation_max_depth)
        # print(depth)
        parent = self.__get_random_node_at_depth(ind.brain,depth)
        try:
            if (isinstance(parent.left,Node)) and (random.random() < 0.5 or not isinstance(parent.right,Node)):
                parent.left = self.__create_random_tree(ind, random.randint(1,TinyGP.max_depth - depth+1))
            else:
                parent.right = self.__create_random_tree(ind, random.randint(1,TinyGP.max_depth - depth+1))
        except Exception as e:
            print(e)

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

        if isinstance(node.left,Node):
            self.__change_nodes_body(new_body, node.left)
        if isinstance(node.right,Node):
            self.__change_nodes_body(new_body, node.right)

    def crossover(self,ind1:Individual,ind2:Individual) -> (Individual,Individual):
        ind1_c = Individual(self.space,self.ground_y)
        ind1_c.brain = deepcopy(ind1.brain)
        ind2_c = Individual(self.space,self.ground_y)
        ind2_c.brain = deepcopy(ind2.brain)

        depth = random.randint(self.crossover_min_depth, self.crossover_max_depth)
        parent1 = self.__get_random_node_at_depth(ind1_c.brain, depth)
        parent2 = self.__get_random_node_at_depth(ind2_c.brain, depth)

        to_change_1 = random.randint(0, 1)
        if to_change_1 == 0: leaf1 = parent1.left
        else: leaf1 = parent1.right

        to_change_2 = random.randint(0, 1)
        if to_change_2 == 0: leaf2 = parent2.left
        else:leaf2 = parent2.right

        self.__change_nodes_body(ind2_c, ind2_c.brain)
        self.__change_nodes_body(ind1_c, ind1_c.brain)

        if to_change_1 == 0: parent1.left = leaf2
        else: parent1.right = leaf2

        if to_change_2 == 0: parent2.left = leaf1
        else: parent2.right = leaf1

        return ind1_c, ind2_c

    def evolve(self):
        #crossover
        parents = self.tournament(self.crossover_rate)
        children = []
        to_remove = []
        for i in range(0,len(parents)-len(parents)%2,2):
            to_remove.append(i)
            to_remove.append(i+1)
            children += self.crossover(parents[i],parents[i+1])

        self.population = [x for i, x in enumerate(self.population) if i not in to_remove]

        # negative tournament
        self.negative_tournament(self.crossover_rate)

        #mutation
        mutants = self.tournament(self.mutation_rate)
        for mutant in mutants:
            if mutant in self.population: self.population.remove(mutant)
            # print(f"Before mutation: {mutant.brain}")
            self.mutation(mutant)
            # print(f"After mutation: {mutant.brain}")

        #merging
        self.population += mutants
        self.population += children
        self.population += parents
        self.population.sort(key=lambda x: (x.brain.size,x.brain.depth))

        if len(self.population) > self.population_size:
            for i in range(self.population_size,len(self.population)):
                self.population[i].die()
            self.population = self.population[:self.population_size]
        elif len(self.population) < self.population_size:
            for i in range(self.population_size-len(self.population)):
                self.population.append(self.create_random_individual())


    #choose and get from population
    def tournament(self, rate: float) -> List[Individual]:
        self.__weights = [x.fitness for x in self.population]
        m = abs(min(self.__weights)) + 1 if min(self.__weights) < 0 else 0
        self.__weights = [w + m for w in self.__weights]

        selection_count = int(self.population_size * rate)
        return random.choices(self.population, weights=self.__weights, k=selection_count)

    #choose and remove from population
    def negative_tournament(self, rate: float) -> None:
        self.__weights = [x.fitness for x in self.population]
        mX = abs(max(self.__weights))
        self.__weights = [w + mX for w in self.__weights]

        removal_count = int(self.population_size * rate)
        to_remove = random.sample(range(len(self.population)), removal_count)

        for i in to_remove:
            self.population[i].die()

        self.population = [x for i, x in enumerate(self.population) if i not in to_remove]