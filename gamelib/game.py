import math
import sys
import pygame as pg
from pygame.constants import SCRAP_SELECTION
import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d

from . import config

class GameWindow:

    def __init__(self):
        pg.display.set_caption('TODO')
        self.screen = pg.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.game()
        # try:
        #     pg.mixer.init()
        #     pg.mixer.music.load(data.filepath("TODO.ogg"))
        #     pg.mixer.music.play(-1)
        # except:
        #     pass
        # self.restart = True
        # self.intro()

    # def intro(self):
    #     while self.restart:
    #         title = Title(self, self.screen)
    #         title.loop()
    #         self.game()

    def game(self):
        game = Game(self.screen)
        game.loop()
        # if game.win:
        #     pg.mixer.music.load(data.filepath("sad-trio.ogg"))
        #     pg.mixer.music.play(-1)
        #     ending = Ending(self, self.screen)
        #     ending.loop()

def get_pygame_coordinates_from_position(position):
    return int(position[0]), config.SCREEN_HEIGHT - int(position[1]) # - config.SCREEN_HEIGHT

def flipy(p):
    """Convert chipmunk coordinates to pygame coordinates."""
    return Vec2d(p[0], config.SCREEN_HEIGHT - p[1])


class Car(pg.sprite.Sprite):
    def __init__(self, size=(50, 100), mass=1, position=(100, 200), color=(0, 0, 255)):
        self.body = pymunk.Body()

        self.body.position = Vec2d(*position)

        self._width, self._height = size
        self.shape = pymunk.Poly.create_box(self.body, (size[0], size[1]), 0.0)
        self.shape.mass = mass
        self.shape.friction = 1

        self.image = pg.Surface(size, pg.SRCALPHA)
        self.image.fill(color)
        self._orig_image = self.image
        self.color = color
        self._velocity = (0, 0)

    def draw(self, screen):
        left, top = get_pygame_coordinates_from_position(self.body.position)
        left = left - self._width / 2
        top = top - self._height / 2

        shape = self.shape
        ps = [
            pos.rotated(shape.body.angle) + shape.body.position
            for pos in shape.get_vertices()
        ]
        ps.append(ps[0])
        left, top = ps[3][0], ps[3][1]

        self.image = pg.transform.rotozoom(
            self._orig_image,
            -math.degrees(self.body.angle),
            1
            )
        rect = self.image.get_rect(center=self.body.position)
        screen.blit(self.image, rect)

    def stop(self, velocity):
        if self._left_right_vel == 0 and self._up_down_vel == 0:
            return

        self._left_right_vel = velocity[0] # ["left"]
        self._up_down_vel = velocity[1] # ["down"]
        self.body.velocity -= velocity


    def move(self, velocity):
        if self._left_right_vel != 0 and self._up_down_vel != 0:
            return
        self._left_right_vel = velocity[0] # ["left"]
        self._up_down_vel = velocity[1] # ["down"]
        self.body.velocity += velocity

    def __str__(self):
        return str(self.body.position)


class Game:
    def __init__(self, screen):
        self._screen = screen
        self._space = pymunk.Space()
        self._space.iterations = 20
        self._space.sleep_time_threshold = 0.5
        self._draw_options = pymunk.pygame_util.DrawOptions(self._screen)
        self._clock = pg.time.Clock()

        self._red_car = Car(position=(200, 200), color=(255, 0, 0))
        self._space.add(self._red_car.body, self._red_car.shape)
        self._blue_car = Car(position=(350, 350))
        self._space.add(self._blue_car.body, self._blue_car.shape)
        self._rotate = False

    def _clear_screen(self):
        self._screen.fill(pg.Color((100, 100, 100)))

    def _draw_objects(self):
        # self._space.debug_draw(self._draw_options)
        self._red_car.draw(self._screen)
        self._blue_car.draw(self._screen)

    def exit_game(self):
        pg.quit()
        sys.exit()

    def loop(self):
        FPS = 50
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.exit_game()
                elif event.type == pg.KEYDOWN:
                    self.on_keydown(event)
                elif event.type == pg.KEYUP:
                    self.on_keyup(event)
            self._clear_screen()
            self._draw_objects()
            self._space.step(1 / FPS)
            pg.display.flip()
            # Delay fixed time between frames
            self._clock.tick(FPS)
            # pg.display.set_caption("fps: " + str(self._clock.get_fps()))

    @property
    def keys(self):
        move_factor = 150
        move_left = {
            "velocity": (-move_factor, 0),
            "rotation": -1
        }
        move_right = {
            "velocity": (move_factor, 0),
            "rotation": 1
        }
        move_up = {
            "velocity": (0, -move_factor),
            "rotation": 0
        }
        move_down = {
            "velocity": (0, move_factor),
            "rotation": 0
        }
        return {
            pg.K_LEFT: move_left,
            pg.K_a: move_left,
            pg.K_RIGHT: move_right,
            pg.K_d: move_right,
            pg.K_UP: move_up,
            pg.K_w: move_up,
            pg.K_DOWN: move_down,
            pg.K_s: move_down
        }

    def on_keydown(self, event):
        # if event.key == pg.K_ESCAPE:
        #     self.pause()
        if event.key in [pg.K_ESCAPE]:
            self.exit_game()


        if event.key == pg.K_RSHIFT:
            self._rotate = True

        if event.key in self.keys:
            if self._rotate:
                direction = self.keys[event.key]["rotation"] * (math.pi / 3)
                self._blue_car.body.angular_velocity = direction
                return

            # v = Vec2d(*keys[event.key]["velocity"]) * 20
            # self._blue_car.body.position += v
            self._blue_car.move(self.keys[event.key]["velocity"])
            # self._blue_car.body.velocity += self.keys[event.key]["velocity"]

        if event.key == pg.K_SPACE:
            self._blue_car.body.angular_velocity = 0
            self._blue_car.body.velocity = 0, 0



    def on_keyup(self, event):
        if event.key == pg.K_RSHIFT:
            self._rotate = False

        if event.key in self.keys:
            if event.key in [pg.K_LEFT, pg.K_RIGHT]:
                self._blue_car.body.angular_velocity = 0

            if self._rotate:
                return

            self._blue_car.stop(self.keys[event.key]["velocity"])

        # if not self.win and not self.paused and not self.controls_paused:
        #     if event.key == pygame.K_UP or event.key == pygame.K_w:
        #         self.character.stop_up()
        #     elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        #         self.character.stop_down()
        #     elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        #         self.character.stop_left()
        #     elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        #         self.character.stop_right()
