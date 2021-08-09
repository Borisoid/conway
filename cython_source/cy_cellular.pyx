from typing import List, Callable

import cython

from libc.stdlib cimport (
    malloc,
    free,
)
from libc.math cimport abs


pyT_grid = List[List[bool]]


@cython.cdivision(True)
cdef inline int modulo(int a, int n) nogil:
    return ((a % n ) + n ) % n


# lookup strategies ###########################################################

cdef int torus_grid_lookup(bint** grid, int w, int h, int x, int y):
    return (
        <int>grid[modulo((x + 0), w)][modulo((y - 1), h)] +  # N
        <int>grid[modulo((x + 1), w)][modulo((y - 1), h)] +  # NE
        <int>grid[modulo((x + 1), w)][modulo((y - 0), h)] +  # E
        <int>grid[modulo((x + 1), w)][modulo((y + 1), h)] +  # SE
        <int>grid[modulo((x + 0), w)][modulo((y + 1), h)] +  # S
        <int>grid[modulo((x - 1), w)][modulo((y + 1), h)] +  # SW
        <int>grid[modulo((x - 1), w)][modulo((y - 0), h)] +  # W
        <int>grid[modulo((x - 1), w)][modulo((y - 1), h)]    # NW
    )

cdef int limited_plane_grid_lookup(bint** grid, int w, int h, int x, int y):
    cdef int[8][2] coordinates = [
        [x + 0, y - 1],  # N
        [x + 1, y - 1],  # NE
        [x + 1, y - 0],  # E
        [x + 1, y + 1],  # SE
        [x + 0, y + 1],  # S
        [x - 1, y + 1],  # SW
        [x - 1, y - 0],  # W
        [x - 1, y - 1],  # NW
    ]
    cdef int alive_neighbours = 0
    cdef int i, ix, iy
    for i in range(8):
        ix = coordinates[i][0]
        iy = coordinates[i][1]
        if ix < 0 or ix >= w or iy < 0 or iy >= h:
            continue
        alive_neighbours += <int>grid[ix][iy]
    return alive_neighbours

# end lookup strategies #######################################################

# tick rules ##################################################################

cdef bint standard_rule(bint current_state, int neighbours):
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


ctypedef bint(*cT_rule)(bint current_state, int neighbours)
ctypedef int(*cT_lookup)(bint** grid, int w, int h, int x, int y)


def get_engine(grid: pyT_grid, rule: str = 'standard', lookup: str = 'torus'):
    cdef int cells_x = len(grid)
    cdef int cells_y = len(grid[0])

    cdef cT_rule rule_callback
    if rule == 'standard':
        rule_callback = standard_rule

    cdef cT_lookup lookup_callback
    if lookup == 'torus':
        lookup_callback = torus_grid_lookup
    elif lookup == 'limited_plane':
        lookup_callback = limited_plane_grid_lookup

    cdef bint** c_grid_this_tick = <bint**>malloc(cells_x * sizeof(bint*))
    for x in range(cells_x):
        c_grid_this_tick[x] = <bint*>malloc(cells_y * sizeof(bint))

    def tick_grid(grid_this_tick: pyT_grid, grid_next_tick: pyT_grid):
        cdef int x
        cdef int y

        for y in range(cells_y):
            for x in range(cells_x):
                c_grid_this_tick[x][y] = <bint>grid_this_tick[x][y]

        for y in range(cells_y):
            for x in range(cells_x):
                neighbours = lookup_callback(c_grid_this_tick, cells_x, cells_y, x, y)
                grid_next_tick[x][y] = bool(rule_callback(c_grid_this_tick[x][y], neighbours))

    def _del(self):
        for x in range(cells_x):
            free(c_grid_this_tick[x])
        free(c_grid_this_tick)

    tick_grid.__del__ = _del

    return tick_grid
