import sys
from analysis import analyze_fairness_amr


def main():
    if len(sys.argv) < 3:
        print("Usage: python analysis.py summary <input_file>")
        sys.exit(1)
    command = sys.argv[1]
    if command == "summary":
        input_file = sys.argv[2]
        analyze_fairness_amr(input_file)
    else:
        print(f"Unknown command: {command}")
        print("Usage: python analysis.py summary <input_file>")
        sys.exit(1)


if __name__ == "__main__":
    main()
