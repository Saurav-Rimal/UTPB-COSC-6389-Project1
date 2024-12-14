import math
import random
import tkinter as tk
from tkinter import messagebox
import os

os.environ['PYTHONWARNINGS'] = 'ignore'

city_count = 25
node_size = 7  # Slightly larger node size
connection_thickness = 1
margin = 50

class Node:
    def __init__(self, x, y, identifier):
        self.x = x
        self.y = y
        self.identifier = identifier

    def render(self, canvas, hue='white'):
        canvas.create_oval(
            self.x - node_size, self.y - node_size,
            self.x + node_size, self.y + node_size,
            fill=hue, outline=hue
        )

class Edge:
    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination
        self.length = math.hypot(origin.x - destination.x, origin.y - destination.y)

    def render(self, canvas, hue='red', dotted=False):
        options = {'fill': hue, 'width': connection_thickness}
        if dotted:
            options['dash'] = (4, 2)
        canvas.create_line(
            self.origin.x, self.origin.y,
            self.destination.x, self.destination.y,
            **options
        )

class RouteOptimizer:
    def __init__(self, nodes):
        self.nodes = nodes
        self.node_count = len(nodes)
        self.distance_grid = self.build_distance_grid()
        self.current_route = list(range(self.node_count))
        random.shuffle(self.current_route)
        self.optimal_route = self.current_route[:]
        self.shortest_distance = self.compute_route_length(self.optimal_route)
        self.heat = 10000
        self.cooling_factor = 0.995

    def build_distance_grid(self):
        grid = [[0] * self.node_count for _ in range(self.node_count)]
        for i in range(self.node_count):
            for j in range(i + 1, self.node_count):
                distance = math.hypot(
                    self.nodes[i].x - self.nodes[j].x,
                    self.nodes[i].y - self.nodes[j].y
                )
                grid[i][j] = distance
                grid[j][i] = distance
        return grid

    def compute_route_length(self, route):
        total = 0
        for i in range(len(route)):
            a, b = route[i], route[(i + 1) % len(route)]
            total += self.distance_grid[a][b]
        return total

    def swap_nodes(self, route):
        new_route = route[:]
        i, j = random.sample(range(self.node_count), 2)
        new_route[i], new_route[j] = new_route[j], new_route[i]
        return new_route

    def optimize(self):
        candidate_route = self.swap_nodes(self.current_route)
        current_length = self.compute_route_length(self.current_route)
        candidate_length = self.compute_route_length(candidate_route)
        if self.should_accept(current_length, candidate_length, self.heat):
            self.current_route = candidate_route
            current_length = candidate_length
            if current_length < self.shortest_distance:
                self.shortest_distance = current_length
                self.optimal_route = self.current_route[:]
        self.heat *= self.cooling_factor

    def should_accept(self, current, candidate, temp):
        if candidate < current:
            return True
        return random.random() < math.exp((current - candidate) / temp)

class TravelingSalesmanGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Traveling Salesman Problem")
        self.geometry("1024x700")
        self.configure(bg="#0F0F0F")

        self.top_bar = tk.Frame(self, bg="#333333", height=100)
        self.top_bar.pack(side=tk.TOP, fill=tk.X, pady=0)


        self.canvas = tk.Canvas(self, bg="#0F0F0F", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.node_collection = []
        self.optimizer = None
        self.active = False

        self.create_top_buttons()

    def create_top_buttons(self):
        button_width = 15
        button_style = {
            "bg": "#1E1E1E",
            "fg": "black",
            "activebackground": "#3E3E3E",
            "activeforeground": "red",
            "bd": 2,
            "font": ("Arial", 12, "bold"),
            "width": button_width,
            "height": 1
        }

        tk.Button(self.top_bar, text="Generate Nodes", command=self.populate, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(self.top_bar, text="Begin Optimization", command=self.initiate_optimizer, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(self.top_bar, text="Clear", command=self.clear, **button_style).pack(side=tk.LEFT, padx=5)

        self.info_bar = tk.Label(self.top_bar, text="Optimal Route Length: ", anchor="e", fg="#FFFFFF", font=("Helvetica", 10, "bold"))
        self.info_bar.pack(side=tk.RIGHT, padx=10)

    def populate(self):
        self.reset_canvas()
        self.node_collection.clear()
        for i in range(city_count):
            self.create_node(i)
        self.display_nodes()

    def create_node(self, id):
        x = random.randint(margin, self.winfo_width() - margin)
        y = random.randint(margin, self.winfo_height() - margin)
        node = Node(x, y, id)
        self.node_collection.append(node)

    def display_nodes(self):
        for node in self.node_collection:
            node.render(self.canvas)

    def reset_canvas(self):
        self.canvas.delete("all")

    def initiate_optimizer(self):
        if not self.node_collection:
            self.populate()
        self.optimizer = RouteOptimizer(self.node_collection)
        self.active = True
        self.run_optimization()

    def run_optimization(self):
        if self.active and self.optimizer.heat > 1:
            self.optimizer.optimize()
            self.reset_canvas()
            self.visualize_route(self.optimizer.current_route)
            self.canvas.update()
            self.after(10, self.run_optimization)
        else:
            self.active = False
            self.show_optimal_length()

    def show_optimal_length(self):
        self.info_bar.config(text=f"Optimal Route Length: {int(self.optimizer.shortest_distance)}")
        self.reset_canvas()
        self.visualize_route(self.optimizer.optimal_route, final=True)

    def clear(self):
        self.reset_canvas()
        self.node_collection.clear()
        self.info_bar.config(text="Optimal Route Length: ")
        self.active = False

    def visualize_route(self, route, final=False):
        color = 'green' if final else 'red'
        for i in range(len(route)):
            node_a = self.node_collection[route[i]]
            node_b = self.node_collection[ route[(i + 1) % len(route)]]
            edge = Edge(node_a, node_b)
            edge.render(self.canvas, hue=color, dotted=True)
        for node in self.node_collection:
            node.render(self.canvas, hue='white')

if __name__ == '__main__':
    gui = TravelingSalesmanGUI()
    gui.mainloop()
