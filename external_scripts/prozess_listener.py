# Wichtig: Dieses Skript benötigt 'pyautogui' und 'keyboard' installiert.
# Es läuft als separater Prozess.
# Der Pfad zu den Bildern muss relativ zu diesem Skript korrekt sein,
# oder es müssen absolute Pfade verwendet werden.
# Annahme: Der "Bilder" Ordner ist im selben Verzeichnis wie das Hauptprojekt,
# von dem aus dieses Skript als Subprozess gestartet wird, oder der Pfad
# wird angepasst.

import pyautogui
import keyboard  # Beachte: keyboard benötigt root/Admin-Rechte unter Linux/macOS für globale Hotkeys
import time
from threading import Thread
import os
from pathlib import Path

# Versuche, den Bilder-Ordner relativ zum Hauptprojekt zu finden.
# Dies ist eine Heuristik und funktioniert, wenn das Skript aus einem Unterordner
# des Projekts gestartet wird, wo auch der "Bilder" Ordner liegt.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT_GUESS = SCRIPT_DIR.parent  # Annahme: external_scripts ist ein Unterordner von Projekt Root
IMAGES_FOLDER = PROJECT_ROOT_GUESS / "Bilder"

print(f"Prozess Listener: Vermuteter Projekt-Root: {PROJECT_ROOT_GUESS}")
print(f"Prozess Listener: Suche Bilder in: {IMAGES_FOLDER}")


def get_image_path_listener(image_name):
    path = IMAGES_FOLDER / image_name
    if not path.exists():
        # Fallback: Suche im aktuellen Verzeichnis des Skripts (falls Bilder dort wären)
        fallback_path = SCRIPT_DIR / image_name
        if fallback_path.exists():
            print(f"Prozess Listener: Bild {image_name} im Skriptverzeichnis gefunden: {fallback_path}")
            return str(fallback_path)
        print(f"Prozess Listener: Bild {image_name} nicht gefunden in {IMAGES_FOLDER} oder {SCRIPT_DIR}")
        raise pyautogui.ImageNotFoundException(f"Bild {image_name} nicht gefunden.")
    return str(path)


def process_images_for_f12():
    try:
        # Pfade zu den Bildern anpassen, falls nötig!
        image1_path = get_image_path_listener('image1.png')  # Beispielbildname
        image2_path = get_image_path_listener('image2.png')  # Beispielbildname

        print(f"Prozess Listener: Suche image1.png ({image1_path})")
        image_pos = pyautogui.locateOnScreen(image1_path, confidence=0.7, grayscale=True)
        if image_pos is None:
            print("Prozess Listener: image1.png nicht gefunden.")
            return  # Frühzeitiger Ausstieg, wenn das erste Bild nicht da ist

        x, y = pyautogui.center(image_pos)
        time.sleep(0.05)
        pyautogui.click(x, y)
        print("Prozess Listener: Klick auf image1.png")
        time.sleep(0.05)

        print(f"Prozess Listener: Suche image2.png ({image2_path})")
        image_pos = pyautogui.locateOnScreen(image2_path, confidence=0.7, grayscale=True)
        if image_pos is None:
            print("Prozess Listener: image2.png nicht gefunden.")
            return

        x, y = pyautogui.center(image_pos)
        time.sleep(0.05)
        pyautogui.click(x, y)
        print("Prozess Listener: Klick auf image2.png")
        time.sleep(0.05)
    except pyautogui.ImageNotFoundException:
        print("Prozess Listener: Ein oder mehrere Bilder für F12-Aktion nicht gefunden.")
    except Exception as e:
        print(f"Prozess Listener: Fehler in process_images_for_f12: {e}")


def on_f12_pressed_event(event):  # event wird von keyboard übergeben
    if event.name == 'f12':  # Sicherstellen, dass es wirklich F12 ist
        print("Prozess Listener: F12 gedrückt.")
        pyautogui.rightClick()
        time.sleep(0.05)
        # Starte die Bildverarbeitung in einem neuen Thread, um den Listener nicht zu blockieren
        img_thread = Thread(target=process_images_for_f12, daemon=True)
        img_thread.start()
        time.sleep(0.2)  # Etwas mehr Zeit geben, bevor STRG+V kommt
        # Original hatte 2s, das ist sehr lang. Teste mit kürzerer Zeit.
        # Diese Zeit muss ggf. an die Geschwindigkeit der process_images angepasst werden.
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        pyautogui.press('enter')
        print("Prozess Listener: F12-Aktion abgeschlossen.")


if __name__ == '__main__':
    print("Prozess Listener (F12 Hotkey) gestartet. Drücke F12, um Aktionen auszulösen.")
    print("Beende diesen Prozess durch Schließen des Fensters oder über Task-Manager.")

    # Registriere den Hotkey
    # 'suppress=True' würde verhindern, dass F12 an andere Anwendungen weitergegeben wird.
    # Ist hier meist nicht gewünscht.
    keyboard.on_press_key('f12', on_f12_pressed_event)

    # Halte das Skript am Laufen, um auf Hotkeys zu lauschen
    try:
        while True:
            time.sleep(1)  # Reduziert CPU-Last
    except KeyboardInterrupt:
        print("Prozess Listener durch Benutzer beendet.")
    finally:
        keyboard.unhook_all()  # Wichtig, um Hotkeys freizugeben
        print("Prozess Listener beendet und Hotkeys freigegeben.")