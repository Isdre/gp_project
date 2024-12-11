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
        self.display_flags = 0
        self.H = 600
        self.display_size = (1000, self.H)

        self.space = pymunk.Space()
        self.space.gravity = (0.0, 981.0)
        # self.space.damping = 0.999 # to prevent it from blowing up.

        # Pymunk physics coordinates start from the lower right-hand corner of the screen.
        self.ground_y = self.H - 50
        #ground = pymunk.Segment(self.space.static_body, (0, self.ground_y), (1000, self.ground_y), 1.0)
        #ground.friction = 1.0
        #self.space.add(ground)

        self.screen = None

        self.draw_options = None

        self.fps = 60

    def create_boundarues(self,width,height):
        rects = [
            [(width/2,height-10),(width*1.5,20)]#,
            #[(width / 2, 10), (width, 20)],
            #[(10, height/2), (20, height)],
            #[(width-10, height/2), (20, height)]
        ]

        for pos,size in rects:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = pos
            shape = pymunk.Poly.create_box(body, size)
            self.space.add(body, shape)

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

        def to_pygame(p):
            return int(p.x), int(p.y + height)  # Small hack to convert pymunk to pygame coordinates

        def from_pygame(p):
            return to_pygame(p)

        clock = pygame.time.Clock()
        running = True
        font = pygame.font.Font(None, 16)

        simulate = True
        while running:
            self.draw()
            iterations = 10
            dt = 1.0 / float(self.fps) / float(iterations)
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_r:
                    simulate = not simulate
            if simulate:
                for x in range(iterations):
                    tinyGP.step()
                    self.space.step(dt)

            pygame.display.update()
            clock.tick(self.fps)


if __name__ == '__main__':
    sim = Simulator()
    tinyGP = TinyGP(sim.space,sim.ground_y,sim.fps)
    sim.main(tinyGP)