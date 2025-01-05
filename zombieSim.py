import numpy as np
import matplotlib.pyplot as plt
import time

grid_size = 20  # Map size
human_count = 18  #  Num of humans
zombie_count = 7  # Num of zombies
empty = 0  # Empty space
human = 1  # Human
zombie = 2  # Zombie

def initialize_grid(grid_size, human_count, zombie_count):
    grid = np.zeros((grid_size, grid_size), dtype=int)

    # Placing humans randomly
    for _ in range(human_count):
        while True:
            x, y = np.random.randint(0, grid_size, size=2)
            if grid[x, y] == empty:
                grid[x, y] = human
                break

    for _ in range(zombie_count):
        while True:
            x, y = np.random.randint(0, grid_size, size=2)
            if grid[x, y] == empty:
                grid[x, y] = zombie
                break

    return grid

def display_grid_matplotlib(grid, step):
    color_map = {
        empty: 0,  # White
        human: 1,  # Blue
        zombie: 2  # Red
    }
    grid_mapped = np.vectorize(color_map.get)(grid)  # assign grid vals to numeric

    plt.imshow(grid_mapped, cmap="coolwarm", interpolation="nearest")
    plt.title(f"Zombie Simulation - Step {step}")
    plt.axis("off")
    plt.colorbar(ticks=[0, 1, 2], label="Entity Type")
    plt.pause(0.5)
    plt.clf()

def move_entities(grid):
    new_grid = np.zeros_like(grid)
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            if grid[x, y] == empty:
                continue

            # Find a random new position
            dx, dy = np.random.choice([-1, 0, 1]), np.random.choice([-1, 0, 1])
            new_x, new_y = (x + dx) % grid.shape[0], (y + dy) % grid.shape[1]

            if new_grid[new_x, new_y] == empty:
                new_grid[new_x, new_y] = grid[x, y]
            else:
                new_grid[x, y] = grid[x, y]

    return new_grid

# Infecting the humans near zombies
def infect(grid):
    new_grid = grid.copy()
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            if grid[x, y] == zombie:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = (x + dx) % grid.shape[0], (y + dy) % grid.shape[1]
                        if grid[nx, ny] == human:
                            new_grid[nx, ny] = zombie  # Human becomes a zombie 
    return new_grid

def simulate(grid, steps):
    for step in range(steps):
        print(f"Step {step + 1}")
        grid = move_entities(grid)
        grid = infect(grid)
        display_grid_matplotlib(grid, step + 1)
        time.sleep(0.5)

grid = initialize_grid(grid_size, human_count, zombie_count)
simulate(grid, 20)

plt.show()
