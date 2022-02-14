#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cstdio>
#include <list>
#include <unordered_set>


namespace py = pybind11;


struct cell {
    int x;
    int y;

    cell(int x, int y) {
        this->x = x;
        this->y = y;
    }

    int operator== (const cell& other) const {
        return this->x == other.x && this->y == other.y;
    }

    struct hasher {
        std::size_t operator() (const cell &c) const {
            return ((size_t)c.x << 32) ^ ((size_t)c.y); 
        }
    };
};


using cell_set = std::unordered_set<cell, cell::hasher>;
using cell_list = std::list<cell>;
using rule = bool(*)(const bool &, const int &);
using lookup = void(*)(int, int, const cell &, cell_list &);


#define mod(a, b) ((a % b + b) % b)


bool standard_rule(const bool &current_state, const int &neighbours) {
    if (current_state && (neighbours == 2 || neighbours == 3)) {
        return true;
    } else if (neighbours == 3) {
        return true;
    } else {
        return false;
    }
}

void torus_lookup(int cells_along_x, int cells_along_y, const cell &c, cell_list &out) {
    int x = c.x;
    int y = c.y;
    out.push_back(cell(mod(x + 0, cells_along_x), mod(y - 1, cells_along_y)));  // N
    out.push_back(cell(mod(x + 1, cells_along_x), mod(y - 1, cells_along_y)));  // NE
    out.push_back(cell(mod(x + 1, cells_along_x), mod(y - 0, cells_along_y)));  // E
    out.push_back(cell(mod(x + 1, cells_along_x), mod(y + 1, cells_along_y)));  // SE
    out.push_back(cell(mod(x + 0, cells_along_x), mod(y + 1, cells_along_y)));  // S
    out.push_back(cell(mod(x - 1, cells_along_x), mod(y + 1, cells_along_y)));  // SW
    out.push_back(cell(mod(x - 1, cells_along_x), mod(y - 0, cells_along_y)));  // W
    out.push_back(cell(mod(x - 1, cells_along_x), mod(y - 1, cells_along_y)));  // NW
}


void tick_grid(
    int cells_along_x,
    int cells_along_y,
    cell_set *live_cells_this_tick,
    cell_set *live_cells_next_tick,
    cell_set *checked_cells,
    rule rule_callback,
    lookup lookup_callback
) {
    auto live_cell_neighbours = cell_list();  //
    auto cells_to_check = cell_list();  //
    for (auto live_cell : *live_cells_this_tick) {
        lookup_callback(cells_along_x, cells_along_y, live_cell, live_cell_neighbours);
        for (auto live_cell_neighbour : live_cell_neighbours) {
            if (!checked_cells->count(live_cell_neighbour)) {
                int live_neighbour_count = 0;
                lookup_callback(cells_along_x, cells_along_y, live_cell_neighbour, cells_to_check);
                for (auto c : cells_to_check) {
                    if (live_cells_this_tick->count(c)) {
                        live_neighbour_count++;
                    }
                }
                cells_to_check.clear();  //
                checked_cells->insert(live_cell_neighbour);
                if (
                    rule_callback(
                        live_cells_this_tick->count(live_cell_neighbour),
                        live_neighbour_count
                    )
                ) {
                    live_cells_next_tick->insert(live_cell_neighbour);
                }
            }
        }
        live_cell_neighbours.clear();  //
    }
}


class LifeEngine {
    public:
        LifeEngine(int cells_along_x, int cells_along_y, const cell_set &live_cells) {
            this->cells_along_x = cells_along_x;
            this->cells_along_y = cells_along_y;
            live_cells_this_tick = new cell_set(live_cells);
            live_cells_next_tick = new cell_set();
            checked_cells = new cell_set();

            swap();
        }

        ~LifeEngine() {
            delete live_cells_this_tick;
            delete live_cells_next_tick;
            delete checked_cells;
        }

        void swap() {
            auto tmp = live_cells_this_tick;
            live_cells_this_tick = live_cells_next_tick;
            live_cells_next_tick = tmp;
        }

        void tick() {
            auto rule_callback = standard_rule;
            auto lookup_callback = torus_lookup;

            checked_cells->clear();

            cell_set *tmp = live_cells_this_tick;
            live_cells_this_tick = live_cells_next_tick;
            live_cells_next_tick = tmp;
            live_cells_next_tick->clear();

            tick_grid(
                cells_along_x, cells_along_y,
                live_cells_this_tick, live_cells_next_tick, checked_cells,
                rule_callback, lookup_callback
            );
        }

        cell_set get_live_cells_this_tick() {
            return *live_cells_this_tick;
        }

        cell_set get_live_cells_next_tick() {
            return *live_cells_next_tick;
        }

        int cells_along_x;
        int cells_along_y;
        cell_set *live_cells_this_tick;
        cell_set *live_cells_next_tick;
        cell_set *checked_cells;
};


PYBIND11_MODULE(pybind11_opt_cellular, m) {
    m.doc() = "pybind11 example plugin";

    py::class_<LifeEngine>(m, "LifeEngine")
        .def(py::init<int, int, cell_set>())
        .def("tick", &LifeEngine::tick)
        .def("get_live_cells_this_tick", &LifeEngine::get_live_cells_this_tick)
        .def("get_live_cells_next_tick", &LifeEngine::get_live_cells_next_tick);
        
    py::class_<cell>(m, "cell")
        .def(py::init<int, int>())
        .def_readwrite("x", &cell::x)
        .def_readwrite("y", &cell::y);
}
