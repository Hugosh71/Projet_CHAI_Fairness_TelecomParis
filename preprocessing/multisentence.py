import penman
from penman.models.noop import NoOpModel
import re
from pathlib import Path


# -----------------------------------------------------------
# 1. Read AMR blocks from file (start when line starts with "(")
# -----------------------------------------------------------
def read_amr_blocks(filepath):
    """
    Read a .amr file and return a list of cleaned Penman blocks.
    Each block starts with '(' and ignores preceding comments or junk lines.
    """
    blocks = []
    current_block = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Skip comment lines
            if stripped.startswith("#"):
                continue

            # Start of a new AMR graph
            if stripped.startswith("("):
                if current_block:
                    blocks.append("\n".join(current_block))
                    current_block = []
                current_block.append(stripped)
            else:
                # Continuation of current graph (skip empty junk before first '(')
                if current_block and stripped:
                    current_block.append(stripped)

    if current_block:
        blocks.append("\n".join(current_block))

    return blocks


# -----------------------------------------------------------
# 2. Extract subgraph starting from a given node (DFS)
# -----------------------------------------------------------
def extract_subgraph(graph, subroot):
    visited = set()
    stack = [subroot]
    sub_triples = []
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for src, role, tgt in graph.triples:
            if src == node:
                sub_triples.append((src, role, tgt))
                stack.append(tgt)
    return penman.Graph(sub_triples, top=subroot)


# -----------------------------------------------------------
# 3. Keep only connected triples from top (prevents LayoutError)
# -----------------------------------------------------------
def get_connected_subgraph(triples, top):
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


# -----------------------------------------------------------
# 4. Split into sentence graphs and remove nested sub-sentences
# -----------------------------------------------------------
def split_all_snt_without_duplicates(amr_str):
    try:
        g = penman.decode(amr_str, model=NoOpModel())
    except Exception as e:
        print(f"[!] Failed to decode AMR:\n{amr_str[:80]}...\nError: {e}")
        return []

    # Find all :snt* triples anywhere
    snt_triples = [
        (src, role, tgt) for (src, role, tgt) in g.triples if role.startswith(":snt")
    ]

    if not snt_triples:
        return [penman.encode(g)]

    snt_targets = {tgt for (_, _, tgt) in snt_triples}

    sentences = []
    # 1. Extract sub-sentences first
    for _, role, tgt in snt_triples:
        sub_g = extract_subgraph(g, tgt)
        sentences.append(penman.encode(sub_g))

    # 2. Rebuild parent graph without those :snt* triples
    filtered_triples = [
        t for t in g.triples if not (t[1].startswith(":snt") and t[2] in snt_targets)
    ]

    connected_parent_triples = get_connected_subgraph(filtered_triples, g.top)
    if connected_parent_triples:
        parent_g = penman.Graph(connected_parent_triples, top=g.top)
        sentences.insert(0, penman.encode(parent_g))

    return sentences


# -----------------------------------------------------------
# 5. Filter sentences containing "fairness"
# -----------------------------------------------------------
def filter_fairness(sentences):
    return [s for s in sentences if re.search(r"\bfairness\b", s, re.IGNORECASE)]


# -----------------------------------------------------------
# 6. Main pipeline: read -> split -> filter -> save
# -----------------------------------------------------------
def process_amr_file(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    blocks = read_amr_blocks(input_path)
    print(f"📥 Found {len(blocks)} AMR blocks in file {input_path}")

    all_sentences = []
    for block in blocks:
        sentences = split_all_snt_without_duplicates(block)
        fairness_sents = filter_fairness(sentences)
        all_sentences.extend(fairness_sents)

    with open(output_path, "w", encoding="utf-8") as out:
        for s in all_sentences:
            out.write(s.strip() + "\n\n")

    print(f"Wrote {len(all_sentences)} AMRs containing 'fairness' to {output_path}")
