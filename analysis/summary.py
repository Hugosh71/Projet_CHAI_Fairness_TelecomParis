"""AMR fairness term analysis and statistics."""

import collections
import pandas as pd


def analyze_fairness_amr(amr_path: str, max_items: int = 20) -> None:
    """
    Analyze fairness-related concepts in AMR graphs and print statistics.

    Args:
        amr_path: Path to .amr file.
        max_items: Maximum number of items to show per category (default: 20).
    """

    try:
        import penman
    except ImportError:
        print("Please install 'penman' first: pip install penman")
        return

    # Load AMR graphs from file
    try:
        with open(amr_path, "r", encoding="utf-8", errors="ignore") as f:
            graphs = penman.load(f)
    except Exception as e:
        print(f"Failed to load AMR file: {e}")
        return

    # Initialize counters for statistics
    position_counts = collections.Counter()
    parent_role_counts = collections.Counter()
    parent_concept_counts = collections.Counter()
    child_role_counts = collections.Counter()
    sibling_concept_counts = collections.Counter()

    # Store example relations for each role family
    parent_examples = collections.defaultdict(list)
    child_examples = collections.defaultdict(list)

    def role_family(role: str) -> str:
        """Normalize role to family (e.g., op1/op2 -> 'op')."""
        r = role.lstrip(":").lower()
        return "op" if r.startswith("op") else r

    # Process each AMR graph
    for g in graphs:
        # Map variable -> concept (instance triples)
        inst = {src: tgt for (src, role, tgt) in g.triples if role == ":instance"}

        # Build adjacency lists (outgoing and incoming edges)
        outgoing = collections.defaultdict(list)
        incoming = collections.defaultdict(list)
        for src, role, tgt in g.triples:
            if role == ":instance":
                continue
            outgoing[src].append((role, tgt))
            incoming[tgt].append((role, src))

        # Find all fairness-related variables
        fairness_vars = [v for v, c in inst.items() if c in {"fairness", "fair-01"}]
        for v in fairness_vars:
            # Determine position in graph (root, leaf, or interior)
            if v == g.top:
                pos = "root"
            else:
                children = [t for (r, t) in outgoing.get(v, []) if r != ":instance"]
                pos = "leaf" if not children else "interior"
            position_counts[pos] += 1

            # Analyze parent relations
            for r, parent_v in incoming.get(v, []):
                fam = role_family(r)
                parent_role_counts[fam] += 1
                parent_concept = inst.get(parent_v, "(literal)")
                parent_concept_counts[parent_concept] += 1
                # Store examples (max 3 per role family)
                if len(parent_examples[fam]) < 3:
                    parent_examples[fam].append((parent_concept, r))

                # Find sibling concepts (same parent)
                for rc, sib_v in outgoing.get(parent_v, []):
                    if sib_v == v:
                        continue
                    sib_concept = inst.get(sib_v)
                    if sib_concept:
                        sibling_concept_counts[sib_concept] += 1

            # Analyze child relations
            for r, child_v in outgoing.get(v, []):
                if r == ":instance":
                    continue
                fam = role_family(r)
                child_role_counts[fam] += 1
                child_concept = inst.get(child_v, "(literal)")
                # Store examples (max 3 per role family)
                if len(child_examples[fam]) < 3:
                    child_examples[fam].append((child_concept, r))

    def print_df(title: str, counter: collections.Counter):
        """Print counter as pandas DataFrame table."""
        print(f"\n=== {title} ===")
        if not counter:
            print("[No data]")
            return
        df = pd.DataFrame(counter.most_common(max_items), columns=[title, "count"])
        print(df.to_string(index=False))

    # Print all statistics tables
    print_df("Position of fairness", position_counts)
    print_df("Parent roles (relations) of fairness", parent_role_counts)
    print_df("Parent concepts of fairness", parent_concept_counts)
    print_df("Child roles (relations) of fairness", child_role_counts)
    print_df("Sibling concepts (same parent as fairness)", sibling_concept_counts)

    # Print example relations
    print("\n--- Example relations (first few) ---")
    for fam, exs in list(parent_examples.items())[:5]:
        print(f"Parent role {fam}: {exs[:3]}")
    for fam, exs in list(child_examples.items())[:5]:
        print(f"Child role {fam}: {exs[:3]}")

    print("\nAnalysis completed.")
