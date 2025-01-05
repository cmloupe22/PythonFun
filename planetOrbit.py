import matplotlib.pyplot as plt
import numpy as np


num_planets = 3
simulation_steps = 1500
center_position = np.array([0, 0])  # Sun will be in the middle
orbit_radii = [20, 30, 40]  # Orbit size/arc for the planets
orbit_speeds = [0.02, 0.015, 0.01]
colors = ['blue', 'green', 'red']

planets = []
for i in range(num_planets):
    angle = np.random.uniform(0, 2 * np.pi)  # Randomize how it starts
    planet = {
        'radius': orbit_radii[i],
        'angle': angle,
        'speed': orbit_speeds[i],
        'color': colors[i]
    }
    planets.append(planet)

def update_positions(planets):
    for planet in planets:
        planet['angle'] += planet['speed']  # Update angles based on speed

# Visualization
plt.ion()
fig, ax = plt.subplots()
ax.set_xlim(-50, 50)
ax.set_ylim(-50, 50)
ax.set_aspect('equal')

for step in range(simulation_steps):
    ax.clear()
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.set_title("Planets Orbiting the Sun")

    # Plot the sun
    ax.scatter(center_position[0], center_position[1], color='yellow', s=200, label="Sun")

    # Update and plot planets
    update_positions(planets)
    for planet in planets:
        x = center_position[0] + planet['radius'] * np.cos(planet['angle'])
        y = center_position[1] + planet['radius'] * np.sin(planet['angle'])
        ax.scatter(x, y, color=planet['color'])

    plt.pause(0.05)

plt.ioff()
plt.show()
