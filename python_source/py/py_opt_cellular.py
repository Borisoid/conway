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


# lookup strategies ###########################################################

def torus_grid_lookup(cell: T_cell):
    x, y = cell
    yield ((x + 0) % CELLS_ALONG_X, (y - 1) % CELLS_ALONG_Y)  # N
    yield ((x + 1) % CELLS_ALONG_X, (y - 1) % CELLS_ALONG_Y)  # NE
    yield ((x + 1) % CELLS_ALONG_X, (y - 0) % CELLS_ALONG_Y)  # E
    yield ((x + 1) % CELLS_ALONG_X, (y + 1) % CELLS_ALONG_Y)  # SE
    yield ((x + 0) % CELLS_ALONG_X, (y + 1) % CELLS_ALONG_Y)  # S
    yield ((x - 1) % CELLS_ALONG_X, (y + 1) % CELLS_ALONG_Y)  # SW
    yield ((x - 1) % CELLS_ALONG_X, (y - 0) % CELLS_ALONG_Y)  # W
    yield ((x - 1) % CELLS_ALONG_X, (y - 1) % CELLS_ALONG_Y)  # NW

def limited_plane_grid_lookup(cell: T_cell):
    x, y = cell
    cells = (
        (x + 0, y - 1),
        (x + 1, y - 1),
        (x + 1, y - 0),
        (x + 1, y + 1),
        (x + 0, y + 1),
        (x - 1, y + 1),
        (x - 1, y - 0),
        (x - 1, y - 1),
    )
    for x, y in cells:
        if 0 <= x < CELLS_ALONG_X and 0 <= y < CELLS_ALONG_Y:
            yield x, y

# end lookup strategies #######################################################

# tick rules ##################################################################

def standard_rule(current_state: bool, neighbours: int) -> bool:
    # if cell is alive and has 2-3 live heighbours
    # it lives to next tick, else it dies
    if current_state and neighbours in (2, 3):
        return True
    # if a dead cell has exactly 3 live neighbours it becomes alive
    elif neighbours == 3:
        return True
    else:
        return False

# end tick rules ##############################################################

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
    live_cells_old: T_cell_set, checked_cells_old: T_cell_set,
    live_cells: T_cell_set, checked_cells: T_cell_set
):
    for x, y in checked_cells_old:
        pygame.draw.rect(
            screen, DEAD_CELL_COLOR,
            (x*CELLS_X_OFFSET, y*CELLS_Y_OFFSET, CELLS_WIDTH, CELLS_HEIGHT)
        )

    for x, y in checked_cells:
        if (x, y) in live_cells:
            cell_color = LIVE_CELL_COLOR
        else:
            cell_color = CHECKED_CELL_COLOR

        pygame.draw.rect(
            screen, cell_color,
            (x*CELLS_X_OFFSET, y*CELLS_Y_OFFSET, CELLS_WIDTH, CELLS_HEIGHT)
        )

    pygame.display.update()


def tick_grid(
    live_cells_this_tick: T_cell_set,
    live_cells_next_tick: T_cell_set,
    checked_cells: T_cell_set,
    rule: T_tick_rule,
    lookup: T_lookup_coordinates_generator,
):
    for live_cell in live_cells_this_tick:
        for live_cell_neighbour in lookup(live_cell):
            if live_cell_neighbour not in checked_cells:
                live_neighbour_count = 0
                for c in lookup(live_cell_neighbour):
                    if c in live_cells_this_tick:
                        live_neighbour_count += 1
                checked_cells.add(live_cell_neighbour)
                if rule(live_cell_neighbour in live_cells_this_tick, live_neighbour_count):
                    live_cells_next_tick.add(live_cell_neighbour)


def main():

    print()

    live_cells_this_tick = set()
    live_cells_next_tick = set()
    checked_cells = set()
    checked_cells_old = set()

    for i in range(CELLS_ALONG_X*CELLS_ALONG_Y // 2):
        live_cells_this_tick.add(
            (random.randint(0, CELLS_ALONG_X - 1),
             random.randint(0, CELLS_ALONG_Y - 1))
        )
    # for c in ((100, 65), (102, 66), (99, 67), (100, 67), (103, 67), (104, 67), (105, 67),):
    #     live_cells_this_tick.add(c)

    draw_grid_setup()
    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        checked_cells_old = checked_cells.copy()
        checked_cells.clear()
        tick_grid(
            live_cells_this_tick, live_cells_next_tick, checked_cells,
            standard_rule, torus_grid_lookup
        )
        draw_grid(
            live_cells_this_tick, checked_cells_old,
            live_cells_next_tick, checked_cells
        )
        live_cells_this_tick, live_cells_next_tick = live_cells_next_tick, live_cells_this_tick
        live_cells_next_tick.clear()
        

        clock.tick(FPS)
        print("\033[F", '{:3.5f}'.format(clock.get_fps()), sep='')


if __name__ == '__main__':
    main()
    