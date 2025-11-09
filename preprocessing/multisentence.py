"""AMR graph splitting and filtering utilities."""

import penman
from penman.models.noop import NoOpModel
import re
from pathlib import Path


def read_amr_blocks(filepath):
    """
    Read AMR blocks from a file, ignoring comments.

    Args:
        filepath: Path to .amr file.

    Returns:
        List of AMR block strings, each starting with '('.
    """
    blocks = []
    current_block = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Skip comment lines
            if stripped.startswith("#"):
                continue

            # New AMR graph starts with '('
            if stripped.startswith("("):
                if current_block:
                    blocks.append("\n".join(current_block))
                    current_block = []
                current_block.append(stripped)
            else:
                # Continuation of current graph
                if current_block and stripped:
                    current_block.append(stripped)

    if current_block:
        blocks.append("\n".join(current_block))

    return blocks


def extract_subgraph(graph, subroot):
    """
    Extract subgraph starting from a given root node using DFS.

    Args:
        graph: Penman graph to extract from.
        subroot: Root node for the subgraph.

    Returns:
        Penman graph containing only nodes reachable from subroot.
    """
    visited = set()
    stack = [subroot]
    sub_triples = []
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        # Collect all triples starting from this node
        for src, role, tgt in graph.triples:
            if src == node:
                sub_triples.append((src, role, tgt))
                stack.append(tgt)
    return penman.Graph(sub_triples, top=subroot)


def get_connected_subgraph(triples, top):
    """
    Keep only triples connected to the top node (prevents LayoutError).

    Args:
        triples: List of (source, role, target) triples.
        top: Root node of the graph.

    Returns:
        List of connected triples reachable from top.
    """
    visited = set()
    stack = [top]
    connected = []
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for src, role, tgt in triples:
            if src == node:
                connected.append((src, role, tgt))
                stack.append(tgt)
    return connected


def split_all_snt_without_duplicates(amr_str):
    """
    Split multi-sentence AMR graph into individual sentence graphs.

    Args:
        amr_str: AMR graph string.

    Returns:
        List of AMR strings, one per sentence (parent graph + sub-sentences).
    """
    try:
        g = penman.decode(amr_str, model=NoOpModel())
    except Exception as e:
        print(f"[!] Failed to decode AMR:\n{amr_str[:80]}...\nError: {e}")
        return []

    # Find all :snt* triples (sentence relations)
    snt_triples = [
        (src, role, tgt) for (src, role, tgt) in g.triples if role.startswith(":snt")
    ]

    if not snt_triples:
        return [penman.encode(g)]

    snt_targets = {tgt for (_, _, tgt) in snt_triples}

    sentences = []
    # Extract sub-sentence graphs
    for _, role, tgt in snt_triples:
        sub_g = extract_subgraph(g, tgt)
        sentences.append(penman.encode(sub_g))

    # Rebuild parent graph without :snt* triples
    filtered_triples = [
        t for t in g.triples if not (t[1].startswith(":snt") and t[2] in snt_targets)
    ]

    # Keep only connected triples from root
    connected_parent_triples = get_connected_subgraph(filtered_triples, g.top)
    if connected_parent_triples:
        parent_g = penman.Graph(connected_parent_triples, top=g.top)
        sentences.insert(0, penman.encode(parent_g))

    return sentences


def filter_fairness(sentences):
    """
    Filter sentences containing the word "fairness".

    Args:
        sentences: List of AMR sentence strings.

    Returns:
        List of sentences containing "fairness" (case-insensitive).
    """
    return [s for s in sentences if re.search(r"\bfairness\b", s, re.IGNORECASE)]


def process_amr_file(input_path, output_path):
    """
    Main pipeline: read AMR file, split sentences, filter for fairness, save.

    Args:
        input_path: Path to input .amr file.
        output_path: Path to output .amr file (will be overwritten).
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    blocks = read_amr_blocks(input_path)
    print(f"Found {len(blocks)} AMR blocks in file {input_path}")

    all_sentences = []
    for block in blocks:
        sentences = split_all_snt_without_duplicates(block)
        fairness_sents = filter_fairness(sentences)
        all_sentences.extend(fairness_sents)

    # Write filtered sentences to output file
    with open(output_path, "w", encoding="utf-8") as out:
        for s in all_sentences:
            out.write(s.strip() + "\n\n")

    print(f"Wrote {len(all_sentences)} AMRs containing 'fairness' to {output_path}")
