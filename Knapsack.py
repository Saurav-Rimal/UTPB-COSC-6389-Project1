import math
import random
import tkinter as tk
from tkinter import *
import threading
import time

num_items = 100
frac_target = 0.7
min_value = 128
max_value = 2048

screen_padding = 10
item_padding = 20
stroke_width = 1

num_generations = 999
pop_size = 50
elitism_count = 2
mutation_rate = 0.1

sleep_time = 0.1

predefined_colors = ['#789DBC', '#FFE3E3', '#FEF9F2', '#C9E9D2', '#DA8359', '#FF8A8A', '#BED754', '#D4ADFC','#FB2576','#F79646','#F7D674','#B4E1A1','#81E8D8','#42F4F4','#4D5360','#263238']

def random_predefined_color():
    return random.choice(predefined_colors)

class Item:
    def __init__(self):
        self.value = random.randint(min_value, max_value)
        self.color = random_predefined_color()
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    def place(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self, canvas, active=False):
        canvas.create_text(self.x + self.w + item_padding + stroke_width * 2, self.y + self.h / 2, text=f'{self.value}', fill="white")
        canvas.create_rectangle(self.x + stroke_width / 2,
                                self.y + stroke_width / 2,
                                self.x + self.w - stroke_width / 2,
                                self.y + self.h - stroke_width / 2,
                                fill=self.color if active else '',
                                outline=self.color,
                                width=stroke_width)

class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Knapsack")
        self.configure(bg='#1A1A1D')  # Set background to dark
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.width, self.height))
        self.state("zoomed")

        self.canvas = Canvas(self, bg='#1A1A1D', highlightthickness=0)
        self.canvas.place(x=0, y=50, width=self.width, height=self.height - 50)

        self.items_list = []
        self.target = 0
        self.generation = 0
        self.running = False
        self.start_time = 0

        # Add buttons and labels to the top bar
        top_bar = Frame(self, bg='#333333', relief=RAISED, bd=2)
        top_bar.place(x=0, y=0, width=self.width, height=50)

        button_style = {
            "bg": "#FEF9F2",
            "fg": "Black",
            "font": ("Arial", 12, "bold"),
            "relief": RAISED,
            "bd": 2,
            "activebackground": "#555555",
            "activeforeground": "red"
        }

        generate_button = Button(top_bar, text="Generate Blocks", command=self.generate_and_draw, **button_style)
        generate_button.pack(side=LEFT, padx=10, pady=5)

        target_button = Button(top_bar, text="Get Target", command=self.set_target, **button_style)
        target_button.pack(side=LEFT, padx=10, pady=5)

        run_button = Button(top_bar, text="Run Solver", command=self.start_thread, **button_style)
        run_button.pack(side=LEFT, padx=10, pady=5)

        clear_button = Button(top_bar, text="Clear", command=self.clear, **button_style)
        clear_button.pack(side=LEFT, padx=10, pady=5)

        self.info_label = Label(top_bar, text="Target: 0, Generation: 0", bg="#333333", fg="white", font=("Arial", 12, "bold"))
        self.info_label.pack(side=RIGHT, padx=20)

        self.mainloop()

    def update_info_label(self):
        self.info_label.config(text=f"Target: {self.target}, Generation: {self.generation}")

    def generate_and_draw(self):
        self.generate_knapsack()
        self.draw_items()

    def set_target(self):
        target_set = random.sample(self.items_list, int(num_items * frac_target))
        self.target = sum(item.value for item in target_set)
        self.update_info_label()
        self.draw_target()

    def start_thread(self):
        self.running = True
        self.start_time = time.time()
        thread = threading.Thread(target=self.run, args=())
        thread.start()

    def clear(self):
        self.running = False
        self.generation = 0
        self.update_info_label()
        self.clear_canvas()

    def get_rand_item(self):
        i1 = Item()
        for i2 in self.items_list:
            if i1.value == i2.value:
                return None
        return i1

    def add_item(self):
        item = self.get_rand_item()
        while item is None:
            item = self.get_rand_item()
        self.items_list.append(item)

    def generate_knapsack(self):
        self.items_list = []
        for _ in range(num_items):
            self.add_item()

        item_max = max(item.value for item in self.items_list)
        w = self.width - screen_padding
        h = self.height - screen_padding - 50
        num_rows = math.ceil(num_items / 6)
        row_w = w / 8 - item_padding
        row_h = (h - 200) / num_rows

        for x in range(0, 6):
            for y in range(0, num_rows):
                if x * num_rows + y >= num_items:
                    break
                item = self.items_list[x * num_rows + y]
                item_w = row_w / 2
                item_h = max(item.value / item_max * row_h, 1)
                item.place(screen_padding + x * row_w + x * item_padding,
                           screen_padding + y * row_h + y * item_padding,
                           item_w,
                           item_h)

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_items(self):
        for item in self.items_list:
            item.draw(self.canvas)

    def draw_target(self):
        x = (self.width - screen_padding) / 8 * 7
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 2 - screen_padding
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='black')
        self.canvas.create_text(x + w // 2, y + h + screen_padding, text=f'{self.target}', font=('Arial', 18), fill="white")

    def draw_sum(self, item_sum, target):
        x = (self.width - screen_padding) / 8 * 6
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 2 - screen_padding
        h *= (item_sum / target)
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='black')
        self.canvas.create_text(x + w // 2, y + h + screen_padding,
                                text=f'{item_sum} ({"+" if item_sum > target else "-"}{abs(item_sum - target)})',
                                font=('Arial', 18), fill="white")

    def draw_genome(self, genome, gen_num):
        self.generation = gen_num
        self.update_info_label()
        for i in range(num_items):
            item = self.items_list[i]
            active = genome[i]
            item.draw(self.canvas, active)

    def run(self):
        def gene_sum(genome):
            total = sum(self.items_list[i].value for i in range(len(genome)) if genome[i])
            return total

        def fitness(genome):
            return abs(gene_sum(genome) - self.target)

        def get_population(last_pop=None):
            population = []
            if last_pop is None:
                for _ in range(pop_size):
                    genome = [random.random() < frac_target for _ in range(num_items)]
                    population.append(genome)
                return population
            else:
                elites = [last_pop[i] for i in range(elitism_count)]
                population.extend(elites)
                while len(population) < pop_size:
                    parents = random.sample(last_pop, 2)
                    crossover_point = random.randint(0, num_items - 1)
                    child = parents[0][:crossover_point] + parents[1][crossover_point:]
                    if random.random() < mutation_rate:
                        mutate_index = random.randint(0, num_items - 1)
                        child[mutate_index] = not child[mutate_index]
                    population.append(child)
                return population

        def generation_step(generation=0, pop=None):
            if not self.running or generation >= num_generations:
                return

            if pop is None:
                pop = get_population()

            fitnesses = sorted(pop, key=fitness)
            best_genome = fitnesses[0]
            best_fitness = fitness(best_genome)

            self.after(0, self.clear_canvas)
            self.after(0, self.draw_target)
            self.after(0, self.draw_sum, gene_sum(best_genome), self.target)
            self.after(0, self.draw_genome, best_genome, generation)

            if best_fitness == 0:
                elapsed_time = time.time() - self.start_time
                print(f'Target {self.target} met at generation {generation}! Time taken: {elapsed_time:.2f} seconds')
                return

            self.after(int(sleep_time * 1000), generation_step, generation + 1, get_population(pop))

        generation_step()

if __name__ == '__main__':
    UI()