import math
import random
import tkinter as tk
from tkinter import Canvas, Label, Button, Entry
import threading

# Configuration constants
EDGE_CHANCE = 0.2
VERTEX_SIZE = 10
LINE_THICKNESS = 1
TOTAL_ITERATIONS = 1000
POPULATION_COUNT = 50
ELITE_SURVIVORS = 2
GENE_ALTERATION_RATE = 0.1
RENDER_DELAY = 0.1

CHROMATIC_SPECTRUM = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500',
    '#800080', '#008000', '#000080', '#FFD700', '#00CED1', '#FF4500', '#7FFF00',
    '#DC143C', '#1E90FF', '#DAA520', '#32CD32', '#B22222', '#FF69B4'
]


class NetworkStructure:
    def __init__(self, vertex_count, edge_chance):
        self.vertex_count = vertex_count
        self.connections = []
        self.node_locations = {}

        for i in range(vertex_count):
            for j in range(i + 1, vertex_count):
                if random.random() < edge_chance:
                    self.connections.append((i, j))

        for i in range(vertex_count):
            theta = 2 * math.pi * i / vertex_count
            r = 0.8
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            self.node_locations[i] = (x, y)

    def fetch_connections(self):
        return self.connections

    def find_adjacent_nodes(self, node):
        adjacent = []
        for edge in self.connections:
            if edge[0] == node:
                adjacent.append(edge[1])
            elif edge[1] == node:
                adjacent.append(edge[0])
        return adjacent

    def get_node_position(self, node):
        return self.node_locations[node]


class VisualInterface(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Vertex Coloring Problem")
        self.configure(bg="#1A1A1D")
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.width, self.height))
        self.state("zoomed")

        self.display = Canvas(self, bg="#1A1A1D", highlightthickness=0)
        self.display.place(x=0, y=50, width=self.width, height=self.height - 50)

        self.network = None
        self.optimal_score = float('inf')
        self.current_violations = 0

        self.setup_control_panel()
        self.mainloop()

    def setup_control_panel(self):
        control_panel = Canvas(self, bg="#333333", height=50, highlightthickness=0)
        control_panel.place(x=0, y=0, width=self.width, height=50)

        Label(control_panel, text="Vertex Count:", fg="white", bg="#333333", font=("Arial", 12)).place(x=20, y=15)
        self.vertex_input = Entry(control_panel, bg="#555555", fg="white", width=5, font=("Arial", 12))
        self.vertex_input.place(x=150, y=15)
        self.vertex_input.insert(0, "20")

        Label(control_panel, text="Color Count:", fg="white", bg="#333333", font=("Arial", 12)).place(x=220, y=15)
        self.color_input = Entry(control_panel, bg="#555555", fg="white", width=5, font=("Arial", 12))
        self.color_input.place(x=340, y=15)
        self.color_input.insert(0, "4")

        Button(control_panel, text="Create Vertices", command=self.create_network, bg="#555555", fg="black",
               font=("Arial", 12)).place(x=420, y=10)
        Button(control_panel, text="Start Solver", command=self.initiate_thread, bg="#555555", fg="black",
               font=("Arial", 12)).place(x=550, y=10)

        self.status_display = Label(control_panel, text="", fg="white", bg="#333333", font=("Arial", 12), anchor="e")
        self.status_display.place(x=self.width - 450, y=10, width=450)

    def create_network(self):
        try:
            vertex_count = int(self.vertex_input.get())
            self.color_count = int(self.color_input.get())
        except ValueError:
            print("Invalid input for vertices or colors")
            return

        self.network = NetworkStructure(vertex_count, EDGE_CHANCE)
        self.clear_display()
        self.render_network()

    def clear_display(self):
        self.display.delete("all")

    def adjust_coordinates(self, x, y):
        margin = 150
        screen_x = (x + 1) * (self.width - 2 * margin) / 2 + margin
        screen_y = (y + 1) * (self.height - 2 * margin) / 2
        return screen_x, screen_y

    def render_network(self, coloring=None):
        if not self.network:
            return

        for edge in self.network.fetch_connections():
            v1, v2 = edge
            x1, y1 = self.network.get_node_position(v1)
            x2, y2 = self.network.get_node_position(v2)
            x1, y1 = self.adjust_coordinates(x1, y1)
            x2, y2 = self.adjust_coordinates(x2, y2)
            self.display.create_line(x1, y1, x2, y2, width=LINE_THICKNESS, fill='gray', dash=(5, 5))

        for vertex in range(self.network.vertex_count):
            x, y = self.network.get_node_position(vertex)
            x, y = self.adjust_coordinates(x, y)
            color = CHROMATIC_SPECTRUM[coloring[vertex] if coloring else 0]
            self.display.create_oval(
                x - VERTEX_SIZE, y - VERTEX_SIZE,
                x + VERTEX_SIZE, y + VERTEX_SIZE,
                fill='white' if not coloring else color,
                outline='black', width=2
            )

    def update_status(self, iteration):
        status_text = f"Colors used: {self.color_count} | Conflicts: {self.current_violations} | Best fitness: {self.optimal_score} | Generation: {iteration}"
        self.status_display.config(text=status_text)

    def initiate_thread(self):
        if not self.network:
            print("Create a network first!")
            return
        thread = threading.Thread(target=self.optimize)
        thread.start()

    def optimize(self):
        def count_violations(coloring):
            violations = 0
            for edge in self.network.fetch_connections():
                v1, v2 = edge
                if coloring[v1] == coloring[v2]:
                    violations += 1
            return violations

        def calculate_fitness(genome):
            return count_violations(genome)

        def initialize_population():
            return [[random.randint(0, self.color_count - 1) for _ in range(self.network.vertex_count)] for _ in
                    range(POPULATION_COUNT)]

        def select_breeding_pair(population, fitnesses):
            def tournament():
                contestants = random.sample(list(enumerate(fitnesses)), 3)
                winner_idx = min(contestants, key=lambda x: x[1])[0]
                return population[winner_idx]

            return tournament(), tournament()

        def breed(parent1, parent2):
            crossover_points = sorted(random.sample(range(len(parent1)), 2))
            child = parent1[:crossover_points[0]] + parent2[crossover_points[0]:crossover_points[1]] + parent1[
                                                                                                       crossover_points[
                                                                                                           1]:]
            return child

        def mutate(genome):
            if random.random() < GENE_ALTERATION_RATE:
                point = random.randint(0, len(genome) - 1)
                new_color = random.randint(0, self.color_count - 1)
                while new_color == genome[point]:
                    new_color = random.randint(0, self.color_count - 1)
                genome[point] = new_color
            return genome

        def evolution_cycle(iteration=0, population=None):
            if iteration >= TOTAL_ITERATIONS:
                return

            if population is None:
                population = initialize_population()

            population_fitness = [(genome, calculate_fitness(genome)) for genome in population]
            population_fitness.sort(key=lambda x: x[1])

            fittest_genome = population_fitness[0][0]
            self.optimal_score = population_fitness[0][1]
            self.current_violations = self.optimal_score

            print(f'Generation {iteration}, Current Conflicts: {self.optimal_score}')
            self.after(0, self.clear_display)
            self.after(0, self.render_network, fittest_genome)
            self.after(0, self.update_status, iteration)

            if self.optimal_score == 0:
                return

            next_generation = []
            next_generation.extend([genome for genome, _ in population_fitness[:ELITE_SURVIVORS]])

            while len(next_generation) < POPULATION_COUNT:
                parent1, parent2 = select_breeding_pair(
                    [genome for genome, _ in population_fitness],
                    [fitness for _, fitness in population_fitness]
                )
                offspring = breed(parent1, parent2)
                offspring = mutate(offspring)
                next_generation.append(offspring)

            self.after(int(RENDER_DELAY * 1000), evolution_cycle, iteration + 1, next_generation)

        evolution_cycle()


if __name__ == "__main__":
    VisualInterface()
