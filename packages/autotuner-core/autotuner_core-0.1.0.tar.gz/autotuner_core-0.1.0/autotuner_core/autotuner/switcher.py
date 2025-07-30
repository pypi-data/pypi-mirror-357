from autotuner_core.algorithms.sorting.counting_sort import counting_sort
from autotuner_core.algorithms.sorting.insertion_sort import insertion_sort
from autotuner_core.algorithms.sorting.merge_sort import merge_sort
from autotuner_core.algorithms.sorting.quick_sort import quick_sort
from autotuner_core.algorithms.sorting.timsort import timsort
from autotuner_core.autotuner.features import get_array_features


def choose_sort_algorithm(arr, algo="auto"):
    features = get_array_features(arr)
    size = features["size"]
    sortedness = features["sortedness_score"]
    if algo == "auto":
        if size <= 10:
            chosen_algo = "insertion_sort"
            sorted_arr = insertion_sort(arr)
        elif sortedness > 0.85:
            chosen_algo = "timsort"
            sorted_arr = timsort(arr)
        elif (
            all(isinstance(x, int) for x in arr) and min(arr) >= 0 and max(arr) < 10_000
        ):
            chosen_algo = "counting_sort"
            sorted_arr = counting_sort(arr)
        elif 10 < size <= 30:
            chosen_algo = "quick_sort"
            sorted_arr = quick_sort(arr)
        else:
            chosen_algo = "merge_sort"
            sorted_arr = merge_sort(arr)
    elif algo == "insertion_sort":
        chosen_algo = "insertion_sort"
        sorted_arr = insertion_sort(arr)
    elif algo == "timsort":
        chosen_algo = "timsort"
        sorted_arr = timsort(arr)
    elif algo == "counting_sort":
        chosen_algo = "counting_sort"
        sorted_arr = counting_sort(arr)
    elif algo == "quick_sort":
        chosen_algo = "quick_sort"
        sorted_arr = quick_sort(arr)
    elif algo in ["merge", "merge_sort"]:
        chosen_algo = "merge_sort"
        sorted_arr = merge_sort(arr)
    elif algo == "all_algorithms":
        chosen_algo = "all_algorithms"
        sorted_arr = {
            "insertion_sort": insertion_sort(arr),
            "timsort": timsort(arr),
            "counting_sort": (
                counting_sort(arr)
                if all(isinstance(x, int) and x >= 0 for x in arr)
                else "N/A"
            ),
            "quick_sort": quick_sort(arr),
            "merge_sort": merge_sort(arr),
        }
    else:
        raise ValueError(f"Unsupported algorithm: {algo}")

    return {"sorted_array": sorted_arr, "algorithm": chosen_algo, "features": features}
