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

### Analyzing AMR files
AMR file analysis is available through `analyze.py`, which now uses argparse for modern CLI parsing. Two subcommands are available:

- **summary**: Summarize fairness-specific statistics for an AMR file.
- **centrality_score**: Show the top K AMR graphs with highest fairness centrality.

#### Usage
```bash
python analyze.py summary <input_file>
python analyze.py centrality_score <input_file> [--k <K>]
```
- `<input_file>`: Path to your AMR file.
- `--k <K>`: (Optional, default: 10) Number of top central graphs to show for the `centrality_score` command.

#### Example
```bash
python analyze.py summary data/fair_AMR-500_clean.amr
python analyze.py centrality_score data/fair_AMR-500_clean.amr --k 5
```
Run `python analyze.py -h` to see a list of all commands and options.

## Project Structure
```
project-root/
├── preprocessing/
│   └── multisentence.py    # AMR graph splitting and filtering
├── preprocess.py           # Preprocessing CLI entry point
├── analyze.py              # Analysis CLI entry point (summary & centrality)
├── requirements.txt        # Pip dependencies
```

## Notes
- The code uses the [penman](https://github.com/goodmami/penman) library to parse and split AMR graphs.
- All results are filtered so they only include AMRs containing the word 'fairness'.
