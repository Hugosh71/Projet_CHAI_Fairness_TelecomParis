import penman
from penman.models.noop import NoOpModel
import re
import pandas as pd
import numpy as np
from collections import defaultdict, deque
from pathlib import Path

FAIRNESS_REGEX = re.compile(r"Fairness|fairness|fair-[0-9]+", re.IGNORECASE)

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
    """Parse AMR blocks starting at '('."""
    blocks, current = [], []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.startswith("(") and current:
                blocks.append("\n".join(current))
                current = []
            current.append(s)
    if current:
        blocks.append("\n".join(current))
    return blocks


def build_graph_dict(triples):
    adj = defaultdict(list)
    rev = defaultdict(list)
    for src, role, tgt in triples:
        adj[src].append((role, tgt))
        rev[tgt].append((role, src))
    return adj, rev


def find_fairness_nodes(triples):
    fairness_nodes = set()
    for src, role, tgt in triples:
        if isinstance(tgt, str) and FAIRNESS_REGEX.search(tgt):
            fairness_nodes.add(src)
    return fairness_nodes


def shortest_distances_from_root(adj, root):
    """Compute shortest BFS distances from root to all reachable nodes."""
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
    return {node: [r for r, _ in lst] for node, lst in rev.items()}


def fairness_score_for_graph(amr_str, graph_id):
    """
    Compute a fairness centrality score for a single AMR graph.
    Returns (graph_id, score, fairness_node_count, amr_str).
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

    distances = shortest_distances_from_root(adj, g.top)
    incoming_roles = get_incoming_roles(rev)

    node_scores = []
    for fn in fairness_nodes:
        dist = distances.get(fn)
        if dist is None:
            continue
        roles = incoming_roles.get(fn, [])
        weight = max(
            [ROLE_WEIGHTS[r] for r in roles],
            default=1.0 if inst_map.get(g.top) else 0.4,
        )

        if fn == g.top:
            weight, dist = 1.0, 0

        node_scores.append(weight * (1 / (1 + dist)))

    if not node_scores:
        return (graph_id, 0.0, len(fairness_nodes), amr_str)

    max_score = np.max(node_scores)

    return (graph_id, max_score, len(fairness_nodes), amr_str)


def top_k_fairness_graphs(filepath, k=5):
    blocks = read_amr_blocks(filepath)
    scored_graphs = [
        fairness_score_for_graph(block, i) for i, block in enumerate(blocks)
    ]
    scored_graphs.sort(key=lambda x: x[1], reverse=True)
    top_graphs = scored_graphs[:k]

    print(f"Top {k} graphs by fairness centrality:\n")

    df = pd.DataFrame(top_graphs, columns=["gid", "score", "fairness_nodes", "amr"])

    return df
