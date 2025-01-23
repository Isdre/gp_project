import random
import re
from enum import IntEnum
from typing import List
from pygame import math
import numpy as np
from Individual.Individual import *

class Evolution:
    # parameters
    enum_max = 8
    max_TTL = 50  # seconds

    random_const_amount = 50
    random_const_min = -25
    random_const_max = 25

    generation = 50
    max_depth = 8
    population_size = 50

    mutation_rate_basic = 0.3
    mutation_rate_critic = 0.5

    crossover_rate_basic = 0.25
    crossover_rate_critic = 0.0

    best_ind_file = "best_ind.txt"
    population_file = "population.txt"
    # -----------

    def __init__(self,space,ground_y,fps,end_generation=0, end_evolution=0):

        self.space = space
        self.ground_y = ground_y
        self.fps = fps
        #-----------
        assert Evolution.max_depth > 2
        assert Evolution.population_size > 0

        match end_generation:
            case 0:
                self.if_end_generation = self.reached_time_limit
            case _:
                self.if_end_generation = self.reached_time_limit

        match end_evolution:
            case 0:
                self.if_end_evolution = self.reached_generation_limit
            case _:
                self.if_end_evolution = self.reached_generation_limit

        self.best_brain = ""
        self.best_fitness = 0
        self.best_size = pow(2, Evolution.max_depth)
        self.best_depth = Evolution.max_depth

        self.general_stagnation_constraint = 5
        self.general_stagnation_epsilon = 100
        self.general_stagnation_count = -1
        self.general_stagnation = False

        self.anomaly_constraint = 4000
        self.left_anomaly_constraint = -100

        self.random_consts = [random.random() * (Evolution.random_const_max - Evolution.random_const_min) + Evolution.random_const_min for _ in range(Evolution.random_const_amount)]

        self.population = [self.create_random_individual() for _ in range(Evolution.population_size)]

        self.mutation_rate = Evolution.mutation_rate_basic
        self.crossover_rate = Evolution.crossover_rate_basic
        self.negative_tournament_rate = Evolution.crossover_rate_basic

        self.generation = 1
        self.generation_timer = 0
        #---

        self.mutation_min_depth = 4
        self.mutation_max_depth = 8

        self.crossover_min_depth = 6
        self.crossover_max_depth = 8

        with open("best_fitness.txt","w") as f:
            f.write("")
        with open("average_fitness.txt","w") as f:
            f.write("")
        with open("average_size.txt","w") as f:
            f.write("")

        print("First generation created")

    def print_stats(self):
        print(f"Generation: {self.generation}")
        print(f"Size of population: {len(self.population)}")
        print(f"Stagnation: {self.general_stagnation_count}/{self.general_stagnation_constraint}")
        num_bodies = len(self.space.bodies)
        num_shapes = len(self.space.shapes)
        num_constraints = len(self.space.constraints)

        print(f"Number of bodies: {num_bodies}")
        print(f"Number of shapes: {num_shapes}")
        print(f"Number of constraints: {num_constraints}")

    def start_generation(self):
        self.print_stats()
        self.generation_timer = 0
        for ind in self.population:
            ind.reset_individual()

    #returns true if simulation should be continued
    def step(self,dt:float):
        for ind in self.population:
            try:
                float(ind.brain)
                ind.check_speed()
            except:
                ind.live = False
        self.calc_fitness()
        self.generation_timer += dt
        # print(self.generation_timer)

    def next_generation(self):
        self.check_for_errors()
        self.find_best()
        self.check_for_stagnation()
        self.evolve()
        self.generation += 1
        self.start_generation()

    def calc_fitness(self):
        for ind in self.population:
            if ind.live: ind.fitness = ind.getDistance()

    def find_best(self):
        maybe_best = max(self.population, key=lambda x: (x.fitness,-1*x.brain.size,-1*x.brain.depth))

        if maybe_best.fitness - self.best_fitness < self.general_stagnation_epsilon:
            self.general_stagnation_count += 1
        else:
            self.general_stagnation_count = 0

        if (maybe_best.fitness > self.best_fitness or
                (maybe_best.fitness == self.best_fitness and maybe_best.brain.size < self.best_size)  or
                (maybe_best.fitness == self.best_fitness and maybe_best.brain.size == self.best_size and maybe_best.brain.depth < self.best_depth)):

            self.best_brain = str(maybe_best.brain)
            self.best_fitness = maybe_best.fitness
            self.best_size = maybe_best.brain.size
            self.best_depth = maybe_best.brain.depth

        print(f"Best fitness: {self.best_fitness}")
        print(f"Best size: {self.best_size}")
        print(f"Best brain: {self.best_brain}")
        fitness_sum = 0
        size_sum = 0
        for p in self.population:
            fitness_sum += p.fitness
            size_sum += p.brain.size
        print(f"Average fitness: {fitness_sum/Evolution.population_size}")
        print(f"Average size: {size_sum / Evolution.population_size}")
        with open("best_fitness.txt","a") as f:
            f.write(f"{self.best_fitness}\n")
        with open("average_fitness.txt","a") as f:
            f.write(f"{fitness_sum/Evolution.population_size}\n")
        with open("average_size.txt","a") as f:
            f.write(f"{size_sum/Evolution.population_size}\n")

    def check_for_stagnation(self):
        if self.general_stagnation_count >= self.general_stagnation_constraint:
            self.general_stagnation = True
            self.general_stagnation_count = 0
            self.mutation_rate = Evolution.mutation_rate_critic
            self.crossover_rate = Evolution.crossover_rate_critic
            # self.negative_tournament_rate = Evolution.mutation_rate_critic

    def check_for_errors(self):
        for i in range(len(self.population)-1,-1,-1):
            if self.population[i].max_speed > self.anomaly_constraint:
                self.population[i].live = False
            if not self.population[i].live:# or self.population[i].fitness < self.left_anomaly_constraint:
                ind = self.population.pop(i)
                ind.die()
                # print("DIE")
                del ind


    #full
    def __create_random_tree(self,body:Individual,depth:int) -> Node:
        node = Node()

        op = random.randint(2,Evolution.enum_max)

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
            case OperatorGP.Loop:
                node.func = body.loop
            case _:
                print("BAD NEWS")

        return node

    #
    def __create_random_tree_1(self,body:Individual,depth:int) -> Node:
        node = Node()

        if depth == 1:
            op = random.randint(0, 1)
        else:
            op = random.randint(0, Evolution.enum_max)

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
            case OperatorGP.Loop:
                node.func = body.loop
            case _:
                print("BAD NEWS")

        if op > 1:
            node.left = self.__create_random_tree(body, depth - 1)
            node.right = self.__create_random_tree(body, depth - 1)

        return node

    def create_random_individual(self) -> Individual:
        ind = Individual(self.space,self.ground_y)
        ind.brain = self.__create_random_tree(ind,Evolution.max_depth)
        return ind

    #get random Node at particular depth
    def __get_random_node_at_depth(self,current:Node,depth:int) -> Node:
        if depth <= 2 or not (isinstance(current.left, Node) or isinstance(current.right, Node)):
            return current

        candidates = []
        if isinstance(current.left, Node) and current.left.depth >= depth - 1:
            candidates.append(current.left)
        if isinstance(current.right, Node) and current.right.depth >= depth - 1:
            candidates.append(current.right)

        if candidates:
            chosen = random.choice(candidates)
            return self.__get_random_node_at_depth(chosen, depth - 1)

        return current

    def mutation(self,ind:Individual):
        depth = random.randint(self.mutation_min_depth, self.mutation_max_depth)
        # print(depth)
        parent = self.__get_random_node_at_depth(ind.brain,depth)
        try:
            if (isinstance(parent.left,Node)) and (random.random() < 0.5 or not isinstance(parent.right,Node)):
                parent.left = self.__create_random_tree(ind, random.randint(self.mutation_min_depth, self.mutation_max_depth))
            else:
                parent.right = self.__create_random_tree(ind, random.randint(self.mutation_min_depth,self.mutation_max_depth))
        except Exception as e:
            print(e)

    def __change_nodes_body(self, new_body:Individual, node:Node):
        match node.operator:
            case OperatorGP.Variable:
                match str(node.func):
                    case "getHeight":
                        node.func = new_body.getHeight
                    case "getSpread":
                        node.func = new_body.getSpread
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
            case OperatorGP.Loop:
                node.func = new_body.loop

        if isinstance(node.left,Node):
            self.__change_nodes_body(new_body, node.left)
        if isinstance(node.right,Node):
            self.__change_nodes_body(new_body, node.right)

    def crossover(self,ind1:Individual,ind2:Individual) -> (Individual,Individual):
        ind1_c = Individual(self.space, self.ground_y)
        ind1_c.brain = Node.deepcopy(ind1.brain)
        self.__change_nodes_body(ind1_c, ind1_c.brain)
        ind2_c = Individual(self.space,self.ground_y)
        ind2_c.brain = Node.deepcopy(ind2.brain)
        self.__change_nodes_body(ind2_c,ind2_c.brain)

        depth = random.randint(self.crossover_min_depth, self.crossover_max_depth)
        #
        # print(ind1.brain)
        # print(ind2.brain)
        #
        # print(ind1_c.brain)
        # print(ind2_c.brain)

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
        # self.check_if_are_duplicates()
        # self.print_stats()
        #crossover
        # print("Before crossover")
        # self.print_stats()
        parents = self.tournament(self.crossover_rate)
        parents = list(dict.fromkeys(parents))

        children = []
        to_remove = []

        for i in range(0,len(parents)-len(parents)%2,2):
            # print(f"{i} {i+1}")
            to_remove.append(self.population.index(parents[i]))
            to_remove.append(self.population.index(parents[i+1]))
            children += self.crossover(parents[i],parents[i+1])

        # print(len(parents))
        if len(parents)%2 != 0:
            to_remove.append(self.population.index(parents[-1]))

        to_remove.sort(reverse=True)
        # print(to_remove)
        for i in to_remove:
            self.population.pop(i)

        # self.check_if_are_duplicates()

        # print("After crossover and before negative_tournament")
        # print(f"Parents size: {len(parents)}")
        # print(f"Children size: {len(children)}")
        # self.print_stats()

        # negative tournament
        self.negative_tournament(self.negative_tournament_rate)
        # print("After negative_tournament and before mutation")
        # print(f"Parents size: {len(parents)}")
        # print(f"Children size: {len(children)}")


        #mutation

        # self.check_if_are_duplicates()

        # mutants = [m for m in self.tournament(self.mutation_rate) if m in self.population]
        mutants = self.tournament(self.mutation_rate)
        mutants = list(dict.fromkeys(mutants))
        # print(f"Amount of individuals to mutate: {len(mutants)}")
        # self.print_stats()
        # to_remove = []
        # self.check_if_are_duplicates()
        for mutant in mutants:
            if mutant in self.population:
                # print(f"Mutant is in population. {mutant}")
                self.population.remove(mutant)
            # else:
                # print(f"Mutant is not in population. {mutant}")
                # self.population.append(mutant)

            self.mutation(mutant)

        # print("After mutation")
        # print(f"Parents size: {len(parents)}")
        # print(f"Children size: {len(children)}")
        # print(f"Mutants size: {len(mutants)}")
        # self.print_stats()
        # self.check_if_are_duplicates()
        #merging
        self.population += mutants
        # self.check_if_are_duplicates()
        self.population += children
        # self.check_if_are_duplicates()
        self.population += parents
        # self.check_if_are_duplicates()
        # print("Before validation")
        # self.print_stats()
        if len(self.population) > Evolution.population_size:
            # print("Too many")
            self.population.sort(key=lambda x: (x.brain.size, x.brain.depth))
            for i in range(Evolution.population_size,len(self.population)):
                ind = self.population.pop(-1)
                ind.die()
                del ind
        elif len(self.population) < Evolution.population_size:
            # print("Not enough")
            for i in range(Evolution.population_size-len(self.population)):
                self.population.append(self.create_random_individual())
        # print("After evolve")
        # self.print_stats()

        if self.general_stagnation:
            self.mutation_rate = Evolution.mutation_rate_basic
            self.crossover_rate = Evolution.crossover_rate_basic
            self.negative_tournament_rate = Evolution.crossover_rate_basic
            self.general_stagnation = False

        self.check_if_are_duplicates()
        self.validate_population()

    #choose and get from population
    def tournament(self, rate: float) -> List[Individual]:
        fitness_values = [x.fitness for x in self.population]
        max_fitness = max(fitness_values)
        min_fitness = min(fitness_values)

        if max_fitness == min_fitness:
            weights = [1.0] * len(fitness_values)
        else:
            weights = [(f - min_fitness) / (max_fitness - min_fitness) for f in fitness_values]

        total_weight = sum(weights)
        if total_weight == 0:
            probabilities = [1.0 / len(weights)] * len(weights)
        else:
            probabilities = [w / total_weight for w in weights]

        selection_count = int(len(self.population) * rate)

        selected_individuals = np.random.choice(
            self.population,
            size=selection_count,
            replace=False,
            p=probabilities
        )

        # Return the selected individuals as a list
        return selected_individuals.tolist()

    #choose and remove from population -- check
    def negative_tournament_0(self, rate: float) -> None:
        fitness_values = [x.fitness for x in self.population]

        min_fitness = min(fitness_values)
        max_fitness = max(fitness_values)

        if max_fitness == min_fitness:
            weights = [1.0] * len(fitness_values)
        else:
            # Przekształć fitness na wagi: max_fitness - fitness
            weights = [(max_fitness - f) for f in fitness_values]

        total_weight = sum(weights)

        if total_weight == 0:
            probabilities = [1.0 / len(weights)] * len(weights)
        else:
            probabilities = [w / total_weight for w in weights]

        removal_count = int(len(self.population) * rate)

        to_remove = np.random.choice(
            range(len(self.population)),
            size=removal_count,
            replace=False,
            p=probabilities
        )

        for index in sorted(to_remove, reverse=True):
            individual = self.population.pop(index)
            individual.die()
            del individual

    def negative_tournament(self, rate: float) -> None:
        fitness_values = [(-1) * x.fitness for x in self.population]
        max_fitness = max(fitness_values)
        min_fitness = min(fitness_values)

        if max_fitness == min_fitness:
            weights = [1.0] * len(fitness_values)
        else:
            weights = [(f - min_fitness) / (max_fitness - min_fitness) for f in fitness_values]

        total_weight = sum(weights)
        if total_weight == 0:
            probabilities = [1.0 / len(weights)] * len(weights)
        else:
            probabilities = [w / total_weight for w in weights]

        removal_count = int(len(self.population) * rate)

        to_remove = np.random.choice(
            range(len(self.population)),
            size=removal_count,
            replace=False,
            p=probabilities
        )

        for index in sorted(to_remove, reverse=True):
            individual = self.population.pop(index)
            individual.die()
            del individual

    def validate_population(self):
        assert len(self.population) == Evolution.population_size, "Population exceeds the allowed size!"
        assert all(isinstance(ind, Individual) for ind in self.population), "Invalid individual in population!"

        num_bodies = len(self.space.bodies)
        num_shapes = len(self.space.shapes)
        num_constraints = len(self.space.constraints)

        # assert num_bodies == Evolution.population_size * 5
        # assert num_shapes >= Evolution.population_size * 5
        # assert num_constraints == Evolution.population_size * 8

    def check_if_are_duplicates(self):
        a = len(self.population)
        self.population = list(dict.fromkeys(self.population))
        b = len(self.population)
        assert a == b, f"Population contained duplicate individuals ({a-b})"

    def save(self):
        self.population.sort(key=lambda x: (x.fitness),reverse=True)
        with open(Evolution.population_file, "w") as f:
            for p in self.population:
                f.write(str(p.brain)+"\n")
        with open(Evolution.best_ind_file, "w") as f:
            f.write(self.best_brain+"\n")
            f.write(str(self.best_fitness)+"\n")
            f.write(str(self.best_size)+"\n")
            f.write(str(self.best_depth)+"\n")

    def load_best_indvidual(self,filename:str,put_to_population:bool=False) :
        with open(filename, "r") as f:
            self.best_brain = f.readline().strip()
        #     self.best_fitness = float(f.readline().strip())
        #     self.best_size = int(f.readline().strip())
        #     self.best_depth = int(f.readline().strip())
        if put_to_population:
            self.load_individual(self.best_brain)

    def load_population(self,filename):
        self.clear_population()
        with open(filename, "r") as f:
            for line in f.readlines():
                self.load_individual(line)

    def load_individual(self,brain:str):
        new_ind = Individual(self.space,self.ground_y)

        def parse_inner(expr):
            expr = expr.strip()
            match = re.match(r"(\w+)\((.*)\)", expr)

            node = Node()

            if match:
                func_name = match.group(1)
                args = match.group(2)

                match func_name:
                    case "default":
                        node.operator = OperatorGP.Constant
                    case "getHeight" | "getSpread":
                        node.operator = OperatorGP.Variable
                        node.func = func_name
                    case "rotateAcLeft":
                        node.operator = OperatorGP.RotateAcLeft
                    case "rotateBaLeft":
                        node.operator = OperatorGP.RotateBaLeft
                    case "rotateAcRight":
                        node.operator = OperatorGP.RotateAcRight
                    case "rotateBaRight":
                        node.operator = OperatorGP.RotateBaRight
                    case "addDegree":
                        node.operator = OperatorGP.AddDegree
                    case "substractDegree":
                        node.operator = OperatorGP.SubstractDegree
                    case "condition":
                        node.operator = OperatorGP.Condition
                    case "loop":
                        node.operator = OperatorGP.Loop
                    case _:
                        print(f"Unrecognized operator : {func_name}")

                balance = 0
                current_arg = []
                for char in args:
                    if char == ',' and balance == 0:
                        node.left = (parse_inner(''.join(current_arg)))
                        current_arg = []
                    else:
                        current_arg.append(char)
                        if char == '(':
                            balance += 1
                        elif char == ')':
                            balance -= 1
                if current_arg:
                    node.right = (parse_inner(''.join(current_arg)))  # Add the last child
                return node
            else:
                return float(expr)

        new_ind.brain = parse_inner(brain)

        self.__change_nodes_body(new_ind, new_ind.brain)
        # print(new_ind.brain)

        self.population.append(new_ind)

    def clear_population(self):
        for _ in range(len(self.population)):
            i = self.population.pop(-1)
            i.die()
            del i

    def reached_time_limit(self):
        return self.generation_timer >= Evolution.max_TTL

    def reached_generation_limit(self):
        return self.generation >= Evolution.generation