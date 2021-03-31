import math
import sys
import pygame as pg
from pygame.constants import SCRAP_SELECTION
from pygame.display import update
import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d
from .pygame_functions import *

setAutoUpdate(False)

from . import config



def tuple_add(tup1, tup2):
    return tup1[0] + tup2[0], tup1[1] + tup2[1]

def tuple_subtract(tup1, tup2):
    return tup1[0] - tup2[0], tup1[1] - tup2[1]


class GameWindow:

    def __init__(self):
        screenSize(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
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

class Car(pg.sprite.Sprite):
    def __init__(self, size=(50, 100), mass=1, position=(100, 200), color=(0, 0, 255)):
        super().__init__()
        self.body = pymunk.Body()

        self.body.position = Vec2d(*position)

        self._width, self._height = size
        self.shape = pymunk.Poly.create_box(self.body, (size[0], size[1]), 0.0)
        self.shape.mass = mass
        self.shape.friction = 1

        self.image = pg.Surface(size, pg.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=position)
        self._orig_image = self.image
        self.color = color
        self._velocity = (0, 0)

    def update(self):
        # shape = self.shape
        # ps = [
        #     pos.rotated(shape.body.angle) + shape.body.position
        #     for pos in shape.get_vertices()
        # ]
        # ps.append(ps[0])
        # left, top = ps[3][0], ps[3][1]

        self.image = pg.transform.rotozoom(
            self._orig_image,
            -math.degrees(self.body.angle),
            1
            )
        self.rect = self.image.get_rect(center=self.body.position)

    def draw(self, screen):
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
        new_vel = self.body.velocity - velocity
        self.body.velocity -= velocity


    def move(self, velocity):
        new_vel = self.body.velocity + velocity
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
        self._speed_factor = 15
        self._max_speed = 10
        self._current_speed = 0

        self._red_car = Car(position=(300, 300), color=(255, 0, 0))
        self._space.add(self._red_car.body, self._red_car.shape)
        self._blue_car = Car(position=(350, 576))
        self._space.add(self._blue_car.body, self._blue_car.shape)
        self._shift_key_down = False
        self._background_scroll = (0, 0)
        self._distance_label = makeLabel("Distance: 0", 25, 10, 10, "white")
        self._speed_label = makeLabel("Speed 0 / 10", 25, 10, 60, "white")

        showSprite(self._blue_car)
        showSprite(self._red_car)

    def _calculate_distance(self):
        # dist = math.hypot(x1-x2, y1-y2)
        x1, y1 = self._red_car.body.position
        x2, y2 = self._blue_car.body.position
        return int(math.hypot(x1-x2, y1-y2))

    def _update_objects(self):
        if self._background_scroll is not None:
            scrollBackground(*self._background_scroll)
        distance = self._calculate_distance()
        changeLabel(self._distance_label, f"Distance: {distance}")
        # self._screen.fill(pg.Color((100, 100, 100)))

    def _draw_objects(self):
        self._blue_car.update()
        self._red_car.update()
        updateDisplay()
        # self._space.debug_draw(self._draw_options)
        # self._red_car.draw(self._screen)
        # self._blue_car.draw(self._screen)

    def exit_game(self):
        pg.quit()
        sys.exit()

    def loop(self):
        setBackgroundImage("data/road_tarmac1.png")
        showLabel(self._distance_label)
        showLabel(self._speed_label)

        FPS = 120
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.exit_game()
                elif event.type == pg.KEYDOWN:
                    self.on_keydown(event)
                elif event.type == pg.KEYUP:
                    self.on_keyup(event)
            self._update_objects()
            self._draw_objects()
            self._space.step(1 / FPS)
            self._clock.tick(FPS)
            pg.display.set_caption("fps: " + str(self._clock.get_fps()))

    @property
    def keys_bak(self):
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

    def _increase_velocity(self):
        if self._current_speed >= self._max_speed:
            return

        self._current_speed += 1
        increment = self._max_speed / self._speed_factor
        self._background_scroll = self._background_scroll[0], math.ceil(self._background_scroll[1] + increment)
        changeLabel(self._speed_label, f"Speed: {self._current_speed} / {self._max_speed}")

    def _decrease_velocity(self):
        if self._background_scroll[1] < 1:
            return

        self._current_speed -= 1
        increment = self._max_speed / self._speed_factor
        self._background_scroll = self._background_scroll[0], math.floor(self._background_scroll[1] - increment)
        changeLabel(self._speed_label, f"Speed: {self._current_speed} / {self._max_speed}")


    @property
    def keys(self):
        move_left = {"movement": (self._speed_factor, 0),  "action": None}
        move_right = {"movement": (-self._speed_factor, 0), "action": None}
        move_up = {"movement": (0, self._speed_factor),  "action": self._increase_velocity}
        move_down = {"movement": (0, -self._speed_factor),  "action": self._decrease_velocity}
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
        if event.key in [pg.K_ESCAPE]:
            self.exit_game()

        if event.key == pg.K_RSHIFT:
            self._shift_key_down = True

        if event.key in self.keys:
            if self._shift_key_down:
                self._blue_car.body.angle = 0
                self._blue_car.body.angular_velocity = 0
                # direction = self.keys[event.key]["rotation"] * (math.pi / 3)
                # self._blue_car.body.angular_velocity = direction
                return

            if self.keys[event.key]["action"] is not None:
                self.keys[event.key]["action"]()
                return

            self._background_scroll = tuple_add(self._background_scroll, self.keys[event.key]["movement"])
            # self._blue_car.move(self.keys[event.key]["velocity"])

        if event.key == pg.K_SPACE:
            self._blue_car.body.angular_velocity = 0
            self._blue_car.body.velocity = 0, 0


    def on_keyup(self, event):

        if event.key == pg.K_RSHIFT:
            self._shift_key_down = False

        if event.key in self.keys:
            if event.key in [pg.K_LEFT, pg.K_RIGHT] and self._shift_key_down:
                self._blue_car.body.angular_velocity = 0
                self._blue_car.body.angle = 0
                return

            if self.keys[event.key]["action"] is not None:
                self.keys[event.key]["action"]()
                return

            self._background_scroll = tuple_subtract(self._background_scroll, self.keys[event.key]["movement"])
            # self._blue_car.stop(self.keys[event.key]["velocity"])

        # if not self.win and not self.paused and not self.controls_paused:
        #     if event.key == pygame.K_UP or event.key == pygame.K_w:
        #         self.character.stop_up()
        #     elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        #         self.character.stop_down()
        #     elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        #         self.character.stop_left()
        #     elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        #         self.character.stop_right()
