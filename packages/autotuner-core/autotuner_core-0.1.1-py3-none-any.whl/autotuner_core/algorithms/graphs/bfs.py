from collections import deque


def bfs(graph, start):
    visited = set()
    queue = deque([start])
    result = []

    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            result.append(node)
            for neighbor in graph.get(node, []):
                if isinstance(neighbor, (tuple, list)):
                    neighbor = neighbor[0]
                if neighbor not in visited:
                    queue.append(neighbor)

    return result
