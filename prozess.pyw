import pyautogui
import keyboard
import time
import signal
import sys
from threading import Thread, Event

# Global flag für sauberen Exit
running = Event()
running.set()


def process_images():
    try:
        image_pos = pyautogui.locateOnScreen('Bilder/image1.png', confidence=0.7, grayscale=True)
        x, y = pyautogui.center(image_pos)
        time.sleep(0.05)
        pyautogui.click(x, y)
        time.sleep(0.05)
        image_pos = pyautogui.locateOnScreen('Bilder/image2.png', confidence=0.7, grayscale=True)
        x, y = pyautogui.center(image_pos)
        time.sleep(0.05)
        pyautogui.click(x, y)
        time.sleep(0.05)
    except pyautogui.ImageNotFoundException:
        pass


def on_f12_pressed(event):
    if not running.is_set():
        return

    pyautogui.rightClick()
    time.sleep(0.05)
    Thread(target=process_images).start()
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')


def signal_handler(signum, frame):
    """Behandelt Terminierungssignale"""
    print(f"Signal {signum} empfangen. Beende Prozess...")
    cleanup_and_exit()


def cleanup_and_exit():
    """Sauberer Exit"""
    running.clear()  # Stop flag setzen
    try:
        keyboard.unhook_all()  # Alle Keyboard-Hooks entfernen
    except:
        pass
    print("Prozess beendet.")
    sys.exit(0)


# Signal Handler registrieren
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)  # Für Ctrl+C

# Keyboard Hook registrieren
keyboard.on_press_key('F12', on_f12_pressed)

print("Prozess gestartet. Drücke F12 für Aktion.")

try:
    # Hauptschleife mit Exit-Bedingung
    while running.is_set():
        time.sleep(0.1)  # Etwas längere Pause für bessere Performance
except KeyboardInterrupt:
    cleanup_and_exit()
except Exception as e:
    print(f"Fehler: {e}")
    cleanup_and_exit()