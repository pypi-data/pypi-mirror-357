import argparse

from autotuner_core.autotuner.switcher import choose_sort_algorithm


def main():
    parser = argparse.ArgumentParser(description="AutoTuner Sorting CLI")
    parser.add_argument(
        "array",
        nargs="+",
        type=int,
        help="Input array of integers to be sorted",
    )
    parser.add_argument(
        "--algo",
        type=str,
        choices=[
            "auto",
            "bubble",
            "insertion",
            "selection",
            "merge",
            "quick",
            "heap",
            "counting",
            "radix",
            "tim",
            "all_algorithms",
        ],
        default="auto",
        help="Sorting algorithm to use (default: auto)",
    )
    args = parser.parse_args()
    try:
        result = choose_sort_algorithm(args.array, algo=args.algo)
        print("\n Array Features:")
        for k, v in result["features"].items():
            print(f"   {k}: {v}")
        print(f"\n Selected Algorithm: {result['algorithm']}")
        print(f" Sorted Array: {result['sorted_array']}")
        if result["algorithm"] == "all_algorithms":
            print("\n All Algorithm Outputs:")
            for name, output in result["sorted_array"].items():
                print(f"   {name}: {output}")
    except Exception as e:
        print(f"\nError while processing array: {e}")


if __name__ == "__main__":
    main()
