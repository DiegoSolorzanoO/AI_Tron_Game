import pygame
import sys
from pygame.locals import *

pygame.init()

FPS = 60
SPEED = 2
FramePerSec = pygame.time.Clock()

COLORS = {
    'BLACK': (0, 0, 0),
    'BLUE': (0, 0, 255),
    'RED': (255, 0, 0)
}

MAX_DISPLAY_SIZE = 600
DISPLAY_SURFACE = pygame.display.set_mode((MAX_DISPLAY_SIZE, MAX_DISPLAY_SIZE))
DISPLAY_SURFACE.fill(COLORS['BLACK'])

pygame.display.set_caption('Tron Game')

pygame.draw.rect(DISPLAY_SURFACE, COLORS['RED'], (200, 100, 10, 10))


class Player:
    def __init__(self, color, speed, size=10):
        self.speed = speed
        self.direction = (1, 0, 'right')
        self.position = (200, 200)
        self.size = size
        self.color = color
        self.tail = {}

    def update(self):
        # Adds position to tail
        self.tail[(
            self.position[0],
            self.position[1]
        )] = 1

        # Sets next position
        self.position = (
            self.position[0] + self.direction[0] * self.speed,
            self.position[1] + self.direction[1] * self.speed
        )

        # Checks if touching itself or touching boundaries
        if (self.position[0], self.position[1]) in self.tail:
            self.color = COLORS['BLUE']
        if self.position[0] < 0 or self.position[0] > MAX_DISPLAY_SIZE:
            self.color = COLORS['BLUE']
        if self.position[1] < 0 or self.position[1] > MAX_DISPLAY_SIZE:
            self.color = COLORS['BLUE']

        # Checks key pressed for new direction
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT] and not self.direction[2] == 'right':
            self.direction = (-1, 0, 'left')
            return
        if pressed_keys[K_RIGHT] and not self.direction[2] == 'left':
            self.direction = (1, 0, 'right')
            return
        if pressed_keys[K_UP] and not self.direction[2] == 'down':
            self.direction = (0, -1, 'up')
            return
        if pressed_keys[K_DOWN] and not self.direction[2] == 'up':
            self.direction = (0, 1, 'down')
            return

    def draw(self, surface):
        # Draw new position
        pygame.draw.rect(surface, self.color, (
            self.position[0], self.position[1],
            self.size, self.size
        ))

        # Draw tail
        for tail_block in self.tail.keys():
            m = self.size / 2
            pygame.draw.rect(
                surface,
                self.color,
                (
                    tail_block[0]+m/2,
                    tail_block[1]+m/2,
                    m,
                    m
                )
            )


player = Player(COLORS['RED'], SPEED)

while True:
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    player.update()

    DISPLAY_SURFACE.fill(COLORS['BLACK'])

    player.draw(DISPLAY_SURFACE)

    FramePerSec.tick(FPS)
