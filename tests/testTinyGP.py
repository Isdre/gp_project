import pymunk
import numpy as np
from Evolution.Evolution import Evolution

class TestEvolution:
    def testEvolution(self):
        Evolution.population_size = 10
        Evolution.max_depth = 10

        space = pymunk.Space()
        evo = Evolution(space,400,60)
        assert len(evo.population) == Evolution.population_size
        assert len(evo.random_consts) == Evolution.random_const_amount
        consts = np.array(evo.random_consts)
        assert ((consts >= Evolution.random_const_min) & (consts <= Evolution.random_const_max)).all()

        # print()
        for index,ind in enumerate(evo.population):
            # print(f"Individual {index}")
            # print(ind.brain)
            assert str(ind.brain).count("(") == pow(2,Evolution.max_depth) - 1

    def testSize(self):
        Evolution.population_size = 1
        Evolution.max_depth = 4

        space = pymunk.Space()
        evo = Evolution(space, 400, 60)
        ind = evo.population[0]
        print()
        print(ind.brain)
        print(ind.brain.size)
        print(ind.brain.depth)
        evo.mutation(ind)
        print()
        print(ind.brain)
        print(ind.brain.size)
        print(ind.brain.depth)

    def testMutation(self):
        Evolution.population_size = 1
        Evolution.max_depth = 5

        space = pymunk.Space()
        evo = Evolution(space, 400, 60)
        ind = evo.population[0]
        assert str(ind.brain).count("(") == pow(2, Evolution.max_depth) - 1
        # print()
        # print(ind.brain)
        for i in range(100):
            evo.mutation(ind)
            # print(ind.brain)
            float(ind.brain)

    def testCrossover(self):
        Evolution.population_size = 2
        Evolution.max_depth = 5

        space = pymunk.Space()
        evo = Evolution(space, 400, 60)
        ind1 = evo.population[0]
        ind2 = evo.population[1]
        print(ind1.brain)
        print(ind2.brain)
        ind1,ind2 = evo.crossover(ind1,ind2)
        print(ind1.brain)
        print(ind2.brain)

    def testLoad(selfS):
        Evolution.population_size = 2
        Evolution.max_depth = 5

        space = pymunk.Space()
        evo = Evolution(space, 400, 60)
        evo.load_best_indvidual("../best_ind.txt",True)
        assert len(evo.population) == Evolution.population_size + 1, f"{len(evo.population)}"
        print(evo.population[-1].brain)