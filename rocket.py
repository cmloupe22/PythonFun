import time
import os

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def rocket_launch():
    rocket = [
        "        ^        ",
        "       / \       ",
        "      /___\      ",
        "     |     |     ",
        "     |     |     ",
        "    /|_____|\    ",
        "   /_________\   ",
        "        |        ",
        "        |        ",
    ]

    countdown = 5

    # Countdown
    while countdown >= 0:
        clear_console()
        print(f"T-minus {countdown} seconds")
        time.sleep(1)
        countdown -= 1

    clear_console()
    print("Liftoff!")
    time.sleep(1)

    #Animation
    for i in range(15):
        clear_console()
        print("\n" * (15 - i))
        for line in rocket:
            print(line)
        time.sleep(0.1)

    clear_console()
    print("🚀 The rocket is in space! 🚀")

if __name__ == "__main__":
    rocket_launch()
