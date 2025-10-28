# --------------------------------------------------------
# AMR Fairness Term Analysis
# - Requires: penman
#   pip install penman
# --------------------------------------------------------

import collections
import pandas as pd


def analyze_fairness_amr(amr_path: str, max_items: int = 20) -> None:
    """Analyze fairness-related concepts in AMR graphs and print pandas summaries."""

    try:
        import penman
    except ImportError:
        print("Please install 'penman' first: pip install penman")
        return

    # --- Load AMR graphs ---
    try:
        with open(amr_path, "r", encoding="utf-8", errors="ignore") as f:
            graphs = penman.load(f)
    except Exception as e:
        print(f"Failed to load AMR file: {e}")
        return

    # --- Initialize Counters ---
    position_counts = collections.Counter()
    parent_role_counts = collections.Counter()
    parent_concept_counts = collections.Counter()
    child_role_counts = collections.Counter()
    sibling_concept_counts = collections.Counter()

    # Optional: keep small representative samples
    parent_examples = collections.defaultdict(list)
    child_examples = collections.defaultdict(list)

    # --- Helper: normalize role family (group op1/op2/... as 'op') ---
    def role_family(role: str) -> str:
        r = role.lstrip(":").lower()
        return "op" if r.startswith("op") else r

    # --- Iterate over AMR graphs ---
    for g in graphs:
        # Map variable -> concept
        inst = {src: tgt for (src, role, tgt) in g.triples if role == ":instance"}

        # Build edge lookups
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
            # --- Position ---
            if v == g.top:
                pos = "root"
            else:
                children = [t for (r, t) in outgoing.get(v, []) if r != ":instance"]
                pos = "leaf" if not children else "interior"
            position_counts[pos] += 1

            # --- Parent edges ---
            for r, parent_v in incoming.get(v, []):
                fam = role_family(r)
                parent_role_counts[fam] += 1
                parent_concept = inst.get(parent_v, "(literal)")
                parent_concept_counts[parent_concept] += 1
                if len(parent_examples[fam]) < 3:
                    parent_examples[fam].append((parent_concept, r))

                # --- Siblings under the same parent ---
                for rc, sib_v in outgoing.get(parent_v, []):
                    if sib_v == v:
                        continue
                    sib_concept = inst.get(sib_v)
                    if sib_concept:
                        sibling_concept_counts[sib_concept] += 1

            # --- Child edges ---
            for r, child_v in outgoing.get(v, []):
                if r == ":instance":
                    continue
                fam = role_family(r)
                child_role_counts[fam] += 1
                child_concept = inst.get(child_v, "(literal)")
                if len(child_examples[fam]) < 3:
                    child_examples[fam].append((child_concept, r))

    # --- Print summaries as pandas tables ---
    def print_df(title: str, counter: collections.Counter):
        print(f"\n=== {title} ===")
        if not counter:
            print("[No data]")
            return
        df = pd.DataFrame(counter.most_common(max_items), columns=[title, "count"])
        print(df.to_string(index=False))

    print_df("Position of fairness", position_counts)
    print_df("Parent roles (relations) of fairness", parent_role_counts)
    print_df("Parent concepts of fairness", parent_concept_counts)
    print_df("Child roles (relations) of fairness", child_role_counts)
    print_df("Sibling concepts (same parent as fairness)", sibling_concept_counts)

    print("\n--- Example relations (first few) ---")
    for fam, exs in list(parent_examples.items())[:5]:
        print(f"Parent role {fam}: {exs[:3]}")
    for fam, exs in list(child_examples.items())[:5]:
        print(f"Child role {fam}: {exs[:3]}")

    print("\nAnalysis completed.")
