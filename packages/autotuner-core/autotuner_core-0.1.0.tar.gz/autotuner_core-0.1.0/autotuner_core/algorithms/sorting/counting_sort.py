def counting_sort(arr):
    if not arr:
        return []
    if not all(isinstance(x, int) for x in arr):
        raise ValueError("Counting sort only supports integer values.")
    min_val = min(arr)
    max_val = max(arr)
    range_size = max_val - min_val + 1
    count = [0] * range_size
    output = [0] * len(arr)
    for num in arr:
        count[num - min_val] += 1
    for i in range(1, len(count)):
        count[i] += count[i - 1]
    for num in reversed(arr):
        count[num - min_val] -= 1
        output[count[num - min_val]] = num
    return output
