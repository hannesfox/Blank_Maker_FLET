# actions.py

import pyautogui
import pyscreeze
import time
import os


SPEED_FACTOR = 0.4
# ---------------------------------------------


def action_1():
    """Klickt auf das erste Bild."""
    image_position = pyscreeze.locateOnScreen('Bilder/1.png', confidence=0.5)
    if not image_position:
        raise FileNotFoundError("Bild 'Bilder/1.png' konnte nicht auf dem Bildschirm gefunden werden.")

    pyautogui.click(pyscreeze.center(image_position))
    time.sleep(0.5 * SPEED_FACTOR)  # <--- GEÄNDERT


def action_2():
    """Klickt auf das zweite Bild."""
    image_position = pyscreeze.locateOnScreen('Bilder/2.png', confidence=0.4)
    if not image_position:
        raise FileNotFoundError("Bild 'Bilder/2.png' konnte nicht auf dem Bildschirm gefunden werden.")

    pyautogui.click(pyscreeze.center(image_position))
    time.sleep(0.9 * SPEED_FACTOR)  # <--- GEÄNDERT


def action_3(program_name: str):
    """Füllt das erste Textfeld mit dem Programmnamen + '_A'."""
    image_position = pyscreeze.locateOnScreen('Bilder/3.png', confidence=0.5, grayscale=True)
    if not image_position:
        raise FileNotFoundError("Bild 'Bilder/3.png' konnte nicht auf dem Bildschirm gefunden werden.")

    pyautogui.doubleClick(pyscreeze.center(image_position))
    time.sleep(0.2 * SPEED_FACTOR)  #
    pyautogui.press('delete')
    time.sleep(0.1 * SPEED_FACTOR)  #
    text = program_name + '_A'
    pyautogui.typewrite(text)
    time.sleep(0.1 * SPEED_FACTOR)  #


def action_4(program_name: str):
    """Füllt das zweite Textfeld mit dem Programmnamen."""
    pyautogui.press('tab')
    pyautogui.press('tab')
    time.sleep(0.1 * SPEED_FACTOR)  #
    pyautogui.press('delete')
    time.sleep(0.1 * SPEED_FACTOR)  #
    pyautogui.typewrite(program_name)
    time.sleep(0.1 * SPEED_FACTOR)  #


def action_5(machine_type: str):
    """Wählt die Maschinenart aus."""
    pyautogui.press('tab')
    time.sleep(0.1 * SPEED_FACTOR)  #
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('delete')
    time.sleep(0.1 * SPEED_FACTOR)  #
    pyautogui.typewrite(machine_type)
    time.sleep(0.1 * SPEED_FACTOR)  #


def action_6():
    """Bestätigt mit Enter."""
    pyautogui.press('enter')
    time.sleep(0.1 * SPEED_FACTOR)  #


def action_7(destination_folder: str):
    """Lädt Rohteil und Schraubstock in Esprit."""
    # Die Dauer der Mausbewegung wird ebenfalls angepasst
    wegzeit1 = 0.4 * SPEED_FACTOR

    pfad_rohteil = os.path.join(destination_folder, "!rohteil.dxf")
    pfad_schraubstock = os.path.join(destination_folder, "!schraubstock.step")

    if not os.path.exists(pfad_rohteil):
        raise FileNotFoundError(f"Rohteil-Datei nicht gefunden: {pfad_rohteil}")
    if not os.path.exists(pfad_schraubstock):
        raise FileNotFoundError(f"Schraubstock-Datei nicht gefunden: {pfad_schraubstock}")

    pyautogui.doubleClick(974, 1047, duration=wegzeit1)
    time.sleep(0.5 * SPEED_FACTOR)
    pyautogui.hotkey('ctrl', 'o')
    time.sleep(0.5 * SPEED_FACTOR)
    pyautogui.typewrite(pfad_rohteil)
    time.sleep(0.5 * SPEED_FACTOR)
    pyautogui.press('enter')
    time.sleep(0.5 * SPEED_FACTOR)

    pyautogui.doubleClick(977, 1142, duration=wegzeit1)
    time.sleep(0.5 * SPEED_FACTOR)
    pyautogui.hotkey('ctrl', 'o')
    time.sleep(0.8 * SPEED_FACTOR)
    pyautogui.typewrite(pfad_schraubstock)
    time.sleep(0.8 * SPEED_FACTOR)
    pyautogui.press('enter')