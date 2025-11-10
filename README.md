# CHAI Fairness Project

_Main analysis walkthrough and data visualizations live in `notebooks/IA_717_ProjectCHAI-fairness_2025.ipynb`._

## Prerequisites
- Python 3.12 or higher recommended
- Dataset setup:
  - Clone the source data repository into `data/mapaie`:
    ```bash
    git clone https://gitlab.telecom-paris.fr/tiphaine.viard/mapaie data/mapaie
    ```
  - From the `data/mapaie` directory run:
    ```bash
    python dl_docs.py
    python parse_docs.py
    python preprocess.py
    ```

## Installation
Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

---

## Usage
The main end-to-end analysis (including visualizations) is documented in `notebooks/IA_717_ProjectCHAI-fairness_2025.ipynb`. Command-line entry points are summarised below.

### Preprocessing
Clean and prepare data for analysis. The `preprocessing/` module provides CSS/HTML cleaning and AMR graph splitting utilities.

#### Removing CSS from Text/HTML Files
```bash
python preprocess.py remove_css <input_dir>
```
- `<input_dir>`: Path to the directory containing `.txt` or `.html` files. All files in that directory will be overwritten with CSS removed.

Example:
```bash
python preprocess.py remove_css data/mapaie/data/txts/
```

#### Splitting and Filtering AMR Files
```bash
python preprocess.py multisentence <input_file> <output_file>
```
- `<input_file>`: Path to your source AMR file (e.g., `data/fair_AMR-500.amr`)
- `<output_file>`: Path to write the processed output (will be overwritten)

Example:
```bash
python preprocess.py multisentence data/fair_AMR-500.amr data/fair_AMR-500_clean.amr
```

### Analyzing
Analyze AMR files for fairness statistics and centrality-based ranking via the `analysis/` module.

#### CLI Commands
```bash
python analyze.py summary <input_file>
python analyze.py centrality_score <input_file> [--k <K>]
```
- `<input_file>`: Path to your AMR file.
- `--k <K>`: (Optional, default: 10) Number of top central graphs to show for the `centrality_score` command.

Example:
```bash
python analyze.py summary data/fair_AMR-500_clean.amr
python analyze.py centrality_score data/fair_AMR-500_clean.amr --k 5
```
Run `python analyze.py -h` to see a list of all commands and options.

#### Using Modules Programmatically
```python
from preprocessing import process_amr_file, remove_all_css
from analysis import analyze_fairness_amr, top_k_fairness_graphs

# Process AMR file
process_amr_file("input.amr", "output.amr")

# Analyze fairness statistics
analyze_fairness_amr("output.amr", max_items=10)

# Get top K graphs by centrality
df = top_k_fairness_graphs("output.amr", k=5)
```

## Project Structure
```
project-root/
├── preprocessing/
│   ├── cleaning.py         # CSS and HTML cleaning utilities
│   ├── multisentence.py    # AMR graph splitting and filtering
│   └── __init__.py         # Module exports
├── analysis/
│   ├── summary.py           # Fairness statistics analysis
│   ├── centrality_score.py # Centrality-based graph ranking
│   └── __init__.py         # Module exports
├── preprocess.py           # Preprocessing CLI entry point
├── analyze.py              # Analysis CLI entry point (summary & centrality)
├── requirements.txt        # Pip dependencies
├── README.md               # This file
└── data/                   # Data directory (AMR files, text files, etc.)
```

## Notes
- Uses [penman](https://github.com/goodmami/penman) for AMR graph parsing and manipulation.
- All results are filtered to include only AMRs containing the word 'fairness'.
- Centrality scoring combines role weights (ARG0, ARG1, etc.) and graph distance from root.
