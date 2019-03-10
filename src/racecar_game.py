import codecs
import heapq
import json
from enum import Enum, unique

import pygame
import pygame.gfxdraw
from pygame.math import Vector2

from src.abstracts import Drawable, Entity
from src.helpers import segment_intersection, rotate_line, translate_shape, rotate_shape

MAX_VEL = 300
ACC = 200
CAR_DIM = Vector2(30, 15)
LASER_LENGTH = 300
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
        self.screen = None
        self.bg = None
        self.sprites = None
        self.logic_buffer = None
        self.level = Level(self)

        if init_graphics:
            pygame.init()
            pygame.display.set_caption('Q-racing')
            self.screen = pygame.display.set_mode(self.level.dimensions)
            self.sprites = Sprites()

        self.entities = []
        self.drawables = []
        self.drawables.append(self.level)
        self.car = Car(self)
        self.entities.append(self.car)
        self.drawables.append(self.car)

    def act(self, actions, dt):
        sensors = {}
        for entity in self.entities:
            sensors = {**sensors, **entity.act(actions, dt)}
        if sensors.get('car', {}).get('colliding', False):
            self.reset()
        return sensors

    def reset(self):
        self.level.reset()
        # TODO: Find a better way to reset car
        self.drawables.remove(self.car)
        self.entities.remove(self.car)
        self.car = Car(self)
        self.entities.append(self.car)
        self.drawables.append(self.car)

    def render(self, dt):
        for drawable in self.drawables:
            drawable.draw(self.screen, dt)
        # Compose layers
        if self.logic_buffer is not None:
            self.screen.blit(self.logic_buffer, (0, 0))
        pygame.display.flip()


class Car(Entity):
    @property
    def z_index(self):
        return 2

    def draw(self, surface, dt):
        car_buf = self.game.sprites.car_sprite.copy()
        if self.colliding:
            car_buf.fill((0, 0, 255))
        car_buf = pygame.transform.rotozoom(car_buf, -self.angle, 1)
        surface.blit(car_buf, self.pos - Vector2(car_buf.get_size()) / 2)

    def __init__(self, game):
        self.game = game
        level = game.level
        print('start: {}'.format(level.start))
        self.pos = Vector2(level.start)
        self.vel = Vector2(0, 0)
        self.angle = level.start_angle
        self.bounding_box = None
        self.colliding = True
        self.since_checkpoint = 0
        self.sensors = {}
        # Make bounding box as array of lines
        w, h = CAR_DIM
        self.box = [(Vector2(0, e), Vector2(w, e)) for e in (0, h)] + [(Vector2(e, 0), Vector2(e, h)) for e in (0, w)]
        self.lasers = self._init_lasers()

    @staticmethod
    def _init_lasers():
        w, h = CAR_DIM
        lasers = {
            'front': [Vector2(w, h / 2), Vector2(w + LASER_LENGTH, h / 2)],
            'front_left': rotate_line([Vector2(w, 0), Vector2(w + LASER_LENGTH, 0)], Vector2(w, 0), -5),
            'front_left_diag': rotate_line([Vector2(w, 0), Vector2(w + LASER_LENGTH, 0)], Vector2(w, 0), -45),
            'front_left_perp': rotate_line([Vector2(w, 0), Vector2(w + LASER_LENGTH, 0)], Vector2(w, 0), -90),
            'front_right': rotate_line([Vector2(w, h), Vector2(w + LASER_LENGTH, h)], Vector2(w, 0), 5),
            'front_right_diag': rotate_line([Vector2(w, h), Vector2(w + LASER_LENGTH, h)], Vector2(w, h), 45),
            'front_right_perp': rotate_line([Vector2(w, h), Vector2(w + LASER_LENGTH, h)], Vector2(w, h), 90),
            'back': [Vector2(0, h / 2), Vector2(-LASER_LENGTH, h / 2)],
            'back_left_diag': rotate_line([Vector2(0, 0), Vector2(-LASER_LENGTH, 0)], Vector2(0, 0), 45),
            'back_right_diag': rotate_line([Vector2(0, h), Vector2(-LASER_LENGTH, h)], Vector2(0, h), -45),
        }
        return lasers

    def act(self, actions, dt):
        self.sensors = {
        }
        self.since_checkpoint += 1
        if self.since_checkpoint > 60 * 3:
            self.sensors['done'] = True
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
        # Translate and rotate
        box = translate_shape(rotate_shape(self.box, CAR_DIM / 2, self.angle), self.pos - CAR_DIM / 2)
        lasers = translate_shape(rotate_shape(self.lasers.values(), CAR_DIM / 2, self.angle), self.pos - CAR_DIM / 2)
        # Collide lasers
        laserdists = []
        for laser in lasers:
            intersections = []
            for wall in self.game.level.wall_lines:
                isect = segment_intersection(laser, wall)
                if isect is not None:
                    heapq.heappush(intersections, ((isect - laser[0]).length(), isect))
            if len(intersections):
                isect = heapq.heappop(intersections)
                # print(isect)
                laserdists.append(isect[0])
                pygame.draw.circle(self.game.logic_buffer, (0, 0, 0), [int(i) for i in isect[1]], 3)
            else:
                laserdists.append(LASER_LENGTH)
            # pygame.draw.line(self.game.logic_buffer, (255, 0, 0), *laser, 2)
        self.sensors['lasers'] = dict(zip(self.lasers.keys(), laserdists))
        for line in box:
            # pygame.draw.line(self.game.logic_buffer, (0, 0, 0), *line, 4)
            for wall in self.game.level.wall_lines:
                if segment_intersection(line, wall) is not None:
                    # pygame.draw.line(self.game.logic_buffer, (0, 0, 0), *wall, 4)
                    self.sensors['done'] = True
                    break
            # Collide with checkpoint
            if segment_intersection(line, self.game.level.current_checkpoint):
                self.sensors['checkpoint'] = True
                self.since_checkpoint = 0
                self.game.level.increment_checkpoint()
        # Collide checkpoint
        # print(self.pos)
        # self.angle += 1
        return self.sense()

    def sense(self):
        self.sensors = {
            'velocity': self.vel.length(),
            **self.sensors
        }
        return {'car': self.sensors}


class Level(Drawable):
    @property
    def z_index(self):
        return -1

    def draw(self, surface, dt):
        if self.bg_buffer is None:
            self._init_bg(self.game)
        # Draw BG buffer
        surface.blit(self.bg_buffer, (0, 0))
        # Current checkpoint
        pygame.draw.line(surface, (0, 255, 0), *self.checkpoints[self._check_idx], 5)

    def _init_bg(self, game):
        # Initialize permanent background buffer
        self.bg_buffer = pygame.Surface(game.screen.get_size())
        self.bg_buffer.fill(Colors.BG)
        # Track, both inner and outer walls
        for layer, color in zip(range(2), (Colors.TRACK, Colors.BG)):
            pygame.gfxdraw.aapolygon(self.bg_buffer, self.walls[layer], color)
            pygame.gfxdraw.filled_polygon(self.bg_buffer, self.walls[layer], color)
        # Checkpoints
        for checkpoint in self.checkpoints:
            pygame.draw.line(self.bg_buffer, Colors.BG, *checkpoint)

    def __init__(self, game):
        self.game = game
        self.walls = []
        self.wall_lines = []
        self.checkpoints = []
        self._check_idx = -1
        self.start = []
        self.start_angle = []
        self.checkpoints_reversed = True
        self.dimensions = (1366, 768)
        self._load_file()
        # Convert wall points into lines
        for walls in self.walls:
            for i in range(0, len(walls)):
                self.wall_lines.append((Vector2(walls[i - 1]), Vector2(walls[i])))
        # Initialize BG buffer
        self.bg_buffer = None

    @property
    def current_checkpoint(self):
        return self.checkpoints[self._check_idx]

    def increment_checkpoint(self):
        self._check_idx = (self._check_idx - 1 if self.checkpoints_reversed else 1) % len(self.checkpoints)

    def reset(self):
        self._check_idx = -1

    def _load_file(self):
        with codecs.open('../assets/levels/level1/level.json', 'r', encoding='UTF-8') as f:
            level = json.load(f)
        self.walls = level['walls']
        self.checkpoints = level['checkpoints']
        self.start = level['start']
        self.start_angle = level['startangle']
