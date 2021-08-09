from typing import Callable, List
import pygame
import sys
import random


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
DARK_GREEN = (0, 170, 0)
ORANGE = (255, 150, 100)
DARK_DARK_GREY = (20, 20, 20)
GREY = (150, 150, 150)
LIGHT_GREY = (200, 200, 200)

BACKGROUND_COLOR = DARK_DARK_GREY
DEAD_CELL_COLOR = BLACK
LIVE_CELL_COLOR = GREEN


T_grid = List[List[bool]]
T_lookup_strategy = Callable[[T_grid, int, int], int]
T_tick_rule = Callable[[bool, int], bool]


clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))


def invert_grid_cells(grid, *args):
    """allows for quick notation args = x1, y1, x2, y2, x3, y3, ..."""
    for i in range(0, len(args), 2):
        grid[args[i]][args[i+1]] ^= True


def get_grid(x, y, fill_value=False):
    return [[fill_value for _ in range(y)] for _ in range(x)]


# lookup strategies ###########################################################

def torus_grid_lookup(grid: T_grid, x: int, y: int) -> int:
    """return number of live heighbours"""
    return sum((
        grid[(x + 0) % CELLS_ALONG_X][(y - 1) % CELLS_ALONG_Y],  # N
        grid[(x + 1) % CELLS_ALONG_X][(y - 1) % CELLS_ALONG_Y],  # NE
        grid[(x + 1) % CELLS_ALONG_X][(y - 0) % CELLS_ALONG_Y],  # E
        grid[(x + 1) % CELLS_ALONG_X][(y + 1) % CELLS_ALONG_Y],  # SE
        grid[(x + 0) % CELLS_ALONG_X][(y + 1) % CELLS_ALONG_Y],  # S
        grid[(x - 1) % CELLS_ALONG_X][(y + 1) % CELLS_ALONG_Y],  # SW
        grid[(x - 1) % CELLS_ALONG_X][(y - 0) % CELLS_ALONG_Y],  # W
        grid[(x - 1) % CELLS_ALONG_X][(y - 1) % CELLS_ALONG_Y],  # NW
    ))

def limited_plane_grid_lookup(grid: T_grid, x: int, y: int) -> int:
    coordinates = (
        (x + 0, y - 1),
        (x + 1, y - 1),
        (x + 1, y - 0),
        (x + 1, y + 1),
        (x + 0, y + 1),
        (x - 1, y + 1),
        (x - 1, y - 0),
        (x - 1, y - 1),
    )
    alive_neighbours = 0
    for c in coordinates:
        ix = c[0]
        iy = c[1]
        if ix < 0 or ix >= len(grid) or iy < 0 or iy >= len(grid[0]):
            continue
        alive_neighbours += grid[ix][iy]
    return alive_neighbours

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


def draw_grid(grid):
    screen.fill(BACKGROUND_COLOR)
    for y in range(CELLS_ALONG_Y):
        for x in range(CELLS_ALONG_X):
            cell_color = LIVE_CELL_COLOR if grid[x][y] else DEAD_CELL_COLOR
            pygame.draw.rect(
                screen, cell_color,
                (x*CELLS_X_OFFSET, y*CELLS_Y_OFFSET, CELLS_WIDTH, CELLS_HEIGHT)
            )
    pygame.display.update()


def tick_grid(grid, rule: T_tick_rule, lookup: T_lookup_strategy):
    grid_next_tick = get_grid(CELLS_ALONG_X, CELLS_ALONG_Y)
    for y in range(CELLS_ALONG_Y):
        for x in range(CELLS_ALONG_X):
            neighbours = lookup(grid, x, y)
            grid_next_tick[x][y] = rule(grid[x][y], neighbours)
    return grid_next_tick


if __name__ == '__main__':

    grid = get_grid(CELLS_ALONG_X, CELLS_ALONG_Y)
    for i in range(10000):
        x = random.randint(0, CELLS_ALONG_X - 1)
        y = random.randint(0, CELLS_ALONG_Y - 1)
        invert_grid_cells(grid, x, y)
    # invert_grid_cells(grid, 100, 65, 102, 66, 99, 67, 100, 67, 103, 67, 104, 67, 105, 67)
    # invert_grid_cells(grid, 50, 40, 52, 41, 49, 42, 50, 42, 53, 42, 54, 42, 55, 42)

    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        draw_grid(grid)
        grid = tick_grid(grid, standard_rule, torus_grid_lookup)

        clock.tick(120)
        print(clock.get_fps())
