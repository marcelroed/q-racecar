from pygame.time import Clock
import pygame
from sys import exit
from src.racecar_game import Game, Controls

controls = {
    pygame.K_UP: Controls.FRONT,
    pygame.K_LEFT: Controls.LEFT,
    pygame.K_RIGHT: Controls.RIGHT,
    pygame.K_DOWN: Controls.BACK
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
        dt = clock.tick(60) / 1000
        print(dt)
        pressed = pygame.key.get_pressed()
        control = []
        for key, action in controls.items():
            if pressed[key]:
                control.append(action)
        game.act(control, dt)
        game.render()


if __name__ == '__main__':
    main()
