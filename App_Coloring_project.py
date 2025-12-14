import customtkinter as ctk
import networkx as nx
from PIL import Image
from PIL.ImageTk import PhotoImage
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import os, time

# -------------------------------
# COLOR PALETTE
# -------------------------------
PALETTE = ["#FF4D6D", "#FF9F1C", "#2EC4B6", "#E71D36", "#FFBF69", "#8338EC", "#3A86FF"]

# -------------------------------
# GRAPH COLORING ALGORITHMS
# -------------------------------
def greedy_steps(G):
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

def wp_steps(G):
    order = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)
    colors = {}
    steps = []
    for node in order:
        used = {colors[n] for n in G.neighbors(node) if n in colors}
        color = 0
        while color in used:
            color += 1
        colors[node] = color
        steps.append(colors.copy())
    return steps

def dsatur_steps(G):
    colors = {}
    steps = []
    saturation = {n:0 for n in G.nodes()}
    degrees = dict(G.degree())
    uncolored = set(G.nodes())
    while uncolored:
        node = max(uncolored, key=lambda x: (saturation[x], degrees[x]))
        used = {colors[n] for n in G.neighbors(node) if n in colors}
        color = 0
        while color in used:
            color += 1
        colors[node] = color
        steps.append(colors.copy())
        for neigh in G.neighbors(node):
            if neigh in uncolored:
                neighbor_colors = {colors[n] for n in G.neighbors(neigh) if n in colors}
                saturation[neigh] = len(neighbor_colors)
        uncolored.remove(node)
    return steps

def edge_coloring_steps(G):
    LG = nx.line_graph(G)
    steps = greedy_steps(LG)
    edge_steps = []
    for s in steps:
        converted = {}
        for edge_node in s:
            converted[edge_node] = s[edge_node]
        edge_steps.append(converted)
    return edge_steps

# -------------------------------
# GRAPH GENERATION
# -------------------------------
def generate_graph(graph_type, n, p):
    if graph_type == "Cycle":
        return nx.cycle_graph(n)
    elif graph_type == "Aléatoire":
        return nx.erdos_renyi_graph(n, p, seed=1)
    elif graph_type == "Biparti":
        return nx.complete_bipartite_graph(n//2, n-n//2)
    else:
        return nx.Graph()

# -------------------------------
# CREATE SMOOTH ANIMATION GIF
# -------------------------------
def create_animation(G, steps, filename="graph.gif", edge_mode=False):
    pos = nx.spring_layout(G, seed=1)
    fig, ax = plt.subplots(figsize=(5,5))
    fig.patch.set_facecolor("#1C1C1C")

    def update(step):
        ax.clear()
        ax.set_facecolor("#1C1C1C")
        ax.axis('off')
        if edge_mode:
            nx.draw_networkx_nodes(G, pos, node_color="#333333", node_size=400, ax=ax)
            e_colors = []
            for e in G.edges():
                if e in step:
                    e_colors.append(PALETTE[step[e] % len(PALETTE)])
                elif (e[1], e[0]) in step:
                    e_colors.append(PALETTE[step[(e[1], e[0])] % len(PALETTE)])
                else:
                    e_colors.append("#555555")
            nx.draw_networkx_edges(G, pos, edge_color=e_colors, width=3.5, ax=ax)
            nx.draw_networkx_labels(G, pos, font_color="white", ax=ax)
        else:
            node_colors = []
            for node in G.nodes():
                if node in step:
                    node_colors.append(PALETTE[step[node] % len(PALETTE)])
                else:
                    node_colors.append("#333333")
            nx.draw(G, pos, ax=ax, node_color=node_colors, edge_color="#555555",
                    node_size=400, width=2.5, with_labels=True, font_color="white")
    ani = FuncAnimation(fig, update, frames=steps, repeat=False)
    ani.save(filename, writer=PillowWriter(fps=2))
    plt.close(fig)

# -------------------------------
# MAIN GUI
# -------------------------------
class GraphApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("✨ Modern Graph Coloring Visualizer")
        self.geometry("1250x650")
        self.configure(bg="#121212")

        # Left panel
        self.frame_left = ctk.CTkFrame(self, corner_radius=12)
        self.frame_left.pack(side="left", fill="y", padx=15, pady=15)
        ctk.CTkLabel(self.frame_left, text="Graph Coloring Tool", font=("Segoe UI", 20, "bold")).pack(pady=10)

        # Inputs
        ctk.CTkLabel(self.frame_left, text="Nombre de sommets (n)").pack(anchor="w", pady=5)
        self.entry_n = ctk.CTkEntry(self.frame_left)
        self.entry_n.insert(0,"12")
        self.entry_n.pack(fill="x", pady=3)

        ctk.CTkLabel(self.frame_left, text="Type de graphe").pack(anchor="w", pady=5)
        self.graph_type_var = ctk.StringVar(value="Cycle")
        self.combo_graph = ctk.CTkComboBox(self.frame_left, values=["Cycle","Aléatoire","Biparti"], variable=self.graph_type_var)
        self.combo_graph.pack(fill="x", pady=3)

        ctk.CTkLabel(self.frame_left, text="Probabilité p (aléatoire)").pack(anchor="w", pady=5)
        self.entry_p = ctk.CTkEntry(self.frame_left)
        self.entry_p.insert(0,"0.2")
        self.entry_p.pack(fill="x", pady=3)

        ctk.CTkLabel(self.frame_left, text="Mode").pack(anchor="w", pady=5)
        self.mode_var = ctk.StringVar(value="Sommet")
        self.combo_mode = ctk.CTkComboBox(self.frame_left, values=["Sommet","Arête"], variable=self.mode_var)
        self.combo_mode.pack(fill="x", pady=3)

        ctk.CTkLabel(self.frame_left, text="Algorithme").pack(anchor="w", pady=5)
        self.algo_var = ctk.StringVar(value="Greedy")
        self.combo_algo = ctk.CTkComboBox(self.frame_left, values=["Greedy","Welsh-Powell","DSATUR"], variable=self.algo_var)
        self.combo_algo.pack(fill="x", pady=3)

        self.btn_run = ctk.CTkButton(self.frame_left, text="🚀 Générer & Colorier", command=self.run)
        self.btn_run.pack(pady=20, fill="x")

        self.label_result = ctk.CTkLabel(self.frame_left, text="Résultat…")
        self.label_result.pack(pady=10)

        # Right panel
        self.frame_graph = ctk.CTkFrame(self, corner_radius=12)
        self.frame_graph.pack(side="right", fill="both", expand=True, padx=15, pady=15)
        self.current_label = None

        # Delete button
        self.btn_delete = ctk.CTkButton(
            self.frame_graph,
            text="🗑️ Supprimer Graph",
            command=self.delete_graph,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        self.btn_delete.pack(side="bottom", anchor="e", padx=10, pady=10)

    def delete_graph(self):
        if self.current_label:
            self.current_label.destroy()
            self.current_label = None
        if os.path.exists("graph.gif"):
            os.remove("graph.gif")
        self.label_result.configure(text="Graph supprimé.")

    def run(self):
        # Remove old graph
        if self.current_label:
            self.current_label.destroy()
            self.current_label = None

        n = int(self.entry_n.get())
        p = float(self.entry_p.get())
        graph_type = self.graph_type_var.get()
        mode = self.mode_var.get()
        algo = self.algo_var.get()

        G = generate_graph(graph_type, n, p)

        # Choose algorithm
        t0 = time.time()
        if mode=="Sommet":
            if algo=="Greedy":
                steps = greedy_steps(G)
            elif algo=="Welsh-Powell":
                steps = wp_steps(G)
            else:
                steps = dsatur_steps(G)
            edge_mode = False
            nb_colors = len(set(steps[-1].values()))
        else:
            steps = edge_coloring_steps(G)
            edge_mode = True
            nb_colors = len(set(steps[-1].values()))
        t = time.time()-t0
        self.label_result.configure(text=f"{nb_colors} couleurs – {t:.4f}s")

        create_animation(G, steps, filename="graph.gif", edge_mode=edge_mode)

        gif = Image.open("graph.gif")
        frames=[]
        try:
            while True:
                frames.append(PhotoImage(gif.copy()))
                gif.seek(len(frames))
        except EOFError:
            pass

        self.current_label = ctk.CTkLabel(self.frame_graph, text="", fg_color="#121212")
        self.current_label.pack(expand=True)

        # Animate GIF smoothly
        def animate(i=0):
            self.current_label.configure(image=frames[i])
            self.after(300, animate, (i+1)%len(frames))
        animate()

if __name__=="__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = GraphApp()
    app.mainloop()
