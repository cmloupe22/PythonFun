import pygame
import random
import math
import time

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 480, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ant Colony Simulator")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)

FOOD_COUNT = 40
COLONY_RADIUS = 40
FOOD_RADIUS = 5
SPEED = 3
FPS = 30
GROWTH_AMOUNT = 4  # Amount by which the colony grows when food is returned

class Ant:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.has_food = False
        self.target = None

    def move(self):
        if self.target:
            # Move towards the target
            dx, dy = self.target[0] - self.x, self.target[1] - self.y
            dist = math.hypot(dx, dy)
            if dist > 1:
                self.x += SPEED * dx / dist
                self.y += SPEED * dy / dist
        else:
            self.x += random.uniform(-1, 1) * SPEED
            self.y += random.uniform(-1, 1) * SPEED

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)

class Colony:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.ants = [Ant(x, y, color)]  # Starting with one ant
        self.radius = COLONY_RADIUS  # Initial radius of the colony

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 2)

    def update(self, food_sources, enemy_colony):
        for ant in self.ants:
            if not ant.has_food:
                if food_sources:
                    closest_food = min(food_sources, key=lambda f: math.hypot(ant.x - f[0], ant.y - f[1]))
                    ant.target = closest_food
                    if math.hypot(ant.x - closest_food[0], ant.y - closest_food[1]) < FOOD_RADIUS:
                        food_sources.remove(closest_food)
                        ant.has_food = True
            else:
                ant.target = (self.x, self.y)
                if math.hypot(ant.x - self.x, ant.y - self.y) < self.radius:
                    ant.has_food = False
                    self.radius += GROWTH_AMOUNT  # Increase colony when food is delivered
                    self.ants.append(Ant(self.x, self.y, self.color))  # plus one ant when food is delivered

            ant.move()
            ant.draw()

            # Combat mode?
            for enemy_ant in enemy_colony.ants:
                if math.hypot(ant.x - enemy_ant.x, ant.y - enemy_ant.y) < 5:
                    if random.random() < 0.5:
                        enemy_colony.ants.remove(enemy_ant)

food_sources = [(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)) for _ in range(FOOD_COUNT)]

colony1 = Colony(100, 150, RED)
colony2 = Colony(380, 650, BLUE)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)

    # Drawing food sources
    for food in food_sources:
        pygame.draw.circle(screen, GREEN, food, FOOD_RADIUS)

    # Check if food is all consumed
    if not food_sources:
        font = pygame.font.SysFont(None, 55)
        text = font.render("Game Over: All Food Consumed!", True, (0, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(3000)  # Display message for 3 seconds
        running = False
        break

    # Updating colonies
    colony1.update(food_sources, colony2)
    colony2.update(food_sources, colony1)

    colony1.draw()
    colony2.draw()

    pygame.display.flip()
    clock.tick(FPS) #use fps for consistent rate

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
