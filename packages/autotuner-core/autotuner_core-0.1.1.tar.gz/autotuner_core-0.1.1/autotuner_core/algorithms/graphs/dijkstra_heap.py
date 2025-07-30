import heapq


def dijkstra_heap(adj_list, start):
    dist = {node: float("inf") for node in adj_list}
    dist[start] = 0
    visited = set()
    pq = [(0, start)]
    while pq:
        cost, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        for v, weight in adj_list[u]:
            if dist[v] > cost + weight:
                dist[v] = cost + weight
                heapq.heappush(pq, (dist[v], v))
    return dist
