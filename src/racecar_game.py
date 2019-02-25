from math import pi
from enum import Enum, unique
from src.helpers import make_len, vec_len, add_to, rot_center
import pygame, pygame.gfxdraw
from pygame.math import Vector2
import codecs, json

MAX_VEL = 20
ACC = 15
TIMESTEP = 1 / 30
CAR_DIM = (20, 50)


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


class Sprites:
    def __init__(self):
        # self.car = pygame.image.load('./assets/textures/car.png')
        self.car_rect = pygame.Rect((0, 0), CAR_DIM)
        self.car_sprite = pygame.Surface(CAR_DIM)
        self.car_sprite = self.car_sprite.convert_alpha()
        self.make_car_sprite()

    def make_car_sprite(self):
        self.car_sprite.fill(Colors.CAR)
        pygame.draw.rect(self.car_sprite, (0, 0, 0, 255), self.car_rect, 2)


class Game:
    def __init__(self):
        self.level = Level()
        self.car = Car(self.level)
        self.screen = None
        self.bg = None
        self.sprites = None

    def act(self, action):
        reward = self.car.act(action, TIMESTEP)
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
                pygame.draw.line(self.bg, (0, 0, 0), *checkpoint)
        # Car
        car_buf = pygame.transform.rotozoom(self.sprites.car_sprite, self.car.dir, 1)
        # Compose layers
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(car_buf, (500, 500))
        pygame.display.flip()


class Car:
    def __init__(self, level):
        self.pos = level.start
        self.vel = [0, 0]
        self.dir = 96

    def act(self, action, timestep):
        if action[Controls.FRONT]:
            self.vel += ACC * timestep

        if vec_len(self.vel) > MAX_VEL:
            make_len(self.vel, MAX_VEL)

        add_to(self.pos, self.vel)

    def sense(self):
        pass


class Level:
    def __init__(self):
        self.walls = []
        self.checkpoints = []
        self.start = []
        self.dimensions = (1366, 768)
        self.load_file()

    def load_file(self):
        with codecs.open('../assets/levels/level1/level.json', 'r', encoding='UTF-8') as f:
            level = json.load(f)
        self.walls = level['walls']
        self.checkpoints = level['checkpoints']
        self.start = level['start']
