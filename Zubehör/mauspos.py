import pyautogui
import keyboard

def get_mouse_position():
    x, y = pyautogui.position()
    print(f"Mausposition: X={x}, Y={y}")

print("Drücke die Leertaste, um die aktuelle Mausposition zu erfahren.")

keyboard.on_press_key(" ", lambda _: get_mouse_position())

keyboard.wait("esc")  # Wartet auf die "ESC"-Taste, um das Programm zu beenden.
