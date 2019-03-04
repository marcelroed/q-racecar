from enum import Enum, unique
from src.helpers import segment_intersection
import pygame, pygame.gfxdraw
from pygame.math import Vector2
import codecs, json

MAX_VEL = 300
ACC = 200
CAR_DIM = (30, 15)
TURNSPEED = 200
FRICTION = 0.03
IDLE_BREAK = 0.97


@unique
class Controls(Enum):
    FRONT = 0
    BACK = 1
    LEFT = 2
    RIGHT = 3


class Colors:
    BG = (250, 250, 250, 255)
    TRACK = (80, 80, 80, 255)
    CAR = (255, 0, 0, 255)
    CAR_WINDSHIELD = (0, 255, 255, 255)


class Sprites:
    def __init__(self):
        # self.car = pygame.image.load('./assets/textures/car.png')
        self.car_rect = pygame.Rect((0, 0), CAR_DIM)
        self.car_sprite = pygame.Surface(CAR_DIM)
        self.car_sprite = self.car_sprite.convert_alpha()
        self.make_car_sprite()

    def make_car_sprite(self):
        self.car_sprite.fill(Colors.CAR)
        w, h = CAR_DIM
        self.car_sprite.fill(Colors.CAR_WINDSHIELD, (w - 7, 0, 7, h))
        pygame.draw.rect(self.car_sprite, (0, 0, 0, 255), self.car_rect, 2)


class Game:
    def __init__(self, init_graphics=False):
        self.level = Level()
        self.car = Car(self)
        self.screen = None
        self.bg = None
        self.sprites = None
        self.logic_buffer = None
        if init_graphics:
            self.render()

    def act(self, actions, dt):
        reward = self.car.act(actions, dt)
        sensors = self.car.sense(self.level)
        return sensors, reward

    def render(self):
        if self.screen is None:
            pygame.init()
            pygame.display.set_caption('Q-racing')
            self.screen = pygame.display.set_mode(self.level.dimensions)
            self.sprites = Sprites()
        # Initialize permanent background buffer
        if self.bg is None:
            self.bg = pygame.Surface(self.screen.get_size())
            self.bg.fill(Colors.BG)
            # Track, both inner and outer walls
            for layer, color in zip(range(2), (Colors.TRACK, Colors.BG)):
                pygame.gfxdraw.aapolygon(self.bg, self.level.walls[layer], color)
                pygame.gfxdraw.filled_polygon(self.bg, self.level.walls[layer], color)
            # Checkpoints
            for checkpoint in self.level.checkpoints:
                pygame.draw.line(self.bg, Colors.BG, *checkpoint)
        # Car
        car_buf = self.sprites.car_sprite.copy()
        if self.car.colliding:
            car_buf.fill((0, 0, 255))
        car_buf = pygame.transform.rotozoom(car_buf, -self.car.angle, 1)
        # Compose layers
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(car_buf, self.car.pos - Vector2(car_buf.get_size()) / 2)
        if self.logic_buffer is not None:
            self.screen.blit(self.logic_buffer, (0, 0))
        pygame.display.flip()


class Car:
    def __init__(self, game):
        self.game = game
        level = game.level
        print('start: {}'.format(level.start))
        self.pos = Vector2(level.start)
        self.vel = Vector2(0, 0)
        self.angle = level.start_angle
        self.bounding_box = None
        self.colliding = True
        # Make bounding box as array of lines
        w, h = CAR_DIM
        self.box = [(Vector2(0, e), Vector2(w, e)) for e in (0, h)] + [(Vector2(e, 0), Vector2(e, h)) for e in (0, w)]

    def act(self, actions, dt):
        self.game.logic_buffer = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA, 32)
        self.game.logic_buffer = self.game.logic_buffer.convert_alpha()
        dir = Vector2()
        dir.from_polar((1, self.angle))
        if Controls.FRONT not in actions:
            self.vel *= IDLE_BREAK
        for action in actions:
            if action == Controls.FRONT:
                self.vel += dir * ACC * dt
            if action == Controls.LEFT:
                self.angle -= TURNSPEED * dt
            if action == Controls.RIGHT:
                self.angle += TURNSPEED * dt
            if action == Controls.BACK:
                self.vel -= dir * ACC * dt

        if self.vel.length() > MAX_VEL:
            self.vel = MAX_VEL * self.vel.normalize()

        # Friction
        self.vel -= (self.vel - dir.dot(self.vel) * dir) * FRICTION

        self.pos += self.vel * dt

        # Collision
        self.colliding = False
        box = [[point + self.pos for point in line] for line in self.box]
        for line in box:
            for wall in self.game.level.wall_lines:
                if segment_intersection(line, wall) is not None:
                    pygame.draw.line(self.game.logic_buffer, (0, 0, 0), *wall, 4)
                    # print("Colliding!")
                    self.colliding = True
                    break
        # print(self.pos)
        # self.angle += 1

    def sense(self, level):
        sensors = {}
        # Check collision
        sensors['colliding'] = True
        return sensors


class Level:
    def __init__(self):
        self.walls = []
        self.wall_lines = []
        self.checkpoints = []
        self.start = []
        self.start_angle = []
        self.dimensions = (1366, 768)
        self.load_file()
        # Convert wall points into lines
        all_walls = self.walls[0] + self.walls[1]
        for i in range(0, len(all_walls)):
            self.wall_lines.append((Vector2(all_walls[i - 1]), Vector2(all_walls[i])))

    def load_file(self):
        with codecs.open('../assets/levels/level1/level.json', 'r', encoding='UTF-8') as f:
            level = json.load(f)
        self.walls = level['walls']
        self.checkpoints = level['checkpoints']
        self.start = level['start']
        self.start_angle = level['startangle']
