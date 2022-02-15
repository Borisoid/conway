#include <list>
#include <unordered_set>

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

    struct hasher {
        std::size_t operator() (const cell &c) const {
            return ((size_t)c.x << 32) ^ ((size_t)c.y); 
        }
    };
};


typedef std::unordered_set<cell, cell::hasher> cell_set;
typedef std::list<cell> cell_list;
typedef bool(*rule)(const bool &, const int &);
typedef void(*lookup)(const cell &, cell_list &);


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

void torus_lookup(const cell &c, cell_list &out) {
    int x = c.x;
    int y = c.y;
    out.push_back(cell(mod(x + 0, CELLS_ALONG_X), mod(y - 1, CELLS_ALONG_Y)));  // N
    out.push_back(cell(mod(x + 1, CELLS_ALONG_X), mod(y - 1, CELLS_ALONG_Y)));  // NE
    out.push_back(cell(mod(x + 1, CELLS_ALONG_X), mod(y - 0, CELLS_ALONG_Y)));  // E
    out.push_back(cell(mod(x + 1, CELLS_ALONG_X), mod(y + 1, CELLS_ALONG_Y)));  // SE
    out.push_back(cell(mod(x + 0, CELLS_ALONG_X), mod(y + 1, CELLS_ALONG_Y)));  // S
    out.push_back(cell(mod(x - 1, CELLS_ALONG_X), mod(y + 1, CELLS_ALONG_Y)));  // SW
    out.push_back(cell(mod(x - 1, CELLS_ALONG_X), mod(y - 0, CELLS_ALONG_Y)));  // W
    out.push_back(cell(mod(x - 1, CELLS_ALONG_X), mod(y - 1, CELLS_ALONG_Y)));  // NW
}


void tick_grid(
    cell_set *live_cells_this_tick,
    cell_set *live_cells_next_tick,
    cell_set *checked_cells,
    rule rule_callback,
    lookup lookup_callback
) {
    for (auto live_cell : *live_cells_this_tick) {
        cell_list live_cell_neighbours;
        lookup_callback(live_cell, live_cell_neighbours);
        for (auto live_cell_neighbour : live_cell_neighbours) {
            if (checked_cells->find(live_cell_neighbour) == checked_cells->end()) {
                cell_list cells_to_check;
                lookup_callback(live_cell_neighbour, cells_to_check);
                int live_neighbour_count = 0;
                for (auto c : cells_to_check) {
                    if (live_cells_this_tick->count(c)) {
                        live_neighbour_count++;
                    }
                }
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
    }
}
