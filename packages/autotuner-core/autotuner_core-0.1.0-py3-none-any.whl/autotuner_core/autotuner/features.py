def get_array_features(arr):
    n = len(arr)
    is_sorted = all(arr[i] <= arr[i + 1] for i in range(n - 1))
    is_reverse_sorted = all(arr[i] >= arr[i + 1] for i in range(n - 1))
    increasing_pairs = sum(1 for i in range(n - 1) if arr[i] <= arr[i + 1])
    sortedness_score = increasing_pairs / (n - 1) if n > 1 else 1
    return {
        "size": n,
        "is_sorted": is_sorted,
        "is_reverse_sorted": is_reverse_sorted,
        "sortedness_score": round(sortedness_score, 2),
    }
