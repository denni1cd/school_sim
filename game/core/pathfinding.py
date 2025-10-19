import heapq


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, goal, blocked=None):
    if start == goal:
        return [start]

    blocked = set() if blocked is None else set(blocked)
    open_nodes = [(0, start)]
    came_from = {start: None}
    g_score = {start: 0}

    while open_nodes:
        _, current = heapq.heappop(open_nodes)
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            return list(reversed(path))

        x, y = current
        for nx, ny in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
            if not grid.walkable(nx, ny):
                continue
            if (nx, ny) in blocked and (nx, ny) != goal:
                continue
            new_cost = g_score[current] + 1
            if (nx, ny) not in g_score or new_cost < g_score[(nx, ny)]:
                g_score[(nx, ny)] = new_cost
                came_from[(nx, ny)] = current
                priority = new_cost + heuristic((nx, ny), goal)
                heapq.heappush(open_nodes, (priority, (nx, ny)))
    return None