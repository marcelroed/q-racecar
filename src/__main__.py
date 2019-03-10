from sys import exit

import numpy as np
import pygame
from pygame.time import Clock

from src.agent import CarAgent
from src.racecar_game import Game, Controls

controls = {
    pygame.K_i: Controls.FRONT,
    pygame.K_j: Controls.LEFT,
    pygame.K_l: Controls.RIGHT,
    pygame.K_k: Controls.BACK
}


def main():
    # cProfile.run('player_game()', sort='tottime')
    # player_game()
    ai_game()


def player_game():
    game = Game(init_graphics=True)
    clock = Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT, {}))

        dt = clock.tick(60) / 1000
        pressed = pygame.key.get_pressed()
        control = []
        for key, action in controls.items():
            if pressed[key]:
                control.append(action)
        response = game.act(control, dt)
        print(response)
        game.render(dt)


def ai_game():
    game = Game(init_graphics=True)
    clock = Clock()
    state_shape, action_shape = [10, 4]
    agent = CarAgent(state_shape, action_shape)
    state = np.reshape(unpack_response(game.car.sense())[0], (1, state_shape))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
        dt = clock.tick(60) / 1000  # Only used to force at most 60 fps
        dt = 1 / 60
        actions = agent.act(state)
        next_state, reward, done = unpack_response(agent.act(actions, dt))
        reward = reward if not done else -10
        agent.remember(state, actions, reward, next_state, done)
        state = next_state


def unpack_response(response):
    car = response.get('car', {})
    done = car.pop('done', False)
    reward = car.pop('reward', None)
    state = list(car.values())
    print(state)
    return state, reward, done



if __name__ == '__main__':
    main()
