# CHAI Fairness Project

## Prerequisites
- Python 3.12 or higher recommended

## Installation
Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

---

## Preprocessing
This section describes how to clean and prepare your data for analysis, including AMR splitting and CSS removal for text files.

The preprocessing module (`preprocessing/`) provides two main functionalities:
- **`cleaning.py`**: Utilities for removing CSS and HTML tags from text files
- **`multisentence.py`**: AMR graph splitting and filtering for fairness-related content

### Removing CSS from Text/HTML Files
You can clean a directory of text or HTML files by removing all CSS with:

```bash
python preprocess.py remove_css <input_dir>
```
- `<input_dir>`: Path to the directory containing `.txt` or `.html` files. All files in that directory will be overwritten with CSS removed.

The `remove_css` command uses functions from `preprocessing/cleaning.py` to:
- Remove `<style>` blocks
- Remove `<link rel="stylesheet">` tags
- Remove inline `style="..."` attributes
- Remove CSS code blocks (including `@media`, `@keyframes`, etc.)
- Clean up excessive whitespace

#### Example
```bash
python preprocess.py remove_css data/texts/
```
This will process all files in the `data/texts/` directory, removing inline, style blocks, and stylesheet links from each file.

### Splitting and Filtering AMR Files
Use the provided command-line script to process AMR files using the multisentence splitting filter (specific to "fairness"):

```bash
python preprocess.py multisentence <input_file> <output_file>
```
- `<input_file>`: Path to your source AMR file (e.g., `data/fair_AMR-500.amr`)
- `<output_file>`: Path to write the processed output (will be overwritten)

The `multisentence` command uses functions from `preprocessing/multisentence.py` to:
- Read AMR blocks from files (ignoring comments)
- Split multi-sentence AMR graphs into individual sentence graphs
- Extract subgraphs based on `:snt*` relations
- Filter results to only include AMRs containing the word "fairness"

#### Example
```bash
python preprocess.py multisentence data/fair_AMR-500.amr data/fair_AMR-500_clean.amr
```
This will extract all split AMR sentence blocks mentioning 'fairness' and write them to the specified output file.

---

## Analyzing
This section describes how to analyze the output AMR files for fairness, including summary statistics and centrality-based ranking.

### Running Analyses
The `analyze.py` CLI exposes several subcommands:

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
│   ├── cleaning.py         # CSS and HTML cleaning utilities
│   ├── multisentence.py    # AMR graph splitting and filtering
│   └── __init__.py         # Module exports
├── preprocess.py           # Preprocessing CLI entry point
├── analyze.py              # Analysis CLI entry point (summary & centrality)
├── requirements.txt        # Pip dependencies
└── data/                   # Data directory (AMR files, text files, etc.)
```

## Notes
- The code uses the [penman](https://github.com/goodmami/penman) library to parse and split AMR graphs.
- All results are filtered so they only include AMRs containing the word 'fairness'.
