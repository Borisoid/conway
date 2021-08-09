import pygame
import sys
import random

from cython_target.cy_cellular import get_engine


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

clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))


def invert_grid_cells(grid, *args):
    """allows for quick notation args = x1, y1, x2, y2, x3, y3, ..."""
    for i in range(0, len(args), 2):
        grid[args[i]][args[i+1]] ^= True


def get_grid(x, y, fill_value=False):
    return [[fill_value for _ in range(y)] for _ in range(x)]


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


if __name__ == '__main__':

    grid_next_tick = get_grid(CELLS_ALONG_X, CELLS_ALONG_Y)
    grid = get_grid(CELLS_ALONG_X, CELLS_ALONG_Y)
    for i in range(10000):
        x = random.randint(0, CELLS_ALONG_X - 1)
        y = random.randint(0, CELLS_ALONG_Y - 1)
        invert_grid_cells(grid, x, y)
    # invert_grid_cells(grid, 100, 65, 102, 66, 99, 67, 100, 67, 103, 67, 104, 67, 105, 67)
    # invert_grid_cells(grid, 50, 40, 52, 41, 49, 42, 50, 42, 53, 42, 54, 42, 55, 42)

    tick_grid = get_engine(grid, lookup='torus')
    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        draw_grid(grid)
        # grid_next_tick = get_grid(CELLS_ALONG_X, CELLS_ALONG_Y)
        tick_grid(grid, grid_next_tick)
        grid, grid_next_tick = grid_next_tick, grid

        clock.tick(120)
        print(clock.get_fps())
