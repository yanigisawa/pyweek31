import sys
import pygame as pg
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

class Car:
    def __init__(self, size=(100, 200), mass=1, position=(100, 200)):
        self.body = pymunk.Body()
        # TODO: ADD TO SPACE FROM CALLER space.add(body)

        self.body.position = Vec2d(*position)

        self.shape = pymunk.Poly.create_box(self.body, (size[0], size[1]), 0.0)
        self.shape.mass = mass
        self.shape.friction = 0.7
        # TODO - ADD TO SPACE space.add(self.shape)

    def __str__(self):
        return str(self.body.position)


class Game:
    def __init__(self, screen):
        self._screen = screen
        self._space = pymunk.Space()
        self._space.iterations = 10
        self._space.sleep_time_threshold = 0.5
        self._draw_options = pymunk.pygame_util.DrawOptions(self._screen)
        self._clock = pg.time.Clock()

        self._red_car = Car()
        self._blue_car = Car(position=(300, 400))
        self._space.add(self._red_car.body, self._red_car.shape)
        self._space.add(self._blue_car.body, self._blue_car.shape)

    def _clear_screen(self):
        self._screen.fill(pg.Color("green"))

    def _draw_objects(self):
        self._space.debug_draw(self._draw_options)

    def exit_game(self):
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
            self._clear_screen()
            self._draw_objects()
            self._space.step(1)
            pg.display.flip()
            # Delay fixed time between frames
            self._clock.tick(50)
            pg.display.set_caption("fps: " + str(self._clock.get_fps()))


    def on_keydown(self, event):
        # if event.key == pg.K_ESCAPE:
        #     self.pause()
        if event.key in [pg.K_q, pg.K_ESCAPE]:
            self.exit_game()

        keys = {
            pg.K_LEFT: (-1, 0),
            pg.K_a: (-1, 0),
            pg.K_RIGHT: (1, 0),
            pg.K_d: (1, 0),
            pg.K_UP: (0, -1),
            pg.K_w: (0, -1),
            pg.K_DOWN: (0, 1),
            pg.K_s: (0, 1)
        }

        if event.key in keys:
            v = Vec2d(*keys[event.key]) * 20
            self._blue_car.body.position += v

        # if not self.win and not self.paused and not self.character.done and not self.controls_paused:
        #     if event.key == pygame.K_UP or event.key == pygame.K_w:
        #         self.character.move_up()
        #     elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        #         self.character.move_down()
        #     elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        #         self.character.move_left()
        #     elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        #         self.character.move_right()
        #     elif event.key == pygame.K_x or event.key == pygame.K_SPACE:
        #         self.collision_mgr.interact()
        # elif self.controls_paused and not self.script.idle():
        #     if event.key == pygame.K_x or event.key == pygame.K_SPACE:
        #         self.script.skip_dialogue()


    def on_keyup(self, event):
        pass
        # if not self.win and not self.paused and not self.controls_paused:
        #     if event.key == pygame.K_UP or event.key == pygame.K_w:
        #         self.character.stop_up()
        #     elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        #         self.character.stop_down()
        #     elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        #         self.character.stop_left()
        #     elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        #         self.character.stop_right()
