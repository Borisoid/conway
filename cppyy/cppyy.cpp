#include <list>
#include <unordered_set>
// #include <utility>


int CELLS_ALONG_X;
int CELLS_ALONG_Y;


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
};


struct cell_hasher {
    std::size_t operator() (const cell &c) const
    {
        return ((size_t)c.x << 32) ^ ((size_t)c.y); 
    }
};
// struct cell_allocator {
//     cell* allocate (std::size_t n) {
//         return (cell*)malloc(n);
//     };
//     void deallocate (cell* p, std::size_t n) {
//         free(p);
//     };
// };

typedef std::unordered_set<cell, cell_hasher> cell_set;
typedef std::list<cell> cell_list;
typedef bool(*rule)(const bool &, const int &);
typedef cell_list* (*lookup)(const cell &);


inline int mod(int a, int b) {
    return (a % b + b) % b;
}


bool standard_rule(const bool &current_state, const int &neighbours) {
    if (current_state && (neighbours == 2 || neighbours == 3)) {
        return true;
    } else if (neighbours == 3) {
        return true;
    } else {
        return false;
    }
}

cell_list* torus_lookup(const cell &c) {
    int x = c.x;
    int y = c.y;
    cell_list* list = new cell_list();
    list->insert(list->end(), cell(mod((x + 0), CELLS_ALONG_X), mod((y - 1), CELLS_ALONG_Y)));  // N
    list->insert(list->end(), cell(mod((x + 1), CELLS_ALONG_X), mod((y - 1), CELLS_ALONG_Y)));  // NE
    list->insert(list->end(), cell(mod((x + 1), CELLS_ALONG_X), mod((y - 0), CELLS_ALONG_Y)));  // E
    list->insert(list->end(), cell(mod((x + 1), CELLS_ALONG_X), mod((y + 1), CELLS_ALONG_Y)));  // SE
    list->insert(list->end(), cell(mod((x + 0), CELLS_ALONG_X), mod((y + 1), CELLS_ALONG_Y)));  // S
    list->insert(list->end(), cell(mod((x - 1), CELLS_ALONG_X), mod((y + 1), CELLS_ALONG_Y)));  // SW
    list->insert(list->end(), cell(mod((x - 1), CELLS_ALONG_X), mod((y - 0), CELLS_ALONG_Y)));  // W
    list->insert(list->end(), cell(mod((x - 1), CELLS_ALONG_X), mod((y - 1), CELLS_ALONG_Y)));  // NW
    return list;
}

void tick_grid(
    cell_set* live_cells_this_tick,
    cell_set* live_cells_next_tick,
    cell_set* checked_cells,
    rule rule_callback,
    lookup lookup_callback
) {
    for (auto live_cell : *live_cells_this_tick) {
        cell_list* live_cell_neighbours = lookup_callback(live_cell);
        for (auto live_cell_neighbour : *live_cell_neighbours) {
            if (checked_cells->find(live_cell_neighbour) == checked_cells->end()) {
                int live_neighbour_count = 0;
                cell_list* cells_to_check = lookup_callback(live_cell_neighbour);
                for (auto c : *cells_to_check) {
                    if (live_cells_this_tick->find(c) != live_cells_this_tick->end()) {
                        live_neighbour_count++;
                    }
                }
                delete cells_to_check;
                checked_cells->insert(live_cell_neighbour);
                if (
                    rule_callback(
                        live_cells_this_tick->find(live_cell_neighbour) != live_cells_this_tick->end(),
                        live_neighbour_count
                    )
                ) {
                    live_cells_next_tick->insert(live_cell_neighbour);
                }
            }
        }
        delete live_cell_neighbours;
    }
}
