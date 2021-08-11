from test import stopwatch
from typing import Callable, Iterable, List, Set, Tuple
import pygame
import sys
from datetime import datetime
import random

import cppyy


FPS = 60

WIN_WIDTH = 1000
WIN_HEIGHT = 650

CELLS_ALONG_X = 100
CELLS_ALONG_Y = 65
CELLS_SPACE_WIDTH = 1
CELLS_WIDTH = WIN_WIDTH / CELLS_ALONG_X - CELLS_SPACE_WIDTH
CELLS_HEIGHT = WIN_HEIGHT / CELLS_ALONG_Y - CELLS_SPACE_WIDTH
CELLS_X_OFFSET = CELLS_WIDTH + CELLS_SPACE_WIDTH
CELLS_Y_OFFSET = CELLS_HEIGHT + CELLS_SPACE_WIDTH

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_DARK_GREEN = (0, 50, 0)
DARK_GREEN = (0, 170, 0)
ORANGE = (255, 150, 100)
DARK_DARK_GREY = (20, 20, 20)
GREY = (150, 150, 150)
LIGHT_GREY = (200, 200, 200)

BACKGROUND_COLOR = DARK_DARK_GREY
DEAD_CELL_COLOR = BLACK
LIVE_CELL_COLOR = GREEN

CHECKED_CELL_COLOR = DARK_DARK_GREEN


T_cell = Tuple[int, int]
T_cell_set = Set[T_cell]
T_lookup_coordinates_generator = Callable[[T_cell], Iterable[T_cell]]
T_tick_rule = Callable[[bool, int], bool]


clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))


def cell_set_insert(cell_set, xy):
        cell_set.insert(cppyy.gbl.cell(xy[0], xy[1]))


def draw_grid_setup():
    screen.fill(BACKGROUND_COLOR)
    for y in range(CELLS_ALONG_Y):
        for x in range(CELLS_ALONG_X):
            pygame.draw.rect(
                screen, DEAD_CELL_COLOR,
                (x*CELLS_X_OFFSET, y*CELLS_Y_OFFSET, CELLS_WIDTH, CELLS_HEIGHT)
            )
    pygame.display.update()


def draw_grid(
    live_cells_old,
    live_cells,
):
    it = live_cells_old.begin()
    while it != live_cells_old.end():
        c = it.__deref__()
        pygame.draw.rect(
            screen, DEAD_CELL_COLOR,
            (c.x*CELLS_X_OFFSET, c.y*CELLS_Y_OFFSET, CELLS_WIDTH, CELLS_HEIGHT)
        )
        it.__preinc__()

    it = live_cells.begin()
    while it != live_cells.end():
        c = it.__deref__()
        pygame.draw.rect(
            screen, LIVE_CELL_COLOR,
            (c.x*CELLS_X_OFFSET, c.y*CELLS_Y_OFFSET, CELLS_WIDTH, CELLS_HEIGHT)
        )
        it.__preinc__()

    pygame.display.update()


with open('cppyy.cpp', 'r') as f:
    cppyy.cppdef(f.read())
    cppyy.gbl.CELLS_ALONG_X = CELLS_ALONG_X
    cppyy.gbl.CELLS_ALONG_Y = CELLS_ALONG_Y


if __name__ == '__main__':

    live_cells_this_tick = cppyy.gbl.cell_set()
    live_cells_next_tick = cppyy.gbl.cell_set()
    checked_cells = cppyy.gbl.cell_set()
    # checked_cells_old = set()

    for i in range(CELLS_ALONG_X*CELLS_ALONG_Y // 2):
        cell_set_insert(
            live_cells_this_tick,
            (random.randint(0, CELLS_ALONG_X - 1), random.randint(0, CELLS_ALONG_Y - 1))
        )
    # for c in ((100, 65), (102, 66), (99, 67), (100, 67), (103, 67), (104, 67), (105, 67),):
    #     live_cells_this_tick.add(c)

    tick_grid = cppyy.gbl.tick_grid
    rule = cppyy.gbl.standard_rule
    lookup = cppyy.gbl.torus_lookup

    draw_grid_setup()
    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        checked_cells.clear()
        grid = tick_grid(
            live_cells_this_tick, live_cells_next_tick, checked_cells,
            rule, lookup
        )
        draw_grid(live_cells_this_tick, live_cells_next_tick)
        live_cells_this_tick, live_cells_next_tick = live_cells_next_tick, live_cells_this_tick
        live_cells_next_tick.clear()

        clock.tick(120)
        print(clock.get_fps())
