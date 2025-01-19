import pymunk
import numpy as np
from TinyGP.TinyGP import TinyGP

class TestTinyGP:
    def testTinyGP(self):
        TinyGP.population_size = 10
        TinyGP.max_depth = 10

        space = pymunk.Space()
        tinyGP = TinyGP(space,400,60)
        assert len(tinyGP.population) == TinyGP.population_size
        assert len(tinyGP.random_consts) == TinyGP.random_const_amount
        consts = np.array(tinyGP.random_consts)
        assert ((consts >= TinyGP.random_const_min) & (consts <= TinyGP.random_const_max)).all()

        # print()
        for index,ind in enumerate(tinyGP.population):
            # print(f"Individual {index}")
            # print(ind.brain)
            assert str(ind.brain).count("(") == pow(2,TinyGP.max_depth) - 1

    def testSize(self):
        TinyGP.population_size = 1
        TinyGP.max_depth = 4

        space = pymunk.Space()
        tinyGP = TinyGP(space, 400, 60)
        ind = tinyGP.population[0]
        print()
        print(ind.brain)
        print(ind.brain.size)
        print(ind.brain.depth)
        tinyGP.mutation(ind)
        print()
        print(ind.brain)
        print(ind.brain.size)
        print(ind.brain.depth)

    def testMutation(self):
        TinyGP.population_size = 1
        TinyGP.max_depth = 5

        space = pymunk.Space()
        tinyGP = TinyGP(space, 400, 60)
        ind = tinyGP.population[0]
        assert str(ind.brain).count("(") == pow(2, TinyGP.max_depth) - 1
        # print()
        # print(ind.brain)
        for i in range(100):
            tinyGP.mutation(ind)
            # print(ind.brain)
            float(ind.brain)

    def testCrossover(self):
        TinyGP.population_size = 2
        TinyGP.max_depth = 5

        space = pymunk.Space()
        tinyGP = TinyGP(space, 400, 60)
        ind1 = tinyGP.population[0]
        ind2 = tinyGP.population[1]

        print(ind1.brain)
        print(ind2.brain)
        ind1,ind2 = tinyGP.crossover(ind1,ind2)
        print(ind1.brain)
        print(ind2.brain)
