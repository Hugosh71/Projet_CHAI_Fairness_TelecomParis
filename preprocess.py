import sys
import os
from preprocessing import process_amr_file
from preprocessing.cleaning import remove_all_css


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"multisentence", "remove_css"}:
        print("Usage:")
        print(" python preprocess.py multisentence <input_file> <output_file>")
        print(" python preprocess.py remove_css <input_dir>")
        sys.exit(1)
    command = sys.argv[1]
    if command == "multisentence":
        if len(sys.argv) != 4:
            print(
                "Usage: python preprocess.py multisentence <input_file> <output_file>"
            )
            sys.exit(1)
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        process_amr_file(input_file, output_file)
    elif command == "remove_css":
        if len(sys.argv) != 3:
            print("Usage: python preprocess.py remove_css <input_dir>")
            sys.exit(1)
        input_dir = sys.argv[2]
        if not os.path.isdir(input_dir):
            print(f"Error: {input_dir} is not a valid directory.")
            sys.exit(1)
        for filename in os.listdir(input_dir):
            filepath = os.path.join(input_dir, filename)
            if os.path.isfile(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                cleaned = remove_all_css(content)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(cleaned)
                print(f"Processed (CSS removed): {filepath}")


if __name__ == "__main__":
    main()
