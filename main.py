import sys

import pygame
from pygame.locals import USEREVENT, QUIT, KEYDOWN, KEYUP, K_s, K_r, K_q, K_ESCAPE, K_UP, K_DOWN, K_RIGHT, K_LEFT
from pygame.color import THECOLORS

import pymunk
from pymunk import Vec2d
import pymunk.pygame_util

from Individual.Individual import Individual
from Evolution.Evolution import Evolution

from copy import deepcopy

class Simulator:
    def __init__(self):
        self.display_flags = pygame.SCALED
        self.H = 600
        self.display_size = (1000, self.H)

        self.space = pymunk.Space()
        self.space.gravity = (0.0, 981.0 * 15)
        self.space.damping = 0.1 # to prevent it from blowing up.

        # Pymunk physics coordinates start from the lower right-hand corner of the screen.
        self.ground_y = self.H - 50


        self.screen = None

        self.draw_options = None

        self.fps = 30

    #płaski teren
    def create_boundaries(self,width,height):
        thickness = 15
        rects = [
            [[-thickness,height - thickness],[width + thickness,height - thickness]]#,
        ]
        # zaokrąglone schody
        # last = [[150 + rects[-1][0][0],  rects[-1][0][1]], [rects[-1][1][0],  rects[-1][1][1]]]
        # for i in range(20):
        #     last = deepcopy(last)
        #     last[0][0] += 50
        #     last[0][1] -= 30
        #     last[1][0] += 50
        #     last[1][1] -= 30
        #     rects.append(last)

        for a,b in rects:
            body = pymunk.Segment(self.space.static_body, a, b, thickness)
            body.friction = 5

            self.space.add(body)

    #schody
    def create_boundaries_1(self, width, height):
        thickness = 15
        rects = [
            [[-thickness, height - thickness], [width + thickness, height - thickness]]
        ]
        last = [[150 + rects[-1][0][0], rects[-1][0][1]], [rects[-1][1][0], rects[-1][1][1]]]

        for i in range(20):
            last = deepcopy(last)
            last[0][0] += 50
            last[0][1] -= 30
            last[1][0] += 50
            last[1][1] -= 30
            rects.append(last)

        for a, b in rects:
            dx = b[0] - a[0]
            dy = b[1] - a[1]

            normal = (-dy, dx)
            normal_length = (normal[0] ** 2 + normal[1] ** 2) ** 0.5
            normal = (normal[0] / normal_length * thickness, normal[1] / normal_length * thickness)

            corners = [
                (a[0] - normal[0], a[1] - normal[1]),
                (a[0] + normal[0], a[1] + normal[1]),
                (b[0] + normal[0], b[1] + normal[1]),
                (b[0] - normal[0], b[1] - normal[1])
            ]

            body = pymunk.Poly(self.space.static_body, corners)
            body.friction = 5
            self.space.add(body)

    #półkole
    def create_boundaries_2(self, width, height):
        thickness = 15
        rects = [
            [[-thickness, height - thickness], [width + thickness, height - thickness]]
        ]

        for a, b in rects:
            dx = b[0] - a[0]
            dy = b[1] - a[1]

            normal = (-dy, dx)
            normal_length = (normal[0] ** 2 + normal[1] ** 2) ** 0.5
            normal = (normal[0] / normal_length * thickness, normal[1] / normal_length * thickness)

            corners = [
                (a[0] - normal[0], a[1] - normal[1]),
                (a[0] + normal[0], a[1] + normal[1]),
                (b[0] + normal[0], b[1] + normal[1]),
                (b[0] - normal[0], b[1] - normal[1])
            ]

            body = pymunk.Poly(self.space.static_body, corners)
            body.friction = 5
            self.space.add(body)

        pin_radius = 200
        pin_height = height + pin_radius

        pin_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        pin_body.position = (500, pin_height - pin_radius + 80)

        pin_shape = pymunk.Circle(pin_body, pin_radius)
        pin_shape.friction = 5
        pin_shape.elasticity = 0.5  # Ustaw elastyczność dla kolizji
        self.space.add(pin_body, pin_shape)

    def draw(self):
        self.screen.fill(THECOLORS["white"])  ### Clear the screen
        self.space.debug_draw(self.draw_options)  ### Draw space
        pygame.display.update()  ### All done, lets flip the display

    def main(self,evolution:Evolution):
        pygame.init()
        self.screen = pygame.display.set_mode(self.display_size, self.display_flags)
        width, height = self.screen.get_size()
        self.create_boundaries(width*5,height)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        clock = pygame.time.Clock()
        running = True

        simulate = True
        evolution.start_generation()
        while running:
            self.draw()
            iterations = 10
            dt = 1.0 / float(self.fps) / float(iterations)
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    simulate = False
                if event.type == KEYDOWN and event.key == K_r:
                    simulate = True
            if simulate:
                for x in range(iterations):
                    evolution.step(dt)
                    if evolution.if_end_generation():
                        if evolution.if_end_evolution():
                            evolution.find_best()
                            evolution.save()
                            running = False
                            break
                        else:
                            evolution.next_generation()

            pygame.display.update()
            self.space.step(dt)
            clock.tick(self.fps)


if __name__ == '__main__':
    sim = Simulator()
    evo = Evolution(sim.space,sim.ground_y,sim.fps)
    evo.clear_population()
    # evo.load_population("results/population.txt")
    evo.load_best_indvidual("best_ind_foot.txt",put_to_population=True)
    # evo.load_population("results/problem2/population_problem2.txt")
    # evo.load_best_indvidual("results/problem2/best_ind_problem_2.txt",put_to_population=True)
    sim.main(evo)