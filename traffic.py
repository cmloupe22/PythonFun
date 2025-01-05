import time
import random
from collections import deque

class TrafficLight:
    def __init__(self, green_time, red_time, initial_state="red"):
        self.green_time = green_time
        self.red_time = red_time
        self.state = initial_state
        self.time_left = green_time if initial_state == "green" else red_time

    def update(self):
        self.time_left -= 1
        if self.time_left <= 0:
            if self.state == "green":
                self.state = "red"
                self.time_left = self.red_time + random.randint(-1, 1)
            else:
                self.state = "green"
                self.time_left = self.green_time + random.randint(-1, 1)

    def get_color(self):
        return "\033[32mGREEN\033[0m" if self.state == "green" else "\033[31mRED\033[0m"

class Intersection:
    def __init__(self, name, green_time, red_time):
        self.name = name
        self.light = TrafficLight(green_time, red_time)
        self.queue = deque()

    def add_car(self, car):
        self.queue.append(car)

    def update(self):
        self.light.update()
        if self.light.state == "green":
            # Clear out cars faster during green light
            for _ in range(min(2, len(self.queue))):  # Allow up to 2 cars to leave per step
                self.queue.popleft()

    def __str__(self):
        queue_representation = ''.join(self.queue) if self.queue else 'Empty'
        return f"{self.name}: Light: {self.light.get_color()} ({self.light.time_left}s) | Queue: {queue_representation}"

class TrafficSimulator:
    def __init__(self):
        self.intersections = [
            Intersection(name="Brazos & 5th St", green_time=5, red_time=7),
            Intersection(name="Brazos & 6th St", green_time=7, red_time=5),
            Intersection(name="Brazos & 7th St", green_time=6, red_time=6),
        ]

    def add_random_cars(self):
        for i, intersection in enumerate(self.intersections):
            if random.random() < 0.4:  # 40% chance
                num_cars = random.randint(1, 3)
                for _ in range(num_cars):
                    car_id = "\U0001F697"
                    intersection.add_car(car_id)

    def step(self):
        self.add_random_cars()
        update_order = list(range(len(self.intersections)))
        random.shuffle(update_order)
        for i in update_order:
            self.intersections[i].update()

    def display(self):
        print("\n" + "-" * 40)
        for intersection in self.intersections:
            print(f"{intersection}")

    def run(self, steps=20):
        for _ in range(steps):
            self.step()
            self.display()
            time.sleep(1)

if __name__ == "__main__":
    simulator = TrafficSimulator()
    simulator.run()
