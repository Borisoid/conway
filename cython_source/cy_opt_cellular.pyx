# distutils: language = c++

from typing import Tuple, Set

import cython
from libcpp.list cimport list
from libcpp.unordered_set cimport unordered_set


cdef struct cell:
    int x, y

cdef cppclass cell_comparator:
    bint compare "operator()"(const cell &c1, const cell &c2) const:
        return (c1.x == c2.x) and (c1.y == c2.y)

cdef cppclass cell_hasher:
    size_t hash "operator()"(const cell &c) const:
        return c.x ^ c.y


ctypedef unordered_set[cell, cell_hasher, cell_comparator] cell_set
ctypedef list[cell] cell_list
ctypedef bint(*rule)(const bint &, const int &)
ctypedef cell_list*(*lookup)(const cell &, int, int)


@cython.cdivision(True)
cdef inline int mod(int a, int n) nogil:
    return ((a % n ) + n ) % n


cdef inline bint standard_rule(const bint &current_state, const int &neighbours):
    if neighbours == 3:
        return True
    elif current_state and (neighbours == 2):
        return True
    return False


cdef cell_list* torus_lookup(const cell &c, int w, int h):
    cdef int x = c.x
    cdef int y = c.y
    cdef cell_list* out = new cell_list()
    out[0].push_back(cell(mod((x + 0), w), mod((y - 1), h)))  # N
    out[0].push_back(cell(mod((x + 1), w), mod((y - 1), h)))  # NE
    out[0].push_back(cell(mod((x + 1), w), mod((y - 0), h)))  # E
    out[0].push_back(cell(mod((x + 1), w), mod((y + 1), h)))  # SE
    out[0].push_back(cell(mod((x + 0), w), mod((y + 1), h)))  # S
    out[0].push_back(cell(mod((x - 1), w), mod((y + 1), h)))  # SW
    out[0].push_back(cell(mod((x - 1), w), mod((y - 0), h)))  # W
    out[0].push_back(cell(mod((x - 1), w), mod((y - 1), h)))  # NW
    return out


cdef class CLifeEngine:
    cdef cell_set* live_cells_this_tick
    cdef cell_set* live_cells_next_tick
    cdef cell_set* checked_cells

    cdef rule rule_callback
    cdef lookup lookup_callback

    cdef int w, h

    def __cinit__(self, initial_live_cells: Set[Tuple[int, int]], w, h):
        self.out_live_cells = set()
        self.out_checked_cells = set()

        self.live_cells_this_tick = new cell_set()
        self.live_cells_next_tick = new cell_set()
        self.checked_cells = new cell_set()

        self.rule_callback = standard_rule
        self.lookup_callback = torus_lookup

        self.w = w
        self.h = h

        for live_cell in initial_live_cells:
            self.live_cells_this_tick[0].insert(cell(live_cell[0], live_cell[1]))

    def tick(self):
        self._tick()

        self.out_live_cells.clear()
        self.out_checked_cells.clear()

        self.live_cells_this_tick[0].clear()
        for live_cell_next_tick in self.live_cells_next_tick[0]:
            self.out_live_cells.add((live_cell_next_tick.x, live_cell_next_tick.y))
        self.live_cells_next_tick, self.live_cells_this_tick = self.live_cells_this_tick, self.live_cells_next_tick

        self.checked_cells[0].clear()

    cdef void _tick(self):
        cdef cell live_cell
        cdef cell_list* live_cell_neighbours
        cdef cell live_cell_neighbour

        cdef int live_neighbour_count
        cdef cell_list* cells_to_check
        cdef cell cell_to_check

        for live_cell in self.live_cells_this_tick[0]:
            live_cell_neighbours = self.lookup_callback(live_cell, self.w, self.h)
            for live_cell_neighbour in live_cell_neighbours[0]:
                if self.checked_cells[0].count(live_cell_neighbour) == 0:
                    live_neighbour_count = 0
                    cells_to_check = self.lookup_callback(live_cell_neighbour, self.w, self.h)
                    for cell_to_check in cells_to_check[0]:
                        if self.live_cells_this_tick[0].count(cell_to_check) != 0:
                            live_neighbour_count += 1
                    del cells_to_check
                    self.checked_cells[0].insert(live_cell_neighbour)
                    if (
                        self.rule_callback(
                            self.live_cells_this_tick[0].count(live_cell_neighbour) != 0,
                            live_neighbour_count
                        )
                    ):
                        self.live_cells_next_tick[0].insert(live_cell_neighbour)
            del live_cell_neighbours


class LifeEngine(CLifeEngine):
    def tick(self):
        super().tick()
