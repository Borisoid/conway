from typing import Callable, Iterable, List, Set, Tuple
import pygame
import sys
from datetime import datetime
import random

import cppyy

from ..config import *


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


with open('ccpp_source/cppyy_opt.cpp', 'r') as f:
    cppyy.cppdef(f.read())
    cppyy.gbl.CELLS_ALONG_X = CELLS_ALONG_X
    cppyy.gbl.CELLS_ALONG_Y = CELLS_ALONG_Y


def main():

    print()

    live_cells_this_tick = cppyy.gbl.cell_set()
    live_cells_next_tick = cppyy.gbl.cell_set()
    checked_cells = cppyy.gbl.cell_set()
    # checked_cells_old = set()

    for icx, icy in INIT_LIVE_CELLS:
        cell_set_insert(live_cells_this_tick, (icx, icy))

    tick_grid = cppyy.gbl.tick_grid
    rule = cppyy.gbl.standard_rule
    lookup = cppyy.gbl.torus_lookup

    draw_grid_setup()
    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        checked_cells.clear()
        tick_grid(
            live_cells_this_tick, live_cells_next_tick, checked_cells,
            rule, lookup
        )
        draw_grid(live_cells_this_tick, live_cells_next_tick)
        live_cells_this_tick, live_cells_next_tick = live_cells_next_tick, live_cells_this_tick
        live_cells_next_tick.clear()

        clock.tick(FPS)
        print("\033[F", '{:3.5f}'.format(clock.get_fps()), sep='')


if __name__ == '__main__':
    main()
