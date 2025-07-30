def dijkstra_matrix(matrix, start):
    n = len(matrix)
    dist = [float("inf")] * n
    dist[start] = 0
    visited = [False] * n

    for _ in range(n):
        u = -1
        for i in range(n):
            if not visited[i] and (u == -1 or dist[i] < dist[u]):
                u = i
        if u == -1:
            break
        visited[u] = True

        for v in range(n):
            if matrix[u][v] > 0 and dist[u] + matrix[u][v] < dist[v]:
                dist[v] = dist[u] + matrix[u][v]

    return dist
