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

    def testMutation(self):
        TinyGP.population_size = 1
        TinyGP.max_depth = 3

        space = pymunk.Space()
        tinyGP = TinyGP(space, 400, 60)
        ind = tinyGP.population[0]
        assert str(ind.brain).count("(") == pow(2, TinyGP.max_depth) - 1
        # print()
        # print(ind.brain)
        for i in range(100):
            ind = tinyGP.mutation(ind)
            # print(ind.brain)
            assert str(ind.brain).count("(") == pow(2, TinyGP.max_depth) - 1
            float(ind.brain)

    def testCrossover(self):
        TinyGP.population_size = 2
        TinyGP.max_depth = 10

        space = pymunk.Space()
        tinyGP = TinyGP(space, 400, 60)
        ind1 = tinyGP.population[0]
        ind2 = tinyGP.population[1]
        print()
        print(ind1.brain)
        assert str(ind1.brain).count("(") == pow(2, TinyGP.max_depth) - 1
        print(ind2.brain)
        assert str(ind2.brain).count("(") == pow(2, TinyGP.max_depth) - 1
        ind1,ind2 = tinyGP.crossover(ind1,ind2)
        print(ind1.brain)
        assert str(ind1.brain).count("(") == pow(2, TinyGP.max_depth) - 1
        print(ind2.brain)
        assert str(ind2.brain).count("(") == pow(2, TinyGP.max_depth) - 1
