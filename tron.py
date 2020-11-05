import pygame
import sys
from pygame.locals import *
import math
import random

pygame.init()

FPS = 60
SPEED = 2
FramePerSec = pygame.time.Clock()

COLORS = {
    'BLACK': (0, 0, 0),
    'BLUE': (0, 0, 255),
    'RED': (255, 0, 0),
    'WHITE': (255, 255, 255),
    'GREEN': (0, 255, 0)
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

font = pygame.font.Font('freesansbold.ttf', 32)


class Player:
    def __init__(self, color, speed, size=10):
        self.speed = speed
        self.direction = (0, 1, 'down')
        self.position = (random.randint(200, 400), 100)
        self.size = size
        self.color = color
        self.tail = {}
        self.alive = True

    def die(self):
        self.color = COLORS['WHITE']
        self.alive = False

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
        for i in range(self.speed):
            for j in range(self.speed):
                if (self.position[0] + i, self.position[1] + j) in self.tail or (self.position[0] + i, self.position[1] + j) in enemy.tail:
                    self.die()
                    return
        if self.position[0] < 0 or self.position[0] > MAX_DISPLAY_SIZE:
            self.die()
            return
        if self.position[1] < 0 or self.position[1] > MAX_DISPLAY_SIZE:
            self.die()
            return

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

    wide_range = 0.05
    close_range = 0.01
    random_factor = 0.02

    def __init__(self, color, speed, size=10):
        self.speed = speed
        self.direction = (0, -1, 'up')
        self.position = (random.randint(200, 400), 500)
        self.size = size
        self.color = color
        self.tail = {}
        self.alive = True

    def die(self):
        self.color = COLORS['WHITE']
        self.alive = False

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
        for i in range(self.speed):
            for j in range(self.speed):
                if (self.position[0] + i, self.position[1] + j) in self.tail or (self.position[0] + i, self.position[1] + j) in player.tail:
                    self.die()
                    return
        if self.position[0] < 0 or self.position[0] > MAX_DISPLAY_SIZE:
            self.die()
            return
        if self.position[1] < 0 or self.position[1] > MAX_DISPLAY_SIZE:
            self.die()
            return

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
        area_sensor_wide = int(MAX_DISPLAY_SIZE * self.wide_range * 1.1)

        close_to_right = False
        close_to_left = False
        close_to_up = False
        close_to_down = False
        close_to_right_player = False
        close_to_left_player = False
        close_to_up_player = False
        close_to_down_player = False
        for i in range(0, area_sensor):
            if 'right' != OPPOSITES[self.direction[2]]:
                if (self.position[0] + i, self.position[1]) in self.tail and not close_to_right:
                    close_to_right = True
                    weights['right'] += 2
                    weights['up'] += 1
                    weights['down'] += 1
                if (self.position[0] + i, self.position[1]) in player.tail and not close_to_right_player:
                    close_to_right_player = True
                    weights['right'] += 2
                    weights['up'] += 1
                    weights['down'] += 1
            if 'left' != OPPOSITES[self.direction[2]]:
                if (self.position[0] - i, self.position[1]) in self.tail and not close_to_left:
                    close_to_left = True
                    weights['left'] += 2
                    weights['up'] += 1
                    weights['down'] += 1
                if (self.position[0] - i, self.position[1]) in player.tail and not close_to_left_player:
                    close_to_left_player = True
                    weights['left'] += 2
                    weights['up'] += 1
                    weights['down'] += 1
            if 'up' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] - i) in self.tail and not close_to_up:
                    close_to_up = True
                    weights['up'] += 2
                    weights['left'] += 1
                    weights['right'] += 1
                if (self.position[0], self.position[1] - i) in player.tail and not close_to_up_player:
                    close_to_up_player = True
                    weights['up'] += 2
                    weights['left'] += 1
                    weights['right'] += 1
            if 'down' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] + i) in self.tail and not close_to_down:
                    close_to_down = True
                    weights['down'] += 2
                    weights['left'] += 1
                    weights['right'] += 1
                if (self.position[0], self.position[1] + i) in player.tail and not close_to_down_player:
                    close_to_down_player = True
                    weights['down'] += 2
                    weights['left'] += 1
                    weights['right'] += 1

        close_to_right = False
        close_to_left = False
        close_to_up = False
        close_to_down = False
        close_to_right_player = False
        close_to_left_player = False
        close_to_up_player = False
        close_to_down_player = False
        for i in range(area_sensor, area_sensor_wide):
            if 'right' != OPPOSITES[self.direction[2]]:
                if (self.position[0] + i, self.position[1]) in self.tail and not close_to_right:
                    close_to_right = True
                    weights['right'] += 1
                if (self.position[0] + i, self.position[1]) in player.tail and not close_to_right_player:
                    close_to_right_player = True
                    weights['right'] += 1
            if 'left' != OPPOSITES[self.direction[2]]:
                if (self.position[0] - i, self.position[1]) in self.tail and not close_to_left:
                    close_to_left = True
                    weights['left'] += 1
                if (self.position[0] - i, self.position[1]) in player.tail and not close_to_left_player:
                    close_to_left_player = True
                    weights['left'] += 1
            if 'up' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] - i) in self.tail and not close_to_up:
                    close_to_up = True
                    weights['up'] += 1
                if (self.position[0], self.position[1] - i) in player.tail and not close_to_up_player:
                    close_to_up_player = True
                    weights['up'] += 1
            if 'down' != OPPOSITES[self.direction[2]]:
                if (self.position[0], self.position[1] + i) in self.tail and not close_to_down:
                    close_to_down = True
                    weights['down'] += 1
                if (self.position[0], self.position[1] + i) in player.tail and not close_to_down_player:
                    close_to_down_player = True
                    weights['down'] += 1

        random_change = False
        new_dir = None
        if weights[self.direction[2]] == weights[DIR_NEIGHBORS[self.direction[2]][0]] or weights[self.direction[2]] + 1 == weights[DIR_NEIGHBORS[self.direction[2]][0]]:
            if weights[self.direction[2]] == weights[DIR_NEIGHBORS[self.direction[2]][1]] or weights[self.direction[2]] + 1 == weights[DIR_NEIGHBORS[self.direction[2]][1]]:
                random_change = random.randint(
                    0, 100) / 100 <= self.random_factor
                if random_change:
                    if weights[self.direction[2]] + 1 == weights[DIR_NEIGHBORS[self.direction[2]][0]]:
                        new_dir = DIR_NEIGHBORS[self.direction[2]][1]
                    elif weights[self.direction[2]] + 1 == weights[DIR_NEIGHBORS[self.direction[2]][1]]:
                        new_dir = DIR_NEIGHBORS[self.direction[2]][0]
                    else:
                        new_dir = DIR_NEIGHBORS[self.direction[2]
                                                ][random.randint(0, 1)]

        if not random_change:
            lowest = ('', 9999999)
            has_close_bound = False
            for key, value in weights.items():
                if value >= 2:
                    has_close_bound = True
                if value < lowest[1] and not key == OPPOSITES[self.direction[2]]:
                    lowest = (key, value)
            if not has_close_bound:
                return
        else:
            lowest = (new_dir, 0)

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


text_win = font.render("Has ganado! :D", True,
                       COLORS['GREEN'], COLORS['BLACK'])
text_lose = font.render(
    "Has perdido... :(", True, COLORS['RED'], COLORS['BLACK'])
textRect_win = text_win.get_rect()
textRect_win.center = (MAX_DISPLAY_SIZE // 2, MAX_DISPLAY_SIZE // 2)
textRect_lose = text_lose.get_rect()
textRect_lose.center = (MAX_DISPLAY_SIZE // 2, MAX_DISPLAY_SIZE // 2)

player = Player(COLORS['BLUE'], SPEED)
enemy = Enemy(COLORS['RED'], SPEED)

while True:
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    if enemy.alive and player.alive:
        player.update(enemy)
        enemy.update(player)

    DISPLAY_SURFACE.fill(COLORS['BLACK'])

    player.draw(DISPLAY_SURFACE)
    enemy.draw(DISPLAY_SURFACE)

    if enemy.alive and not player.alive:
        DISPLAY_SURFACE.blit(text_lose, textRect_lose)
    elif player.alive and not enemy.alive:
        DISPLAY_SURFACE.blit(text_win, textRect_win)

    FramePerSec.tick(FPS)
