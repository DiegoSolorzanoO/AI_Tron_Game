import pygame
import sys
from pygame.locals import *
import math

pygame.init()

FPS = 60
SPEED = 2
FramePerSec = pygame.time.Clock()

COLORS = {
    'BLACK': (0, 0, 0),
    'BLUE': (0, 0, 255),
    'RED': (255, 0, 0),
    'WHITE': (255, 255, 255)
}

MAX_DISPLAY_SIZE = 600
DISPLAY_SURFACE = pygame.display.set_mode((MAX_DISPLAY_SIZE, MAX_DISPLAY_SIZE))
DISPLAY_SURFACE.fill(COLORS['BLACK'])

pygame.display.set_caption('tron game')

pygame.draw.rect(DISPLAY_SURFACE, COLORS['RED'], (200, 100, 10, 10))

OPPOSITES = {
    'right': 'left',
    'left': 'right',
    'up': 'down',
    'down': 'up'
}

DIR_NEIGHBORS = {
    'left': ['up', 'down'],
    'right': ['up', 'down'],
    'up': ['left', 'right'],
    'down': ['left', 'right']
}


class Player:
    def __init__(self, color, speed, size=10):
        self.speed = speed
        self.direction = (0, 1, 'down')
        self.position = (300, 100)
        self.size = size
        self.color = color
        self.tail = {}

    def update(self, enemy):
        # adds position to tail
        self.tail[(
            self.position[0],
            self.position[1]
        )] = 1

        # sets next position
        self.position = (
            self.position[0] + self.direction[0] * self.speed,
            self.position[1] + self.direction[1] * self.speed
        )

        # checks if touching itself or touching boundaries
        if (self.position[0], self.position[1]) in self.tail or (self.position[0], self.position[1]) in enemy.tail:
            self.color = COLORS['WHITE']
        if self.position[0] < 0 or self.position[0] > MAX_DISPLAY_SIZE:
            self.color = COLORS['WHITE']
        if self.position[1] < 0 or self.position[1] > MAX_DISPLAY_SIZE:
            self.color = COLORS['WHITE']

        # checks key pressed for new direction
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
        # draw new position
        pygame.draw.rect(surface, self.color, (
            self.position[0], self.position[1],
            self.size, self.size
        ))

        # draw tail
        for tail_block in self.tail.keys():
            m = self.size / 2
            pygame.draw.rect(
                surface,
                self.color,
                (
                    tail_block[0] + m / 2,
                    tail_block[1] + m / 2,
                    m,
                    m
                )
            )


class Enemy:

    wide_range = 0.1
    close_range = 0.015

    def __init__(self, color, speed, size=10):
        self.speed = speed
        self.direction = (0, -1, 'up')
        self.position = (300, 500)
        self.size = size
        self.color = color
        self.tail = {}

    def update(self, player):
        # adds position to tail
        self.tail[(
            self.position[0],
            self.position[1]
        )] = 1

        # sets next position
        self.position = (
            self.position[0] + self.direction[0] * self.speed,
            self.position[1] + self.direction[1] * self.speed
        )

        # checks if touching itself or touching boundaries
        if (self.position[0], self.position[1]) in self.tail or (self.position[0], self.position[1]) in player.tail:
            self.color = COLORS['WHITE']
        if self.position[0] < 0 or self.position[0] > MAX_DISPLAY_SIZE:
            self.color = COLORS['WHITE']
        if self.position[1] < 0 or self.position[1] > MAX_DISPLAY_SIZE:
            self.color = COLORS['WHITE']

        weights = {
            'left': 0,
            'right': 0,
            'up': 0,
            'down': 0
        }

        # boundaries weight check
        if MAX_DISPLAY_SIZE - self.position[0] < MAX_DISPLAY_SIZE * self.close_range:
            weights['right'] += 2
        elif MAX_DISPLAY_SIZE - self.position[0] < MAX_DISPLAY_SIZE * self.wide_range:
            weights['right'] += 1

        if self.position[0] < MAX_DISPLAY_SIZE * self.close_range:
            weights['left'] += 2
        elif self.position[0] < MAX_DISPLAY_SIZE * self.wide_range:
            weights['left'] += 1

        if self.position[1] < MAX_DISPLAY_SIZE * self.close_range:
            weights['up'] += 2
        elif self.position[1] < MAX_DISPLAY_SIZE * self.wide_range:
            weights['up'] += 1

        if MAX_DISPLAY_SIZE - self.position[1] < MAX_DISPLAY_SIZE * self.close_range:
            weights['down'] += 2
        elif MAX_DISPLAY_SIZE - self.position[1] < MAX_DISPLAY_SIZE * self.wide_range:
            weights['down'] += 1

        area_sensor = int(MAX_DISPLAY_SIZE * self.close_range)
        area_sensor_wide = int(MAX_DISPLAY_SIZE * self.wide_range * 1.3)

        # Self tail weight check
        close_to_right = False
        close_to_left = False
        close_to_up = False
        close_to_down = False
        for i in range(0, area_sensor):
            if 'right' != OPPOSITES[self.direction[2]]:
                if (self.position[0] + i, self.position[1]) in self.tail and not close_to_right:
                    close_to_right = True
                    weights['right'] += 2
                    weights['up'] += 1
                    weights['down'] += 1
            if 'left' != OPPOSITES[self.direction[2]]:
                if (self.position[0] - i, self.position[1]) in self.tail and not close_to_left:
                    close_to_left = True
                    weights['left'] += 2
                    weights['up'] += 1
                    weights['down'] += 1
            if 'up' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] - i) in self.tail and not close_to_up:
                    close_to_up = True
                    weights['up'] += 2
                    weights['left'] += 1
                    weights['right'] += 1
            if 'down' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] + i) in self.tail and not close_to_down:
                    close_to_down = True
                    weights['down'] += 2
                    weights['left'] += 1
                    weights['right'] += 1

        close_to_right = False
        close_to_left = False
        close_to_up = False
        close_to_down = False
        for i in range(area_sensor, area_sensor_wide):
            if 'right' != OPPOSITES[self.direction[2]]:
                if (self.position[0] + i, self.position[1]) in self.tail and not close_to_right:
                    close_to_right = True
                    weights['right'] += 1
            if 'left' != OPPOSITES[self.direction[2]]:
                if (self.position[0] - i, self.position[1]) in self.tail and not close_to_left:
                    close_to_left = True
                    weights['left'] += 1
            if 'up' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] - i) in self.tail and not close_to_up:
                    close_to_up = True
                    weights['up'] += 1
            if 'down' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] + i) in self.tail and not close_to_down:
                    close_to_down = True
                    weights['down'] += 1

        # Player tail weight check
        close_to_right_player = False
        close_to_left_player = False
        close_to_up_player = False
        close_to_down_player = False
        for i in range(0, area_sensor):
            if 'right' != OPPOSITES[self.direction[2]]:
                if (self.position[0] + i, self.position[1]) in player.tail and not close_to_right_player:
                    close_to_right_player = True
                    weights['right'] += 2
                    weights['up'] += 1
                    weights['down'] += 1
            if 'left' != OPPOSITES[self.direction[2]]:
                if (self.position[0] - i, self.position[1]) in player.tail and not close_to_left_player:
                    close_to_left_player = True
                    weights['left'] += 2
                    weights['up'] += 1
                    weights['down'] += 1
            if 'up' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] - i) in player.tail and not close_to_up_player:
                    close_to_up_player = True
                    weights['up'] += 2
                    weights['left'] += 1
                    weights['right'] += 1
            if 'down' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] + i) in player.tail and not close_to_down_player:
                    close_to_down_player = True
                    weights['down'] += 2
                    weights['left'] += 1
                    weights['right'] += 1

        close_to_right_player = False
        close_to_left_player = False
        close_to_up_player = False
        close_to_down_player = False
        for i in range(area_sensor, area_sensor_wide):
            if 'right' != OPPOSITES[self.direction[2]]:
                if (self.position[0] + i, self.position[1]) in player.tail and not close_to_right_player:
                    close_to_right_player = True
                    weights['right'] += 1
            if 'left' != OPPOSITES[self.direction[2]]:
                if (self.position[0] - i, self.position[1]) in player.tail and not close_to_left_player:
                    close_to_left_player = True
                    weights['left'] += 1
            if 'up' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] - i) in player.tail and not close_to_up_player:
                    close_to_up_player = True
                    weights['up'] += 1
            if 'down' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] + i) in player.tail and not close_to_down_player:
                    close_to_down_player = True
                    weights['down'] += 1

        # Select best transition
        if weights[self.direction[2]] == weights[DIR_NEIGHBORS[self.direction[2]][0]]:
            if weights[self.direction[2]] == weights[DIR_NEIGHBORS[self.direction[2]][1]]:
                return

        lowest = ('', 9999999)
        has_close_bound = False
        for key, value in weights.items():
            if value >= 2:
                has_close_bound = True
            if value < lowest[1] and not key == OPPOSITES[self.direction[2]]:
                lowest = (key, value)
        if not has_close_bound:
            return
        if lowest[0] == 'left':
            self.direction = (-1, 0, 'left')
            return
        if lowest[0] == 'right':
            self.direction = (1, 0, 'right')
            return
        if lowest[0] == 'up':
            self.direction = (0, -1, 'up')
            return
        if lowest[0] == 'down':
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
                    tail_block[0] + m / 2,
                    tail_block[1] + m / 2,
                    m,
                    m
                )
            )


player = Player(COLORS['BLUE'], SPEED)
enemy = Enemy(COLORS['RED'], SPEED)

while True:
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    player.update(enemy)
    enemy.update(player)

    DISPLAY_SURFACE.fill(COLORS['BLACK'])

    player.draw(DISPLAY_SURFACE)
    enemy.draw(DISPLAY_SURFACE)

    FramePerSec.tick(FPS)
