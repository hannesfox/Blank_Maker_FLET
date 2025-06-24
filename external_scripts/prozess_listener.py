import pyautogui
import keyboard
import time
from threading import Thread
import os
from pathlib import Path  # Wir nutzen pathlib für saubere Pfad-Manipulation

# --- ABSOLUTEN PFAD ZU DEN BILDERN ERMITTELN (NEUE, VERBESSERTE VERSION) ---
# Dies löst das Problem, dass die Bilder in einem anderen Ordner liegen.

# 1. Finde den Ordner, in dem das Skript liegt (z.B. ...\external_scripts)
SCRIPT_DIR = Path(__file__).resolve().parent

# 2. Gehe eine Ebene höher zum Projekt-Root (z.B. ...\Blank_Maker_FLET)
PROJECT_ROOT = SCRIPT_DIR.parent

# 3. Gehe von dort in den "Bilder"-Ordner
IMAGES_FOLDER = PROJECT_ROOT / "Bilder"


def get_image_path(image_name):
    """Baut einen vollständigen, absoluten Pfad zu einer Bilddatei im "Bilder"-Ordner."""
    path = IMAGES_FOLDER / image_name
    if not path.exists():
        # Fallback für unterschiedliche Dateiendungen (z.B. .png vs .PNG)
        if path.with_suffix('.PNG').exists():
            return str(path.with_suffix('.PNG'))
        # Wenn immer noch nicht gefunden, werfen wir einen klaren Fehler
        raise FileNotFoundError(f"Bilddatei nicht gefunden: {path}")
    return str(path)


# --- Dein restlicher Code, unverändert, da die Logik oben alles regelt ---

def process_images_robust():
    """
    Diese Funktion sucht und klickt die Bilder mit besserem Timing und Fehler-Feedback.
    """
    try:
        # Pfade zu den Bildern holen
        image1_path = get_image_path('image1.png')
        image2_path = get_image_path('image2.png')  # get_image_path kümmert sich um .png/.PNG

        # --- SCHRITT 1: Suche nach dem ersten Bild ---
        print(f"Suche nach Bild: {image1_path}")
        image1_pos = pyautogui.locateOnScreen(image1_path, confidence=0.7, grayscale=True)

        if image1_pos is None:
            print("FEHLER: image1.png wurde auf dem Bildschirm nicht gefunden.")
            return

        print("image1.png gefunden. Klicke darauf.")
        x, y = pyautogui.center(image1_pos)
        pyautogui.click(x, y)
        time.sleep(1.0)

        # --- SCHRITT 2: Suche nach dem zweiten Bild ---
        print(f"Suche nach Bild: {image2_path}")
        image2_pos = pyautogui.locateOnScreen(image2_path, confidence=0.7, grayscale=True)

        if image2_pos is None:
            print("FEHLER: image2.png wurde nach dem Klick auf image1 nicht gefunden.")
            # Speichere den Screenshot im Skript-Ordner, das ist am einfachsten zu finden
            debug_screenshot_path = SCRIPT_DIR / "debug_screen_failing_at_image2.png"
            pyautogui.screenshot(str(debug_screenshot_path))
            print(f"Habe einen Screenshot ('{debug_screenshot_path}') gespeichert, um das Problem zu analysieren.")
            return

        print("image2.png gefunden. Klicke darauf.")
        x, y = pyautogui.center(image2_pos)
        pyautogui.click(x, y)
        time.sleep(0.5)

        print("Bild-Prozess erfolgreich abgeschlossen.")

    except FileNotFoundError as e:
        print(f"DATEI-FEHLER: {e}. Überprüfe den Pfad und den Dateinamen.")

    except pyautogui.ImageNotFoundException:
        print("FEHLER (ImageNotFoundException): Ein Bild wurde auf dem Bildschirm nicht gefunden.")

    except Exception as e:
        print(f"Ein unerwarteter Fehler ist in process_images_robust aufgetreten: {e}")


def on_f12_pressed(event):
    if event.name != 'f12':
        return

    print("\n--- F12 gedrückt, starte Aktion ---")
    pyautogui.rightClick()
    time.sleep(0.2)

    img_thread = Thread(target=process_images_robust)
    img_thread.start()

    time.sleep(2)  # Diese Zeit muss evtl. angepasst werden, je nachdem wie lange process_images braucht

    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')
    print("--- F12-Aktion (Paste & Enter) abgeschlossen ---")


# --- Hauptprogramm ---
print("Hotkey-Listener gestartet. Drücke F12, um die Aktion auszulösen.")
print(f"Skript läuft aus Verzeichnis: {SCRIPT_DIR}")
print(f"Sucht Bilder im Verzeichnis: {IMAGES_FOLDER}")
print("Beende das Skript mit Strg+C im Terminal oder durch Schließen des Fensters.")

keyboard.on_press_key('f12', on_f12_pressed)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nSkript wird beendet.")
finally:
    keyboard.unhook_all()