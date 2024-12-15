import math
import random
import tkinter as tk
from tkinter import Canvas, Label, Button, Entry
import threading

# Configuration constants
EDGE_PROBABILITY = 0.2
NODE_RADIUS = 10
EDGE_WIDTH = 1
MAX_GENERATIONS = 1000
GENOME_COUNT = 50
TOP_PERFORMERS = 2
MUTATION_RATE = 0.1
VISUALIZATION_INTERVAL = 0.1

color_palette = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500',
    '#800080', '#008000', '#000080', '#FFD700', '#00CED1', '#FF4500', '#7FFF00',
    '#DC143C', '#1E90FF', '#DAA520', '#32CD32', '#B22222', '#FF69B4'
]

class VertexColoringGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Vertex Coloring Visualization")
        self.configure(bg="#1A1A1D")
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.width, self.height))
        self.state("zoomed")
        self.canvas = Canvas(self, bg="#1A1A1D", highlightthickness=0)
        self.canvas.place(x=0, y=50, width=self.width, height=self.height - 50)
        self.graph = None
        self.best_fitness = float('inf')
        self.current_conflicts = 0
        self.initialize_control_panel()
        self.mainloop()

    def initialize_control_panel(self):
        control_panel = Canvas(self, bg="#333333", height=50, highlightthickness=0)
        control_panel.place(x=0, y=0, width=self.width, height=50)

        Label(control_panel, text="Number of Nodes:", fg="white", bg="#333333", font=("Arial", 12)).place(x=20, y=15)
        self.node_entry = Entry(control_panel, bg="#555555", fg="white", width=5, font=("Arial", 12))
        self.node_entry.place(x=150, y=15)
        self.node_entry.insert(0, "20")

        Label(control_panel, text="Number of Colors:", fg="white", bg="#333333", font=("Arial", 12)).place(x=220, y=15)
        self.color_entry = Entry(control_panel, bg="#555555", fg="white", width=5, font=("Arial", 12))
        self.color_entry.place(x=340, y=15)
        self.color_entry.insert(0, "4")

        Button(control_panel, text="Generate Vertices", command=self.generate_vertex, bg="#555555", fg="black",
               font=("Arial", 12)).place(x=420, y=10)
        Button(control_panel, text="Run Algorithm", command=self.start_optimization, bg="#555555", fg="black",
               font=("Arial", 12)).place(x=550, y=10)

        self.status_label = Label(control_panel, text="", fg="white", bg="#333333", font=("Arial", 12), anchor="e")
        self.status_label.place(x=self.width - 450, y=10, width=450)

    def generate_vertex(self):
        try:
            node_count = int(self.node_entry.get())
            self.color_count = int(self.color_entry.get())
        except ValueError:
            print("Invalid input for nodes or colors")
            return

        self.graph = GraphTopology(node_count, EDGE_PROBABILITY)
        self.clear_canvas()
        self.draw_vertex()

    def clear_canvas(self):
        self.canvas.delete("all")

    def scale_coordinates(self, x, y):
        margin = 150
        screen_x = (x + 1) * (self.width - 2 * margin) / 2 + margin
        screen_y = (y + 1) * (self.height - 2 * margin) / 2
        return screen_x, screen_y

    def draw_vertex(self, coloring=None):
        if not self.graph:
            return

        for edge in self.graph.get_edges():
            v1, v2 = edge
            x1, y1 = self.graph.get_node_position(v1)
            x2, y2 = self.graph.get_node_position(v2)
            x1, y1 = self.scale_coordinates(x1, y1)
            x2, y2 = self.scale_coordinates(x2, y2)
            self.canvas.create_line(x1, y1, x2, y2, width=EDGE_WIDTH, fill='gray', dash=(5, 5))

        for node in range(self.graph.node_count):
            x, y = self.graph.get_node_position(node)
            x, y = self.scale_coordinates(x, y)
            color = color_palette[coloring[node] if coloring else 0]
            self.canvas.create_oval(
                x - NODE_RADIUS, y - NODE_RADIUS,
                x + NODE_RADIUS, y + NODE_RADIUS,
                fill='white' if not coloring else color,
                outline='black', width=2
            )

    def update_status_display(self, generation):
        status_text = f"Colors: {self.color_count} | Conflicts: {self.current_conflicts} | Best Score: {self.best_fitness} | Generation: {generation}"
        self.status_label.config(text=status_text)

    def start_optimization(self):
        if not self.graph:
            print("Generate a graph first!")
            return
        thread = threading.Thread(target=self.run_optimization)
        thread.start()

    def run_optimization(self):
        def calculate_conflicts(coloring):
            conflicts = 0
            for edge in self.graph.get_edges():
                v1, v2 = edge
                if coloring[v1] == coloring[v2]:
                    conflicts += 1
            return conflicts

        def evaluate_fitness(genome):
            return calculate_conflicts(genome)

        def create_initial_population():
            return [[random.randint(0, self.color_count - 1) for _ in range(self.graph.node_count)] for _ in
                    range(GENOME_COUNT)]

        def choose_parents(population, fitnesses):
            def tournament():
                participants = random.sample(list(enumerate(fitnesses)), 3)
                winner_idx = min(participants, key=lambda x: x[1])[0]
                return population[winner_idx]

            return tournament(), tournament()

        def crossover(parent1, parent2):
            split_points = sorted(random.sample(range(len(parent1)), 2))
            child = parent1[:split_points[0]] + parent2[split_points[0]:split_points[1]] + parent1[split_points[1]:]
            return child

        def apply_mutation(genome):
            if random.random() < MUTATION_RATE:
                gene = random.randint(0, len(genome) - 1)
                new_color = random.randint(0, self.color_count - 1)
                while new_color == genome[gene]:
                    new_color = random.randint(0, self.color_count - 1)
                genome[gene] = new_color
            return genome

        def genetic_algorithm(generation=0, population=None):
            if generation >= MAX_GENERATIONS:
                return

            if population is None:
                population = create_initial_population()

            population_fitness = [(genome, evaluate_fitness(genome)) for genome in population]
            population_fitness.sort(key=lambda x: x[1])

            best_genome = population_fitness[0][0]
            self.best_fitness = population_fitness[0][1]
            self.current_conflicts = self.best_fitness

            print(f'Generation {generation}, Current Conflicts: {self.best_fitness}')
            self.after(0, self.clear_canvas)
            self.after(0, self.draw_vertex, best_genome)
            self.after(0, self.update_status_display, generation)

            if self.best_fitness == 0:
                return

            next_generation = []
            next_generation.extend([genome for genome, _ in population_fitness[:TOP_PERFORMERS]])

            while len(next_generation) < GENOME_COUNT:
                parent1, parent2 = choose_parents(
                    [genome for genome, _ in population_fitness],
                    [fitness for _, fitness in population_fitness]
                )
                offspring = crossover(parent1, parent2)
                offspring = apply_mutation(offspring)
                next_generation.append(offspring)

            self.after(int(VISUALIZATION_INTERVAL * 1000), genetic_algorithm, generation + 1, next_generation)

        genetic_algorithm()

        class GraphTopology:
            def __init__(self, node_count, EDGE_PROBABILITY):
                self.node_count = node_count
                self.edges = []
                self.node_coordinates = {}

                for i in range(node_count):
                    for j in range(i + 1, node_count):
                        if random.random() < EDGE_PROBABILITY:
                            self.edges.append((i, j))

                for i in range(node_count):
                    angle = 2 * math.pi * i / node_count
                    radius = 0.8
                    x = radius * math.cos(angle)
                    y = radius * math.sin(angle)
                    self.node_coordinates[i] = (x, y)

            def get_edges(self):
                return self.edges

            def get_neighbors(self, node):
                neighbors = []
                for edge in self.edges:
                    if edge[0] == node:
                        neighbors.append(edge[1])
                    elif edge[1] == node:
                        neighbors.append(edge[0])
                return neighbors

            def get_node_position(self, node):
                return self.node_coordinates[node]

class GraphTopology:
    def __init__(self, node_count, EDGE_PROBABILITY):
        self.node_count = node_count
        self.edges = []
        self.node_coordinates = {}

        for i in range(node_count):
            for j in range(i + 1, node_count):
                if random.random() < EDGE_PROBABILITY:
                    self.edges.append((i, j))

        for i in range(node_count):
            angle = 2 * math.pi * i / node_count
            radius = 0.8
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            self.node_coordinates[i] = (x, y)

    def get_edges(self):
        return self.edges

    def get_neighbors(self, node):
        neighbors = []
        for edge in self.edges:
            if edge[0] == node:
                neighbors.append(edge[1])
            elif edge[1] == node:
                neighbors.append(edge[0])
        return neighbors

    def get_node_position(self, node):
        return self.node_coordinates[node]


if __name__ == "__main__":
    VertexColoringGUI()
