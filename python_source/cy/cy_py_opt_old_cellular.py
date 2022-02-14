from cython_target.cy_opt_old_cellular import *

from typing import Callable, Iterable, List, Set, Tuple
import pygame
import sys
import random

from ..config import *


T_cell = Tuple[int, int]
T_cell_set = Set[T_cell]
T_lookup_coordinates_generator = Callable[[T_cell], Iterable[T_cell]]
T_tick_rule = Callable[[bool, int], bool]

clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))


def get_grid(x, y, fill_value=False):
    return [[fill_value for _ in range(y)] for _ in range(x)]


# noinspection PyTypeChecker
def draw_grid_setup():
    screen.fill(BACKGROUND_COLOR)
    for y in range(CELLS_ALONG_Y):
        for x in range(CELLS_ALONG_X):
            pygame.draw.rect(
                screen, DEAD_CELL_COLOR,
                (x * CELLS_X_OFFSET, y * CELLS_Y_OFFSET, CELLS_WIDTH, CELLS_HEIGHT)
            )
    pygame.display.update()


# noinspection PyTypeChecker
def draw_grid(
        live_cells_old: T_cell_set,
        live_cells: T_cell_set
):
    for x, y in live_cells_old:
        pygame.draw.rect(
            screen, DEAD_CELL_COLOR,
            (x * CELLS_X_OFFSET, y * CELLS_Y_OFFSET, CELLS_WIDTH, CELLS_HEIGHT)
        )

    for x, y in live_cells:
        pygame.draw.rect(
            screen, LIVE_CELL_COLOR,
            (x * CELLS_X_OFFSET, y * CELLS_Y_OFFSET, CELLS_WIDTH, CELLS_HEIGHT)
        )

    pygame.display.update()


def main():

    print()

    live_cells = set()
    live_cells_old = set()

    for icx, icy in INIT_LIVE_CELLS:
        live_cells.add((icx, icy))

    engine = LifeEngine(live_cells, CELLS_ALONG_X, CELLS_ALONG_Y)
    live_cells = engine.out_live_cells

    draw_grid_setup()
    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        # checked_cells.clear()
        engine.tick()
        draw_grid(live_cells_old, live_cells)
        live_cells_old = live_cells.copy()


        clock.tick(FPS)
        print("\033[F", '{:3.5f}'.format(clock.get_fps()), sep='')


if __name__ == '__main__':
    main()
