import sys
from preprocessing import process_amr_file


def main():
    if len(sys.argv) < 4:
        print("Usage: python preprocess.py multisentence <input_file> <output_file>")
        sys.exit(1)
    command = sys.argv[1]
    if command == "multisentence":
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        process_amr_file(input_file, output_file)
    else:
        print(f"Unknown command: {command}")
        print("Usage: python preprocess.py multisentence <input_file> <output_file>")
        sys.exit(1)


if __name__ == "__main__":
    main()
