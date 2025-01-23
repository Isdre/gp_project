import os
import matplotlib.pyplot as plt

# Ścieżki do plików
base_path = "results/problem4"
files = {
    "average_fitness": os.path.join(base_path, "average_fitness.txt"),
    "best_fitness": os.path.join(base_path, "best_fitness.txt"),
    "average_size": os.path.join(base_path, "average_size.txt"),
}

def load_data(file_path):
    with open(file_path, "r") as file:
        return [float(line.strip()) for line in file.readlines()]

# Wczytywanie danych z plików
data = {name: load_data(path) for name, path in files.items()}

for name, values in data.items():
    plt.figure()
    plt.plot(values, label=name.replace("_", " ").capitalize())
    plt.title(f"{name.replace('_', ' ').capitalize()} Over Generations")
    plt.xlabel("Generation")
    plt.ylabel(name.replace("_", " ").capitalize())
    plt.legend()
    plt.grid()
    output_path = os.path.join(base_path, f"{name}.png")
    plt.savefig(output_path)
    plt.close()

base_path  # Return the path to verify correct output directory
