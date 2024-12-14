import math
import random
import tkinter as tk
from tkinter import Canvas, Label, Button, Entry
import threading

# Configuration constants
edge_probability = 0.2
node_radius = 10  # Smaller vertices
edge_width = 2
num_colors = 4
num_generations = 1000
pop_size = 50
elitism_count = 2
mutation_rate = 0.1
sleep_time = 0.1
COLOR_PALETTE = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00']

class Graph:
    def __init__(self, num_vertices, edge_probability):
        self.num_vertices = num_vertices
        self.edges = []
        self.vertex_positions = {}

        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                if random.random() < edge_probability:
                    self.edges.append((i, j))

        for i in range(num_vertices):
            angle = 2 * math.pi * i / num_vertices
            radius = 0.8
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            self.vertex_positions[i] = (x, y)

    def get_edges(self):
        return self.edges

    def get_neighbors(self, vertex):
        neighbors = []
        for edge in self.edges:
            if edge[0] == vertex:
                neighbors.append(edge[1])
            elif edge[1] == vertex:
                neighbors.append(edge[0])
        return neighbors

    def get_vertex_position(self, vertex):
        return self.vertex_positions[vertex]

class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Graph Coloring Solver")
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

        # Top bar for controls
        self.top_bar = Canvas(self, bg="#333333", height=50, highlightthickness=0)
        self.top_bar.place(x=0, y=0, width=self.width, height=50)

        Label(self.top_bar, text="Number of Vertices:", fg="white", bg="#333333", font=("Arial", 12)).place(x=20, y=15)
        self.vertices_input = Entry(self.top_bar, bg="#555555", fg="white", width=5, font=("Arial", 12))
        self.vertices_input.place(x=150, y=15)
        self.vertices_input.insert(0, "20")

        Button(self.top_bar, text="Generate Graph", command=self.generate_graph, bg="#555555", fg="white", font=("Arial", 12)).place(x=220, y=10)
        Button(self.top_bar, text="Run Algorithm", command=self.start_thread, bg="#555555", fg="white", font=("Arial", 12)).place(x=350, y=10)

        self.stats_label = Label(self.top_bar, text="", fg="white", bg="#333333", font=("Arial", 12), anchor="e")
        self.stats_label.place(x=self.width - 300, y=10, width=280)

        self.mainloop()

    def generate_graph(self):
        try:
            num_vertices = int(self.vertices_input.get())
        except ValueError:
            print("Invalid number of vertices")
            return

        self.graph = Graph(num_vertices, edge_probability)
        self.clear_canvas()
        self.draw_graph()

    def clear_canvas(self):
        self.canvas.delete("all")

    def transform_coordinates(self, x, y):
        padding = 100
        screen_x = (x + 1) * (self.width - 2 * padding) / 2 + padding
        screen_y = (y + 1) * (self.height - 2 * padding) / 2 + padding
        return screen_x, screen_y

    def draw_graph(self, coloring=None):
        if not self.graph:
            return

        for edge in self.graph.get_edges():
            v1, v2 = edge
            x1, y1 = self.graph.get_vertex_position(v1)
            x2, y2 = self.graph.get_vertex_position(v2)

            x1, y1 = self.transform_coordinates(x1, y1)
            x2, y2 = self.transform_coordinates(x2, y2)

            self.canvas.create_line(x1, y1, x2, y2, width=edge_width, fill='gray')

        for vertex in range(self.graph.num_vertices):
            x, y = self.graph.get_vertex_position(vertex)
            x, y = self.transform_coordinates(x, y)

            color = COLOR_PALETTE[coloring[vertex] if coloring else 0]

            self.canvas.create_oval(
                x - node_radius, y - node_radius,
                x + node_radius, y + node_radius,
                fill='white' if not coloring else color, outline='black', width=2
            )

    def update_stats(self, generation):
        stats_text = f"Colors used: {num_colors}  |  Current conflicts: {self.current_conflicts}  |  Best fitness: {self.best_fitness}  |  Generation: {generation}"
        self.stats_label.config(text=stats_text)

    def start_thread(self):
        if not self.graph:
            print("Generate a graph first!")
            return
        thread = threading.Thread(target=self.run)
        thread.start()

    def run(self):
        def count_conflicts(coloring):
            conflicts = 0
            for edge in self.graph.get_edges():
                v1, v2 = edge
                if coloring[v1] == coloring[v2]:
                    conflicts += 1
            return conflicts

        def fitness(genome):
            return count_conflicts(genome)

        def create_initial_population():
            population = []
            for _ in range(pop_size):
                genome = [random.randint(0, num_colors - 1) for _ in range(self.graph.num_vertices)]
                population.append(genome)
            return population

        def select_parents(population, fitnesses):
            def tournament_select():
                tournament_size = 3
                tournament = random.sample(list(enumerate(fitnesses)), tournament_size)
                winner_idx = min(tournament, key=lambda x: x[1])[0]
                return population[winner_idx]

            return tournament_select(), tournament_select()

        def crossover(parent1, parent2):
            crossover_points = sorted(random.sample(range(len(parent1)), 2))
            child = parent1[:crossover_points[0]] + \
                    parent2[crossover_points[0]:crossover_points[1]] + \
                    parent1[crossover_points[1]:]
            return child

        def mutate(genome):
            if random.random() < mutation_rate:
                point = random.randint(0, len(genome) - 1)
                new_color = random.randint(0, num_colors - 1)
                while new_color == genome[point]:
                    new_color = random.randint(0, num_colors - 1)
                genome[point] = new_color
            return genome

        def evolution_step(generation=0, population=None):
            if generation >= num_generations:
                return

            if population is None:
                population = create_initial_population()

            population_fitness = [(genome, fitness(genome)) for genome in population]
            population_fitness.sort(key=lambda x: x[1])

            best_genome = population_fitness[0][0]
            self.best_fitness = population_fitness[0][1]
            self.current_conflicts = self.best_fitness

            print(f'Generation {generation}, Conflicts: {self.best_fitness}')

            self.after(0, self.clear_canvas)
            self.after(0, self.draw_graph, best_genome)
            self.after(0, self.update_stats, generation)

            if self.best_fitness == 0:
                return

            new_population = []

            new_population.extend([genome for genome, _ in population_fitness[:elitism_count]])

            while len(new_population) < pop_size:
                parent1, parent2 = select_parents(
                    [genome for genome, _ in population_fitness],
                    [fitness for _, fitness in population_fitness]
                )
                child = crossover(parent1, parent2)
                child = mutate(child)
                new_population.append(child)

            self.after(int(sleep_time * 1000), evolution_step, generation + 1, new_population)

        evolution_step()

if __name__ == "__main__":
    UI()
