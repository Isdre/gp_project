import os
import matplotlib.pyplot as plt

# File paths (assuming files are in the current directory)
files = {
    "average_fitness": "average_fitness.txt",
    "best_fitness": "best_fitness.txt",
    "average_size": "average_size.txt",
}

def load_data(file_path):
    if not os.path.exists(file_path):
        # print(f"Warning: File {file_path} not found.")
        return []
    with open(file_path, "r") as file:
        return [float(line.strip()) for line in file.readlines() if line.strip()]

def update_plot():
    # Load data
    data = {name: load_data(path) for name, path in files.items()}
    
    # Check if we have data
    if not any(data.values()):
        # print("No data found to plot.")
        return

    # Create figure and axis
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot Fitness on left Y-axis
    color = 'tab:green'
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('Fitness', color=color)
    
    if data["best_fitness"]:
        ax1.plot(data["best_fitness"], label='Best Fitness', color='green', linewidth=2)
    if data["average_fitness"]:
        ax1.plot(data["average_fitness"], label='Average Fitness', color='blue', linewidth=1.5, alpha=0.7)
        
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, which='both', linestyle='--', alpha=0.5)

    # Create second Y-axis for Size
    ax2 = ax1.twinx()  
    color = 'tab:red'
    ax2.set_ylabel('Average Size', color=color)
    
    if data["average_size"]:
        ax2.plot(data["average_size"], label='Average Size', color=color, linestyle='--', linewidth=1.5)
        
    ax2.tick_params(axis='y', labelcolor=color)

    # Title and Layout
    plt.title('Evolution Progress: Fitness & Size')
    fig.tight_layout()  
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    # Save plot
    output_path = "simulation_results.png"
    try:
        plt.savefig(output_path, dpi=100)
        # print(f"Plot saved to {output_path}")
    except Exception as e:
        print(f"Error saving plot: {e}")
    finally:
        plt.close(fig)

if __name__ == "__main__":
    update_plot()
