"""AMR fairness centrality scoring and ranking."""

import penman
from penman.models.noop import NoOpModel
import re
import pandas as pd
import numpy as np
from collections import defaultdict, deque
from pathlib import Path

# Regex to match fairness-related concepts
FAIRNESS_REGEX = re.compile(r"Fairness|fairness|fair-[0-9]+", re.IGNORECASE)

# Role weights for centrality calculation (higher = more important)
ROLE_WEIGHTS = defaultdict(
    lambda: 0.4,
    {
        ":ARG0": 0.9,
        ":ARG0-of": 0.9,
        ":ARG1": 0.7,
        ":ARG2": 0.7,
        ":ARG3": 0.7,
        ":domain": 0.6,
        ":mod": 0.6,
    },
)


def read_amr_blocks(filepath):
    """
    Read AMR blocks from file, splitting on '('.

    Args:
        filepath: Path to .amr file.

    Returns:
        List of AMR block strings.
    """
    blocks, current = [], []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            # New block starts with '('
            if s.startswith("(") and current:
                blocks.append("\n".join(current))
                current = []
            current.append(s)
    if current:
        blocks.append("\n".join(current))
    return blocks


def build_graph_dict(triples):
    """
    Build adjacency lists from triples (forward and reverse).

    Args:
        triples: List of (source, role, target) triples.

    Returns:
        Tuple of (forward_adj, reverse_adj) dictionaries.
    """
    adj = defaultdict(list)
    rev = defaultdict(list)
    for src, role, tgt in triples:
        adj[src].append((role, tgt))
        rev[tgt].append((role, src))
    return adj, rev


def find_fairness_nodes(triples):
    """
    Find all nodes connected to fairness concepts.

    Args:
        triples: List of (source, role, target) triples.

    Returns:
        Set of node IDs connected to fairness concepts.
    """
    fairness_nodes = set()
    for src, role, tgt in triples:
        if isinstance(tgt, str) and FAIRNESS_REGEX.search(tgt):
            fairness_nodes.add(src)
    return fairness_nodes


def shortest_distances_from_root(adj, root):
    """
    Compute shortest distances from root using BFS.

    Args:
        adj: Forward adjacency dictionary.
        root: Root node ID.

    Returns:
        Dictionary mapping node -> distance from root.
    """
    dist = {root: 0}
    queue = deque([root])
    while queue:
        node = queue.popleft()
        for _, tgt in adj[node]:
            if tgt == node or tgt in dist:
                continue
            dist[tgt] = dist[node] + 1
            queue.append(tgt)
    return dist


def get_incoming_roles(rev):
    """
    Extract incoming roles for each node.

    Args:
        rev: Reverse adjacency dictionary.

    Returns:
        Dictionary mapping node -> list of incoming role names.
    """
    return {node: [r for r, _ in lst] for node, lst in rev.items()}


def fairness_score_for_graph(amr_str, graph_id):
    """
    Compute fairness centrality score for a single AMR graph.

    Score combines:
    - Role weights (ARG0, ARG1, etc. have higher weights)
    - Distance from root (closer = higher score)

    Args:
        amr_str: AMR graph string.
        graph_id: Graph identifier.

    Returns:
        Tuple of (graph_id, score, fairness_node_count, amr_str).
    """
    try:
        g = penman.decode(amr_str, model=NoOpModel())
    except Exception as e:
        print(f"[Graph {graph_id}] Decode error: {e}")
        return (graph_id, 0.0, 0, amr_str)

    adj, rev = build_graph_dict(g.triples)
    inst_map = {src: tgt for src, role, tgt in g.triples if role == ":instance"}
    fairness_nodes = find_fairness_nodes(g.triples)
    if not fairness_nodes:
        return (graph_id, 0.0, 0, amr_str)

    # Compute distances and incoming roles
    distances = shortest_distances_from_root(adj, g.top)
    incoming_roles = get_incoming_roles(rev)

    # Calculate score for each fairness node
    node_scores = []
    for fn in fairness_nodes:
        dist = distances.get(fn)
        if dist is None:
            continue
        roles = incoming_roles.get(fn, [])
        # Weight based on incoming roles (default if root, else 0.4)
        weight = max(
            [ROLE_WEIGHTS[r] for r in roles],
            default=1.0 if inst_map.get(g.top) else 0.4,
        )

        # Root node gets maximum weight and distance 0
        if fn == g.top:
            weight, dist = 1.0, 0

        # Score = weight * (1 / (1 + distance))
        node_scores.append(weight * (1 / (1 + dist)))

    if not node_scores:
        return (graph_id, 0.0, len(fairness_nodes), amr_str)

    # Return maximum score among all fairness nodes
    max_score = np.max(node_scores)
    return (graph_id, max_score, len(fairness_nodes), amr_str)


def top_k_fairness_graphs(filepath, k=5):
    """
    Find top K graphs by fairness centrality score.

    Args:
        filepath: Path to .amr file.
        k: Number of top graphs to return (default: 5).

    Returns:
        DataFrame with columns: gid, score, fairness_nodes, amr.
    """
    blocks = read_amr_blocks(filepath)
    # Score all graphs
    scored_graphs = [
        fairness_score_for_graph(block, i) for i, block in enumerate(blocks)
    ]
    # Sort by score (descending) and take top K
    scored_graphs.sort(key=lambda x: x[1], reverse=True)
    top_graphs = scored_graphs[:k]

    print(f"Top {k} graphs by fairness centrality:\n")

    df = pd.DataFrame(top_graphs, columns=["gid", "score", "fairness_nodes", "amr"])
    return df
