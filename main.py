import sys

import pygame
from pygame.locals import USEREVENT, QUIT, KEYDOWN, KEYUP, K_s, K_r, K_q, K_ESCAPE, K_UP, K_DOWN, K_RIGHT, K_LEFT
from pygame.color import THECOLORS

import pymunk
from pymunk import Vec2d
import pymunk.pygame_util

from Individual.Individual import Individual
from TinyGP.TinyGP import TinyGP

class Simulator:
    def __init__(self):
        self.display_flags = pygame.SCALED
        self.H = 600
        self.display_size = (1000, self.H)

        self.space = pymunk.Space()
        self.space.gravity = (0.0, 981.0 * 8)
        self.space.damping = 0.1 # to prevent it from blowing up.

        # Pymunk physics coordinates start from the lower right-hand corner of the screen.
        self.ground_y = self.H - 50


        self.screen = None

        self.draw_options = None

        self.fps = 30

    def create_boundarues(self,width,height):
        thickness = 5
        rects = [
            [(-thickness,height - thickness),(width + thickness,height - thickness)]#,
            #[(width / 2, 10), (width, 20)],
            #[(10, height/2), (20, height)],
            #[(width-10, height/2), (20, height)]
        ]

        for a,b in rects:
            body = pymunk.Segment(self.space.static_body, a, b, thickness)
            body.friction = 5

            self.space.add(body)

    def reset_bodies(self):
        for body in self.space.bodies:
            if not hasattr(body, 'start_position'):
                continue
            body.position = Vec2d(body.start_position)
            body.force = 0, 0
            body.torque = 0
            body.velocity = 0, 0
            body.angular_velocity = 0
            body.angle = body.start_angle

    def draw(self):
        self.screen.fill(THECOLORS["white"])  ### Clear the screen
        self.space.debug_draw(self.draw_options)  ### Draw space
        pygame.display.update()  ### All done, lets flip the display

    def main(self,tinyGP:TinyGP):
        pygame.init()
        self.screen = pygame.display.set_mode(self.display_size, self.display_flags)
        width, height = self.screen.get_size()
        self.create_boundarues(width,height)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        clock = pygame.time.Clock()
        running = True

        simulate = True
        tinyGP.start_generation()
        while running:
            self.draw()
            iterations = 10
            dt = 1.0 / float(self.fps) / float(iterations)
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_r:
                    simulate = not simulate
            if simulate:
                for x in range(iterations):
                    if not tinyGP.step(dt):
                        tinyGP.next_generation()
            pygame.display.update()
            self.space.step(dt)
            clock.tick(self.fps)


if __name__ == '__main__':
    sim = Simulator()
    tinyGP = TinyGP(sim.space,sim.ground_y,sim.fps)
    sim.main(tinyGP)