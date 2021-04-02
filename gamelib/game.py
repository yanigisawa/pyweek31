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

FPS = 60


def tuple_mult(tup1, factor):
    return tup1[0] * factor, tup1[1] * factor

def tuple_add_vect(tup1, tup2):
    return pygame.Vector2((tup1[0] + tup2[0], tup1[1] + tup2[1]))


def tuple_add(tup1, tup2):
    return tup1[0] + tup2[0], tup1[1] + tup2[1]

def tuple_subtract(tup1, tup2):
    return tup1[0] - tup2[0], tup1[1] - tup2[1]


class GameWindow:

    def __init__(self):
        screenSize(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        pg.display.set_caption('TODO')
        self.screen = pg.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        try:
            pg.mixer.init()
            # pg.mixer.music.load("data/engine.ogg")
            # pg.mixer.music.play(-1)
        except:
            pass

        # self.restart = True
        # self.intro()
        self.game()

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
    def __init__(
        self,
        size=(50, 100),
        mass=1,
        position=(100, 200),
        color=(0, 0, 255),
        collision_type=1,
        file_name=None
    ):
        # super().__init__()
        pg.sprite.Sprite.__init__(self)
        self.body = pymunk.Body()

        self.body.position = Vec2d(*position)

        self._width, self._height = size
        self.shape = pymunk.Poly.create_box(self.body, (size[0], size[1]), 0.0)
        self.shape.mass = mass
        self.shape.elasticity = 0
        self.shape.friction = 1
        self.shape.collision_type = collision_type

        if file_name is not None:
            self._file_name = file_name
            self._load_image()
        else :
            self.image = pg.Surface(size, pg.SRCALPHA)
            self.image.fill(color)
        # self.image = loadImage("data/cop.png")
        self.rect = self.image.get_rect(center=position)
        self._orig_image = self.image
        self.color = color

    def _load_image(self):
        img = loadImage(self._file_name)
        x = 0
        frameSurf = pygame.Surface((img.get_width(), img.get_height()), pygame.SRCALPHA, 32)
        frameSurf.blit(img, (x, 0))
        self.image = pygame.Surface.copy(frameSurf.copy())
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = 0
        self.scale = 1



    @property
    def collision_type(self):
        return self.shape.collision_type

    def apply_force(self, direction):
        move = pygame.Vector2((0, 0))
        move = tuple_add_vect(move, direction)

        impulse = tuple_mult(move, 500)
        if move.length() > 0: move.normalize_ip()
        # self.body.apply_impulse_at_local_point(impulse, self.body.center_of_gravity)
        self.body.apply_force_at_local_point(impulse, self.body.center_of_gravity)
        # self.body.velocity = impulse

        # if you used pymunk before, you'll probably already know
        # that you'll have to invert the y-axis to convert between
        # the pymunk and the pygame coordinates.
        self.pos = pygame.Vector2(self.body.position[0], -self.body.position[1] + config.SCREEN_HEIGHT)
        self.rect.center = self.pos

    def apply_impulse(self, direction):
        move = pygame.Vector2((0, 0))
        move = tuple_add_vect(move, direction)

        impulse = tuple_mult(move, 100)
        if move.length() > 0: move.normalize_ip()
        self.body.apply_impulse_at_local_point(impulse, self.body.center_of_gravity)
        # self.body.apply_force_at_local_point(impulse, self.body.center_of_gravity)

        # if you used pymunk before, you'll probably already know
        # that you'll have to invert the y-axis to convert between
        # the pymunk and the pygame coordinates.
        self.pos = pygame.Vector2(self.body.position[0], -self.body.position[1] + config.SCREEN_HEIGHT)
        self.rect.center = self.pos


    def update(self):
        # pass
        self.image = pg.transform.rotozoom(
            self._orig_image,
            -math.degrees(self.body.angle), 1
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

    # def stop(self, velocity):
    #     new_vel = self.body.velocity - velocity
    #     self.body.velocity -= velocity


    # def move(self, velocity):
    #     new_vel = self.body.velocity + velocity
    #     self.body.velocity += velocity

    def __str__(self):
        return str(self.body.position)

class EnemyCar(Car):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.body.velocity = (0, 0)
        self._have_collided = False

    def set_collided(self):
        # self.image = pg.Surface((self._width, self._height), pg.SRCALPHA)
        # self.image.fill((200, 0, 200))
        # self.rect = self.image.get_rect(center=self.body.position)
        # self._orig_image = self.image
        self._have_collided = True


    def update_for_player_movement(self, player, background_scroll):
        # Right is negative
        # Left is positive
        current = self.body.position
        mult = 1
        new_pos = Vec2d(
            current[0] + background_scroll[0] * mult, current[1] + background_scroll[1] * mult)
        if background_scroll[0] == 0 and background_scroll[1] == 0:
            return

        # new_vel =(new_pos - current) / 1 / FPS
        self.body.position = new_pos
        self.body.velocity = (new_pos - current) / 1 / FPS


    def perform_ai(self):
        if self._have_collided:
            return
        self.body.velocity = (0, -150)

class Game:
    def __init__(self, screen):
        self._screen = screen
        self._draw_options = pymunk.pygame_util.DrawOptions(self._screen)
        self._clock = pg.time.Clock()
        self._speed_factor = 5
        self._speed_increment = 0
        self._max_speed_increment = 10
        self._side_scroll_factor = 2
        self._player_position_speed = 5
        self._distance_label = makeLabel("Distance: 0", 25, 10, 10, "white")
        self._speed_label = makeLabel("Speed 0 / 10", 25, 10, 60, "white")
        self._enemy_angle = makeLabel("Perp: 0", 25, 10, 110, "white")
        self._self_angle = makeLabel("Cop: 0", 25, 10, 160, "white")
        self._velocity_label = makeLabel("Velocity: 0", 25, 10, 210, "white")
        self._player_position = (350, 476)
        self._engine_start_sound = pygame.mixer.Sound(config.ENGINE_START)
        self._engine_idle_sound = pg.mixer.Sound(config.ENGINE_IDLE)
        self._engine_running = pg.mixer.Sound(config.ENGINE_RUNNING)
        self._base_volume = 0.03
        self._engine_running.set_volume(self._base_volume)
        self._car_crash_sound = pg.mixer.Sound(config.CAR_CRASH)
        self._sound_on = True

        showLabel(self._distance_label)
        showLabel(self._speed_label)
        showLabel(self._enemy_angle)
        showLabel(self._self_angle)
        showLabel(self._velocity_label)
        self._reset()

    def collision_post_solve(self, arbitor, space, data):
        self._red_car.set_collided()
        self._have_collided = True
        self._speed_increment = 0
        self._play_crashed()

    def add_pivots(self):
        cars = [self._red_car, self._blue_car]
        for car in cars:
            pivot = pymunk.PivotJoint(self._space.static_body, car.body, (0, 0), (0, 0))
            self._space.add(pivot)
            pivot.max_bias = 0  # disable joint correction
            pivot.max_force = 2000 # emulate linear friction

            gear = pymunk.GearJoint(self._space.static_body, car.body, 0.0, 1.0)
            self._space.add(gear)
            gear.max_bias = 0  # disable joint correction
            gear.max_force = 2000  # emulate angular friction

    def _play_crashed(self):
        if not self._sound_on:
            return
        self._engine_running.stop()
        if not pg.mixer.get_busy():
            self._car_crash_sound.play()

    def _play_engine_idle(self):
        if not self._sound_on:
            return
        self._engine_idle_sound.play(-1)

    def _play_engine_running(self):
        if not self._sound_on:
            return
        pg.mixer.stop()
        self._engine_running.play(-1)

    def _play_engine_start(self):
        if not self._sound_on:
            return
        pg.mixer.stop()
        self._engine_start_sound.play()

    def _reset(self):
        hideAll()
        setBackgroundImage(config.BACKGROUND_IMAGE)
        self._play_engine_start()
        self._play_engine_idle()

        self._space = pymunk.Space()

        self._speed_increment = 0

        # self._red_car = EnemyCar(position=(200, 200), color=(200, 0, 0))
        self._red_car = EnemyCar(position=(200, 200), file_name="data/perp.png")
        self._space.add(self._red_car.body, self._red_car.shape)
        # self._blue_car = Car(position=self._player_position)
        self._blue_car = Car(position=self._player_position, file_name="data/cop.png")
        self._space.add(self._blue_car.body, self._blue_car.shape)
        self._have_collided = False

        self.add_pivots()

        collision_handler = self._space.add_collision_handler(self._red_car.collision_type, self._blue_car.collision_type)
        collision_handler.post_solve = self.collision_post_solve

        self._shift_key_down = False
        self._background_scroll = (0, 0)
        changeLabel(self._speed_label, f"Speed: {self._speed_increment} / {self._max_speed_increment}")

        showSprite(self._blue_car)
        showSprite(self._red_car)

    def _calculate_distance(self):
        x1, y1 = self._red_car.body.position
        x2, y2 = self._blue_car.body.position
        return int(math.hypot(x1-x2, y1-y2))


    def _correct_player_position(self):
        if self._blue_car.body.position == self._player_position:
            return
        distance = self._blue_car.body.position.get_distance(self._player_position)
        t = 1
        if distance < self._player_position_speed:
            self._blue_car.body.position = self._player_position
        else:
            t = self._player_position_speed / distance
        new = self._blue_car.body.position.interpolate_to(self._player_position, t)
        self._blue_car.body.position = new
        self._blue_car.body.velocity = (new - self._blue_car.body.position) / 1 / FPS

    def _update_scroll_for_velocity(self):
        y_mult = .01
        x_mult = .03
        x_vel = -math.ceil(self._blue_car.body.velocity[0] * x_mult)
        y_vel = -math.ceil(self._blue_car.body.velocity[1] * y_mult)
        self._background_scroll = x_vel, y_vel

    def _apply_velocity(self):
        mult = 80
        # if self._red_car.body.velocity[1] < 0:
        #     self.
        if self._speed_increment <=0:
            return
        if abs(self._blue_car.body.velocity[1]) < self._speed_increment * mult:
            self._blue_car.apply_force((0, -self._speed_factor))


    def _update_objects(self):
        self._update_scroll_for_velocity()
        self._apply_velocity()
        if self._background_scroll is not None:
            scrollBackground(*self._background_scroll)
        # self._update_background()
        distance = self._calculate_distance()
        changeLabel(self._distance_label, f"Distance: {distance}")
        changeLabel(self._enemy_angle, f"Perp Angle: {math.degrees(self._red_car.body.angle)}")
        changeLabel(self._self_angle, f"Cop Angle: {math.degrees(self._blue_car.body.angle)}")
        changeLabel(self._speed_label, f"Speed: {self._speed_increment} / {self._max_speed_increment}")
        changeLabel(self._velocity_label, f"VEL: {self._red_car.body.angular_velocity}")
        self._red_car.update_for_player_movement(self._blue_car, self._background_scroll)
        self._red_car.perform_ai()
        self._blue_car.body.position = self._player_position
        self._space.reindex_shapes_for_body(self._red_car.body)
        self._space.reindex_shapes_for_body(self._blue_car.body)
        # self._screen.fill(pg.Color((100, 100, 100)))

    def _draw_objects(self):
        self._blue_car.update()
        self._red_car.update()
        updateDisplay()
        # DEBUGGING PHYSICS
        # self._space.debug_draw(self._draw_options)
        # pg.display.flip()
        # self._red_car.draw(self._screen)
        # self._blue_car.draw(self._screen)

    def exit_game(self):
        pg.quit()
        sys.exit()

    def loop(self):
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
            dt = self._clock.tick(FPS)
            self._space.step(dt / 1000)
            pg.display.set_caption("fps: " + str(self._clock.get_fps()))

    def _increase_velocity(self):
        if self._speed_increment >= self._max_speed_increment:
            return

        if self._speed_increment == 0:
            self._play_engine_running()

        self._engine_running.set_volume(self._base_volume + (self._speed_increment / 100))
        self._speed_increment += 1
        self._blue_car.apply_force((0, -self._speed_factor))

    def _decrease_velocity(self):
        if self._speed_increment < 1:
            self._background_scroll = self._background_scroll[0], 0
            self._play_engine_idle()
            return

        self._speed_increment -= 1
        self._engine_running.set_volume(self._base_volume - (self._speed_increment / 100))
        self._blue_car.apply_force((0, self._speed_factor))

    def _increase_strafe_velocity(self):
        self._blue_car.apply_impulse((self._speed_factor * .5, 0))

    def _decrease_strafe_velocity(self):
        self._blue_car.apply_impulse((-self._speed_factor * .5, 0))

    @property
    def keys(self):
        move_left = {"movement": (-self._speed_factor, 0),  "action": self._decrease_strafe_velocity}
        move_right = {"movement": (self._speed_factor, 0), "action": self._increase_strafe_velocity}
        move_up = {"movement": (0, -self._speed_factor), "action": self._increase_velocity}
        move_down = {"movement": (0, self._speed_factor),  "action": self._decrease_velocity}
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

        if event.key == pg.K_r:
            self._reset()

        if self._have_collided:
            return

        if event.key == pg.K_RSHIFT:
            self._shift_key_down = True

        if event.key == pg.K_SPACE:
            self._blue_car.body.angular_velocity = 0
            self._blue_car.body.velocity = 0, 0
            self._background_scroll = 0, 0



    def on_keyup(self, event):

        if event.key == pg.K_RSHIFT:
            self._shift_key_down = False

        if event.key in self.keys:
            if event.key in [pg.K_LEFT, pg.K_RIGHT] and self._shift_key_down:
                self._blue_car.body.angular_velocity = 0
                self._blue_car.body.angle = 0
                return

            if self._have_collided:
                return

            if self.keys[event.key]["action"] is not None:
                self.keys[event.key]["action"]()
                return

            # self._background_scroll = tuple_subtract(self._background_scroll, self.keys[event.key]["movement"])
            # self._blue_car.apply_impulse(self.keys[event.key]["movement"])

        # if not self.win and not self.paused and not self.controls_paused:
        #     if event.key == pygame.K_UP or event.key == pygame.K_w:
        #         self.character.stop_up()
        #     elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        #         self.character.stop_down()
        #     elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        #         self.character.stop_left()
        #     elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        #         self.character.stop_right()
