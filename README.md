# CHAI Fairness Project

## Prerequisites
- Python 3.12 or higher recommended

## Installation
Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage
### Preprocessing AMR files

Use the provided command-line script to process AMR files using the multisentence splitting filter (specific to "fairness"):

```bash
python preprocess.py multisentence <input_file> <output_file>
```

- `<input_file>`: Path to your source AMR file (e.g., `data/fair_AMR-500.amr`)
- `<output_file>`: Path to write the processed output (will be overwritten)

#### Example
```bash
python preprocess.py multisentence data/fair_AMR-500.amr data/fair_AMR-500_clean.amr
```

This will extract all split AMR sentence blocks mentioning 'fairness' and write them to the specified output file.

## Project Structure
- `preprocessing/` - Project module, contains `multisentence.py` for AMR graph splitting and filtering
- `preprocess.py` - CLI entry point (see usage above)
- `requirements.txt` - Pip dependencies

## Notes
- The code uses the [penman](https://github.com/goodmami/penman) library to parse and split AMR graphs.
- All results are filtered so they only include AMRs containing the word 'fairness'.
