def dfs(graph, start):
    visited = set()
    result = []

    def visit(node):
        visited.add(node)
        result.append(node)
        for neighbor in graph.get(node, []):
            if isinstance(neighbor, (tuple, list)):
                neighbor = neighbor[0]
            if neighbor not in visited:
                visit(neighbor)

    visit(start)
    return result
