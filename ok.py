import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import time

# -----------------------------
# Vertex coloring algorithms with steps for animation
# -----------------------------
def greedy_coloring_steps(G):
    colors = {}
    steps = []
    for node in G.nodes():
        used = {colors[n] for n in G.neighbors(node) if n in colors}
        color = 0
        while color in used:
            color += 1
        colors[node] = color
        steps.append(colors.copy())
    return steps

def dsatur_coloring_steps(G):
    colors = {}
    steps = []
    saturation = {node: 0 for node in G.nodes()}
    degrees = dict(G.degree())
    uncolored = set(G.nodes())

    while uncolored:
        max_sat = -1
        candidates = []
        for node in uncolored:
            if saturation[node] > max_sat:
                max_sat = saturation[node]
                candidates = [node]
            elif saturation[node] == max_sat:
                candidates.append(node)
        node_to_color = max(candidates, key=lambda n: degrees[n])

        used = {colors[n] for n in G.neighbors(node_to_color) if n in colors}
        color = 0
        while color in used:
            color += 1
        colors[node_to_color] = color
        steps.append(colors.copy())

        for neighbor in G.neighbors(node_to_color):
            if neighbor in uncolored:
                neighbor_colors = {colors[n] for n in G.neighbors(neighbor) if n in colors}
                saturation[neighbor] = len(neighbor_colors)

        uncolored.remove(node_to_color)

    return steps

# -----------------------------
# Edge coloring algorithms using line graph
# -----------------------------
def greedy_edge_coloring_steps(G):
    LG = nx.line_graph(G)
    steps_nodes = greedy_coloring_steps(LG)
    steps_edges = []
    for step in steps_nodes:
        edge_colors = {edge: color for edge, color in step.items()}
        steps_edges.append(edge_colors)
    return steps_edges

def dsatur_edge_coloring_steps(G):
    LG = nx.line_graph(G)
    steps_nodes = dsatur_coloring_steps(LG)
    steps_edges = []
    for step in steps_nodes:
        edge_colors = {edge: color for edge, color in step.items()}
        steps_edges.append(edge_colors)
    return steps_edges

# -----------------------------
# Graph generation
# -----------------------------
def generate_graphs():
    graphs = []

    for p in [0.05, 0.1, 0.2]:
        G = nx.erdos_renyi_graph(15, p, seed=1)
        graphs.append(("Erdos-Renyi p="+str(p), G))

    G_cycle = nx.cycle_graph(10)
    graphs.append(("Cycle Graph", G_cycle))

    G_clique = nx.complete_graph(8)
    graphs.append(("Clique Graph", G_clique))

    G_bipartite = nx.complete_bipartite_graph(5, 5)
    graphs.append(("Bipartite Graph", G_bipartite))

    return graphs

# -----------------------------
# Animation function for vertices and edges
# -----------------------------
def animate_graph_edges_vertices(G, vertex_steps, edge_steps, filename="graph_edges_vertices.gif", title="Graph Coloring Animation"):
    pos = nx.circular_layout(G)
    node_palette = ['red', 'green', 'blue', 'orange', 'purple', 'cyan', 'magenta']
    edge_palette = ['black', 'brown', 'pink', 'gray', 'olive', 'cyan', 'purple']
    fig, ax = plt.subplots(figsize=(6,6))

    n_frames = max(len(vertex_steps), len(edge_steps))

    def update(frame):
        ax.clear()
        ax.set_title(title)
        ax.axis('off')
        
        node_step = vertex_steps[min(frame, len(vertex_steps)-1)]
        node_colors = [node_palette[node_step[n]%len(node_palette)] if n in node_step else "lightgray" for n in G.nodes()]

        edge_step = edge_steps[min(frame, len(edge_steps)-1)]
        edge_colors = [edge_palette[edge_step[e]%len(edge_palette)] if e in edge_step else "lightgray" for e in G.edges()]

        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=2)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=400, ax=ax)
        nx.draw_networkx_labels(G, pos, ax=ax)

    ani = FuncAnimation(fig, update, frames=n_frames, repeat=False)
    ani.save(filename, writer=PillowWriter(fps=1))
    plt.close(fig)

# -----------------------------
# Main testing function
# -----------------------------
def run_tests_with_edges():
    graphs = generate_graphs()
    results = []

    for name, G in graphs:
        # Vertex coloring
        t0 = time.time()
        v_steps_greedy = greedy_coloring_steps(G)
        t_greedy_v = time.time() - t0
        n_colors_v_greedy = len(set(list(v_steps_greedy[-1].values())))

        t0 = time.time()
        v_steps_dsatur = dsatur_coloring_steps(G)
        t_dsatur_v = time.time() - t0
        n_colors_v_dsatur = len(set(list(v_steps_dsatur[-1].values())))

        # Edge coloring
        t0 = time.time()
        e_steps_greedy = greedy_edge_coloring_steps(G)
        t_greedy_e = time.time() - t0
        n_colors_e_greedy = len(set(list(e_steps_greedy[-1].values())))

        t0 = time.time()
        e_steps_dsatur = dsatur_edge_coloring_steps(G)
        t_dsatur_e = time.time() - t0
        n_colors_e_dsatur = len(set(list(e_steps_dsatur[-1].values())))

        # Animations
        animate_graph_edges_vertices(G, v_steps_greedy, e_steps_greedy, filename=f"{name}_greedy_edges_vertices.gif", title=f"{name} - Greedy")
        animate_graph_edges_vertices(G, v_steps_dsatur, e_steps_dsatur, filename=f"{name}_dsatur_edges_vertices.gif", title=f"{name} - DSATUR")

        results.append({
            "Graph": name,
            "Vertex Colors Greedy": n_colors_v_greedy,
            "Vertex Colors DSATUR": n_colors_v_dsatur,
            "Edge Colors Greedy": n_colors_e_greedy,
            "Edge Colors DSATUR": n_colors_e_dsatur,
            "Vertex Time Greedy": t_greedy_v,
            "Vertex Time DSATUR": t_dsatur_v,
            "Edge Time Greedy": t_greedy_e,
            "Edge Time DSATUR": t_dsatur_e
        })

    return results

# -----------------------------
# Display results
# -----------------------------
def print_table_edges_vertices(results):
    header = f"{'Graph':25} | {'V_Greedy#':10} | {'V_DSATUR#':10} | {'E_Greedy#':10} | {'E_DSATUR#':10}"
    print(header)
    print("-"*80)
    for r in results:
        print(f"{r['Graph']:25} | {r['Vertex Colors Greedy']:10} | {r['Vertex Colors DSATUR']:10} | {r['Edge Colors Greedy']:10} | {r['Edge Colors DSATUR']:10}")

# -----------------------------
# Main execution
# -----------------------------
if __name__ == "__main__":
    results = run_tests_with_edges()
    print_table_edges_vertices(results)
