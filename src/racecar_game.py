from enum import Enum, unique
import pygame
import codecs, json


@unique
class Controls(Enum):
    FRONT = 0
    BACK = 1
    LEFT = 2
    RIGHT = 3


MAX_VEL = 20
ACC = 15


class Game:
    def __init__(self):
        self.level = Level()
        self.car = Car()
        self.window = None

    def act(self, action):
        reward = self.car.act(action)
        sensors = self.car.sense(self.level)
        return sensors, reward

    def render(self):
        if self.screen is None:
            pygame.init()
            pygame.display.set_caption('Q-racing')
            self.window = pygame.display.set_mode(self.level.dimensions)


class Car:
    def __init__(self, level):
        self.pos = level.start
        self.vel = [0, 0]

    def act(self, action):
        if action[Controls.FRONT]:
            self.vel


class Level:
    def __init__(self):
        self.walls = []
        self.checkpoints = []
        self.dimensions = (1366, 768)
        self.load_file()

    def load_file(self):
        with codecs.open('../assets/levels/level1/level.json', 'r', encoding='UTF-8') as f:
            level = json.load(f)
        self.walls = level['walls']
        self.checkpoints = level['checkpoints']
