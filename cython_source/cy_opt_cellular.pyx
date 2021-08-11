# distutils: language = c++

from typing import Tuple, Set

import cython
from libcpp.list cimport list
from libcpp.unordered_set cimport unordered_set


cdef struct cell:
    int x, y

ctypedef unordered_set[long long] cell_set
ctypedef list[long long] cell_list
ctypedef bint(*rule)(const bint &, const int &)
ctypedef cell_list*(*lookup)(const cell &, int, int)


cdef inline long long hc(cell c):
    return (<long long*>&c)[0]
cdef inline cell c(long long hc):
    return (<cell*>&hc)[0]

@cython.cdivision(True)
cdef inline int mod(int a, int n) nogil:
    return ((a % n ) + n ) % n


cdef inline bint standard_rule(const bint &current_state, const int &neighbours):
    if current_state and (neighbours == 2 or neighbours == 3):
        return True
    elif neighbours == 3:
        return True
    else:
        return False


cdef cell_list* torus_lookup(const cell &c, int w, int h):
    cdef int x = c.x
    cdef int y = c.y
    cdef cell_list* c_list = new cell_list()
    c_list[0].push_back(hc(cell(mod((x + 0), w), mod((y - 1), h))))  # N
    c_list[0].push_back(hc(cell(mod((x + 1), w), mod((y - 1), h))))  # NE
    c_list[0].push_back(hc(cell(mod((x + 1), w), mod((y - 0), h))))  # E
    c_list[0].push_back(hc(cell(mod((x + 1), w), mod((y + 1), h))))  # SE
    c_list[0].push_back(hc(cell(mod((x + 0), w), mod((y + 1), h))))  # S
    c_list[0].push_back(hc(cell(mod((x - 1), w), mod((y + 1), h))))  # SW
    c_list[0].push_back(hc(cell(mod((x - 1), w), mod((y - 0), h))))  # W
    c_list[0].push_back(hc(cell(mod((x - 1), w), mod((y - 1), h))))  # NW
    return c_list


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
            self.live_cells_this_tick[0].insert(hc(cell(live_cell[0], live_cell[1])))

    def tick(self):
        self._tick()

        self.out_live_cells.clear()
        self.out_checked_cells.clear()

        self.live_cells_this_tick[0].clear()
        for h_live_cell_next_tick in self.live_cells_next_tick[0]:
            live_cell_next_tick = c(h_live_cell_next_tick)
            self.out_live_cells.add((live_cell_next_tick.x, live_cell_next_tick.y))
        self.live_cells_next_tick, self.live_cells_this_tick = self.live_cells_this_tick, self.live_cells_next_tick

        # for h_checked_cell in self.checked_cells[0]:
        #    checked_cell = c(h_checked_cell)
        #     self.out.checked_cells.add((checked_cell.x, checked_cell.x))
        self.checked_cells[0].clear()

    cdef void _tick(self):
        cdef long long h_live_cell

        cdef cell live_cell
        cdef cell_list* live_cell_neighbours
        cdef long long h_live_cell_neighbour

        cdef int live_neighbour_count
        cdef cell_list* cells_to_check
        cdef long long h_c

        cdef long long h_live_cell_next_tick
        cdef cell live_cell_next_tick

        for h_live_cell in self.live_cells_this_tick[0]:
            live_cell = c(h_live_cell)
            live_cell_neighbours = self.lookup_callback(live_cell, self.w, self.h)
            for h_live_cell_neighbour in live_cell_neighbours[0]:
                if self.checked_cells[0].find(h_live_cell_neighbour) == self.checked_cells[0].end():
                    live_neighbour_count = 0
                    cells_to_check = self.lookup_callback(c(h_live_cell_neighbour), self.w, self.h)
                    for h_c in cells_to_check[0]:
                        if self.live_cells_this_tick[0].find(h_c) != self.live_cells_this_tick[0].end():
                            live_neighbour_count += 1
                    del cells_to_check
                    self.checked_cells[0].insert(h_live_cell_neighbour)
                    if (
                        self.rule_callback(
                            self.live_cells_this_tick[0].find(h_live_cell_neighbour) != self.live_cells_this_tick[0].end(),
                            live_neighbour_count
                        )
                    ):
                        self.live_cells_next_tick[0].insert(h_live_cell_neighbour)
            del live_cell_neighbours


class LifeEngine(CLifeEngine):
    def tick(self):
        super().tick()



# cdef cell_set test = cell_set()
# test.insert(hc(cell(1, 2)))
#
# cdef cell cc
# cdef long long llc
# for llc in test:
#     cc = c(llc)
#     print(cc.x, cc.y)
