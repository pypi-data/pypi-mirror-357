from collections import deque


def topo_sort(adj_list, num_nodes):
    indegree = [0] * num_nodes
    for u in adj_list:
        for v in adj_list[u]:
            indegree[v] += 1
    queue = deque([i for i in range(num_nodes) if indegree[i] == 0])
    result = []
    while queue:
        u = queue.popleft()
        result.append(u)
        for v in adj_list.get(u, []):
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    if len(result) == num_nodes:
        return result
    else:
        return "Cycle Detected – Topological Sort Not Possible"
