from pygame.time import Clock
import pygame
from sys import exit
from src.racecar_game import Game, Controls

controls = {
    pygame.K_i: Controls.FRONT,
    pygame.K_j: Controls.LEFT,
    pygame.K_l: Controls.RIGHT,
    pygame.K_k: Controls.BACK
}


def main():
    player_game()


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
        # print(dt)
        pressed = pygame.key.get_pressed()
        control = []
        for key, action in controls.items():
            if pressed[key]:
                control.append(action)
        response = game.act(control, dt)
        game.render(dt)


if __name__ == '__main__':
    main()
