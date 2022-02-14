
from typing import Callable, Iterable, List, Set, Tuple
import pygame
import sys
import random

from ..config import *

from pybind11_target.pybind11_opt_cellular import (
    LifeEngine,
    cell,
)


T_cell = Tuple[int, int]
T_cell_set = Set[T_cell]
T_lookup_coordinates_generator = Callable[[T_cell], Iterable[T_cell]]
T_tick_rule = Callable[[bool, int], bool]


clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))


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
    dead_cells_new = live_cells_old - live_cells
    live_cells_new = live_cells - live_cells_old

    for c in dead_cells_new:
        pygame.draw.rect(
            screen, DEAD_CELL_COLOR,
            (c.x*CELLS_X_OFFSET, c.y*CELLS_Y_OFFSET, CELLS_WIDTH, CELLS_HEIGHT)
        )

    for c in live_cells_new:
        pygame.draw.rect(
            screen, LIVE_CELL_COLOR,
            (c.x*CELLS_X_OFFSET, c.y*CELLS_Y_OFFSET, CELLS_WIDTH, CELLS_HEIGHT)
        )

    pygame.display.update()


def main():

    print()

    live_cells_this_tick = set()
    live_cells_next_tick = set()

    for icx, icy in INIT_LIVE_CELLS:
        live_cells_this_tick.add(cell(icx, icy))


    engine = LifeEngine(CELLS_ALONG_X, CELLS_ALONG_Y, live_cells_this_tick)


    draw_grid_setup()
    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        engine.tick()
        live_cells_this_tick = engine.get_live_cells_this_tick()
        live_cells_next_tick = engine.get_live_cells_next_tick()

        draw_grid(live_cells_this_tick, live_cells_next_tick)

        clock.tick(FPS)
        print("\033[F", '{:3.5f}'.format(clock.get_fps()), sep='')


if __name__ == '__main__':
    main()



if __name__ == '__main__':
    main()
