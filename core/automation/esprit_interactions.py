import pyautogui
import pyscreeze  # Wird von pyautogui intern genutzt, expliziter Import nicht immer nötig
import time
import flet as ft
import threading
import traceback
import os
from pathlib import Path

PYWIN32_AVAILABLE = False
if os.name == 'nt':
    try:
        import win32gui
        import win32con
        PYWIN32_AVAILABLE = True
        print("esprit_interactions: pywin32 erfolgreich importiert.")
    except ImportError:
        print("WARNUNG (esprit_interactions): pywin32 nicht installiert. Fokus kann nicht erzwungen werden.")

# --- Hilfsfunktion zum Anzeigen von Flet-Dialogen aus Threads ---
def _show_flet_dialog_from_thread(page_ref: ft.Page, title: str, content_text: str, is_error: bool = False,
                                  bring_to_front_func=None):
    """Zeigt einen Flet Dialog an. `bring_to_front_func` ist optional."""

    if callable(bring_to_front_func):
        bring_to_front_func()
        time.sleep(0.1)

    def _open_dialog_action():
        current_dialog_instance_ref = None  # Vorabdeklaration für die Closure

        def _close_this_specific_dialog(e=None):
            if current_dialog_instance_ref:  # Nur schließen, wenn eine Instanz existiert
                page_ref.close(current_dialog_instance_ref)

        current_dialog_instance_ref = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(content_text),
            actions=[ft.TextButton("OK", on_click=_close_this_specific_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=_close_this_specific_dialog
        )
        page_ref.open(current_dialog_instance_ref)

    _open_dialog_action()


# --- Logik für Esprit Rohteil Definition (ehemals autoesprit.py) ---
def run_esprit_rohteil_definition_sequence(length, width, height, images_base_path: Path):
    """
    Führt die PyAutoGUI-Sequenz zur Definition des Rohteils in Esprit aus.
    Diese Funktion ist blockierend.
    images_base_path: Pfad zum Ordner, der den 'Bilder' Unterordner enthält (oder direkt zum 'Bilder' Ordner).
    """
    print(f"Starte Esprit Rohteil Definition: L={length}, B={width}, H={height}")
    # Derzeit verwendet autoesprit.py keine Bilder, sondern feste Koordinaten.
    # Falls Bilder benötigt werden, hier `images_base_path` verwenden.

    # Beispielhafte PyAutoGUI-Aktionen aus dem Original autoesprit.py
    # Diese Aktionen sind stark von der Bildschirmauflösung und Esprit-Version abhängig.
    # Es ist ratsam, Bilderkennung zu verwenden, falls möglich.
    # Hier wird angenommen, dass die Koordinaten weiterhin gültig sind.

    # WICHTIG: Die SPEED_FACTOR Logik aus actions.py ist hier nicht direkt übernommen.
    # Pyautogui hat `duration` Parameter für Mausbewegungen, die genutzt werden sollten.
    # `time.sleep` wird für Pausen zwischen Aktionen verwendet.

    wegzeit_maus = 0.3  # Dauer für Mausbewegungen
    verweilzeit_aktion = 0.1  # Kurze Pause nach Klicks

    try:
        pyautogui.doubleClick(983, 1014, duration=wegzeit_maus)  # Doppelklick auf Standard
        time.sleep(verweilzeit_aktion)

        # Klicksequenz für Menüpunkte
        positions_menu = [(951, 1031), (950, 1064), (951, 1079), (951, 1095), (951, 1110),
                          (952, 1127), (950, 1143), (951, 1160), (951, 1176),
                          (1265, 142), (1489, 500), (1640, 597)]
        for x, y in positions_menu:
            pyautogui.click(x, y,
                            duration=wegzeit_maus / len(positions_menu))  # Schnellere Klicks innerhalb der Sequenz
            time.sleep(verweilzeit_aktion / 2)

        # Werte eingeben
        pyautogui.doubleClick(1650, 597, duration=wegzeit_maus)  # Klick ins Längenfeld
        time.sleep(verweilzeit_aktion)

        pyautogui.typewrite(str(length));
        pyautogui.press('tab')
        pyautogui.typewrite(str(width));
        pyautogui.press('tab')
        pyautogui.typewrite(str(height));
        pyautogui.press('tab')
        pyautogui.typewrite(str(-length / 2));
        pyautogui.press('tab')  # X-Offset
        pyautogui.typewrite(str(-width / 2));
        pyautogui.press('tab')  # Y-Offset
        pyautogui.typewrite('-4');
        pyautogui.press('tab')  # Z-Offset (wie im Original)
        time.sleep(verweilzeit_aktion)

        # Weitere Klicksequenz
        positions_finish = [(1854, 878), (1478, 553), (951, 1031), (1593, 602)]
        for x, y in positions_finish:
            pyautogui.click(x, y, duration=wegzeit_maus / len(positions_finish))
            time.sleep(verweilzeit_aktion / 2)

        pyautogui.doubleClick(2200, 812, duration=wegzeit_maus)  # Klick "in Kreis" / Bauteilmitte
        time.sleep(0.5)  # Längere Pause

        # Aufräumaktionen
        pyautogui.click(1850, 883, duration=wegzeit_maus);
        time.sleep(verweilzeit_aktion)
        pyautogui.moveTo(1761, 925, duration=wegzeit_maus);
        pyautogui.click();
        time.sleep(verweilzeit_aktion)

        pyautogui.click(951, 1031, duration=wegzeit_maus)  # Solid ausblenden
        pyautogui.click(949, 1048, duration=wegzeit_maus)  # Roh ausblenden
        pyautogui.doubleClick(982, 1143, duration=wegzeit_maus)  # Müll Layer doppelklick
        time.sleep(verweilzeit_aktion)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.click(1394, 110, duration=wegzeit_maus)  # Simulationsbauteil erstellen
        pyautogui.click(1604, 853, duration=wegzeit_maus)  # Übernehmen
        time.sleep(0.5)

        pyautogui.doubleClick(981, 1142, duration=wegzeit_maus)  # Müll Layer
        time.sleep(0.5)
        pyautogui.click(1151, 1102, duration=wegzeit_maus)  # Layer Löschen
        time.sleep(0.5)
        pyautogui.press('left');
        time.sleep(0.2);
        pyautogui.press('enter')  # Bestätigen
        time.sleep(0.5)

        pyautogui.click(1020, 173, duration=wegzeit_maus)  # Freiklicken
        pyautogui.click(950, 1176, duration=wegzeit_maus)  # Spannelemente ausblenden
        pyautogui.click(950, 1031, duration=wegzeit_maus)  # Solid einblenden
        pyautogui.doubleClick(986, 1127, duration=wegzeit_maus)  # Schatten klicken
        pyautogui.click(1756, 109, duration=wegzeit_maus)  # Profilkurve erzeugen
        time.sleep(0.5)

        pyautogui.doubleClick(2205, 814, duration=wegzeit_maus)  # Mittig auf Bauteil
        time.sleep(0.5)
        pyautogui.click(1010, 329, duration=wegzeit_maus)  # OK Klicken
        pyautogui.click(1075, 140, duration=wegzeit_maus)  # Simulation starten (optional?)

        print("Esprit Rohteil Definition abgeschlossen.")

    except pyautogui.FailSafeException:
        print("FailSafe ausgelöst während Esprit Rohteil Definition.")
        raise  # Weitergeben, damit der Aufrufer es handhaben kann
    except Exception as e:
        print(f"Fehler während Esprit Rohteil Definition: {e}")
        traceback.print_exc()
        raise


# --- Logik für B-Seite Automatisierung (ehemals bseite.py) ---
VERWEILZEIT_BSEITE = 0.3  # Angepasste Verweilzeit
PYAUTOGUI_DURATION = 0.2  # Standard Dauer für Mausbewegungen


def _get_bseite_image_path(image_name_with_ext: str, images_folder: Path) -> str:
    """Holt den Pfad zu einem Bild im untergeordneten 'Bilder'-Ordner."""
    path = images_folder / image_name_with_ext  # Annahme: images_folder ist der "Bilder" Ordner selbst
    if not path.exists():
        raise FileNotFoundError(f"Bilddatei für B-Seite nicht gefunden: {path}")
    return str(path)


def _find_image_and_click_bseite(image_name: str, images_folder: Path, conf=0.8, action_desc="Bild", retries=3,
                                 delay_between_retries=0.5):
    img_path = _get_bseite_image_path(image_name, images_folder)
    print(f"Suche B-Seite Bild: {action_desc} ('{image_name}')")
    for attempt in range(retries):
        location = pyautogui.locateOnScreen(img_path, confidence=conf)
        if location:
            print(f"B-Seite Bild '{image_name}' gefunden bei {location}. Klicke...")
            pyautogui.click(pyautogui.center(location), duration=PYAUTOGUI_DURATION)
            time.sleep(VERWEILZEIT_BSEITE / 2)  # Kurze Pause nach Klick
            return True
        print(f"B-Seite Bild '{image_name}' nicht gefunden (Versuch {attempt + 1}/{retries}).")
        if attempt < retries - 1:
            time.sleep(delay_between_retries)
    print(f"B-Seite Bild '{image_name}' nach {retries} Versuchen nicht gefunden.")
    return False


def _perform_bseite_automation_steps(page_for_dialog: ft.Page, partheight_value: float, images_folder_path: Path):
    """Führt die blockierenden PyAutoGUI-Aktionen für die B-Seite aus."""
    current_thread_id = threading.get_ident()
    print(f"[WorkerThread {current_thread_id}] B-Seiten Automation gestartet (Fertigteilhöhe: {partheight_value})")

    # Hilfsfunktion, um Flet-Fenster in Vordergrund zu bringen (Windows-spezifisch)
    def _bring_flet_to_front():
        if os.name == 'nt' and PYWIN32_AVAILABLE:
            try:
                flet_title = page_for_dialog.title or "BlankMaker App"
                hwnd = win32gui.FindWindow(None, flet_title)
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
            except Exception as e_fg:
                print(f"Fehler beim B-Seiten Dialog Vordergrund: {e_fg}")

    try:
        time.sleep(VERWEILZEIT_BSEITE)  # Startverzögerung

        # Masken abwählen
        pyautogui.click(x=3111, y=1289, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)
        pyautogui.click(x=3111, y=1306, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)

        pyautogui.hotkey('ctrl', 'a');
        time.sleep(VERWEILZEIT_BSEITE)
        pyautogui.click(x=1685, y=81, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # Arbeitsebene-Menü
        pyautogui.click(x=1685, y=191, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # Arbeitsebene "Vorne"
        pyautogui.hotkey('ctrl', 'c');
        time.sleep(0.2)

        # Rotieren
        pyautogui.press('r');
        time.sleep(0.1);
        pyautogui.press('o');
        time.sleep(0.1)  # Befehl "Rotieren"
        pyautogui.click(x=2119, y=660, duration=PYAUTOGUI_DURATION);
        time.sleep(0.1)  # Originale behalten
        pyautogui.press('tab');
        time.sleep(0.1)  # Zum Winkelfeld
        pyautogui.typewrite("180");
        time.sleep(0.2)

        # Suche b1.png oder b2.png
        b1_found = _find_image_and_click_bseite('b1.png', images_folder_path, conf=0.7, action_desc="Rotieren Achse b1",
                                                retries=5)
        if not b1_found:
            b2_found = _find_image_and_click_bseite('b2.png', images_folder_path, conf=0.7,
                                                    action_desc="Rotieren Achse b2", retries=5)
            if not b2_found:
                raise Exception("Bilder für Rotationsachse (b1.png oder b2.png) nicht gefunden.")
        pyautogui.click(x=2153, y=816, duration=PYAUTOGUI_DURATION)  # Bestätigungspunkt nach Bildklick
        time.sleep(VERWEILZEIT_BSEITE)

        # Arbeitsebene XYZ auswählen
        pyautogui.click(x=1685, y=80, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)
        pyautogui.click(x=1685, y=116, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # AE "XYZ"
        pyautogui.hotkey('ctrl', 'c');
        time.sleep(0.2)

        # Verschieben
        pyautogui.press('v');
        time.sleep(0.1)  # Befehl "Verschieben"
        pyautogui.click(x=2119, y=660, duration=PYAUTOGUI_DURATION);
        time.sleep(0.1)  # Originale
        for _ in range(2): pyautogui.press('tab')  # Zu X-Feld
        pyautogui.typewrite("0");
        pyautogui.press('tab')  # X 0
        pyautogui.typewrite("0");
        pyautogui.press('tab')  # Y 0
        pyautogui.typewrite(str(partheight_value));
        time.sleep(0.1)  # Z partheight
        pyautogui.press('enter');
        time.sleep(VERWEILZEIT_BSEITE)

        pyautogui.click(x=1021, y=177, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # Freiklick
        pyautogui.press('F8');
        time.sleep(VERWEILZEIT_BSEITE)  # ISO Ansicht

        # Masken einblenden
        pyautogui.click(x=3103, y=1290, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)
        pyautogui.click(x=3118, y=1307, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)

        # Feature auswählen und kopieren
        pyautogui.click(x=1477, y=80, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # Feature Manager
        pyautogui.click(x=1477, y=132, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # "Alle Features"
        pyautogui.hotkey('ctrl', 'a');
        time.sleep(VERWEILZEIT_BSEITE)
        pyautogui.hotkey('ctrl', 'c');
        time.sleep(1.5)  # Längere Pause nach Copy

        # Symmetrie
        pyautogui.press('s');
        time.sleep(0.1);
        pyautogui.press('y');
        time.sleep(0.1)  # Befehl "Symmetrie"
        pyautogui.click(x=2119, y=660, duration=PYAUTOGUI_DURATION);
        time.sleep(0.1)  # Originale
        pyautogui.click(x=2088, y=751, duration=PYAUTOGUI_DURATION);
        time.sleep(0.1)  # Y Achse
        pyautogui.click(x=1021, y=177, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # Freiklick

        # Suche b3.png oder b4.png
        b3_found = _find_image_and_click_bseite('b3.png', images_folder_path, conf=0.7, action_desc="Symmetrieebene b3",
                                                retries=5)
        if not b3_found:
            b4_found = _find_image_and_click_bseite('b4.png', images_folder_path, conf=0.7,
                                                    action_desc="Symmetrieebene b4", retries=5)
            if not b4_found:
                raise Exception("Bilder für Symmetrieebene (b3.png oder b4.png) nicht gefunden.")
        pyautogui.click(x=2153, y=816, duration=PYAUTOGUI_DURATION)  # Bestätigungspunkt
        time.sleep(VERWEILZEIT_BSEITE)
        pyautogui.press('enter');
        time.sleep(VERWEILZEIT_BSEITE)

        # Konturzug auswählen
        pyautogui.click(x=1477, y=82, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # Feature Manager
        pyautogui.click(x=1477, y=251, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # "Konturzug"
        pyautogui.hotkey('ctrl', 'a');
        time.sleep(VERWEILZEIT_BSEITE)

        # Bearbeitungsseite ändern
        pyautogui.click(x=239, y=701, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # Klick auf Eigenschaft
        pyautogui.press('up');
        time.sleep(0.2)
        pyautogui.press('up');
        time.sleep(VERWEILZEIT_BSEITE)  # Zweimal hoch für "Hinten" oder "Unten"
        pyautogui.click(x=1020, y=175, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # Freiklick

        # Alles auswählen (Werkzeugwege)
        pyautogui.click(x=1477, y=80, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)
        pyautogui.click(x=1477, y=101, duration=PYAUTOGUI_DURATION);
        time.sleep(VERWEILZEIT_BSEITE)  # "Alle" (Werkzeugwege)

        # Neuberechnen
        pyautogui.click(x=1514, y=137, duration=PYAUTOGUI_DURATION)  # Klick auf Neuberechnen
        print(f"[WorkerThread {current_thread_id}] Neuberechnung gestartet, warte kurz...")
        time.sleep(3)  # Zeit für Neuberechnung geben

        _show_flet_dialog_from_thread(page_for_dialog, "B-Seite Automatisierung",
                                      "B-Seiten Automatisierung erfolgreich abgeschlossen.",
                                      bring_to_front_func=_bring_flet_to_front)
        print(f"[WorkerThread {current_thread_id}] B-Seiten Automation beendet.")

    except pyautogui.FailSafeException:
        msg = "Maus in Ecke bewegt (Fail-Safe). B-Seiten Automatisierung abgebrochen."
        print(f"[WorkerThread {current_thread_id}] PyAutoGUI FailSafe: {msg}")
        _show_flet_dialog_from_thread(page_for_dialog, "Abbruch (Fail-Safe)", msg, is_error=True,
                                      bring_to_front_func=_bring_flet_to_front)
    except FileNotFoundError as fnf_err:
        msg = f"Ein benötigtes Bild wurde nicht gefunden:\n{fnf_err}\nB-Seiten Automatisierung abgebrochen."
        print(f"[WorkerThread {current_thread_id}] FileNotFoundError: {msg}")
        _show_flet_dialog_from_thread(page_for_dialog, "Bild nicht gefunden", msg, is_error=True,
                                      bring_to_front_func=_bring_flet_to_front)
    except Exception as e:
        msg = f"Ein unerwarteter Fehler ist in der B-Seiten Automatisierung aufgetreten:\n{e}"
        print(f"[WorkerThread {current_thread_id}] Exception in B-Seiten Automation:")
        traceback.print_exc()
        _show_flet_dialog_from_thread(page_for_dialog, "Fehler in B-Seite", msg, is_error=True,
                                      bring_to_front_func=_bring_flet_to_front)


def start_bseite_automation_threaded(page_instance: ft.Page, partheight_value: float, images_base_path: Path):
    """
    Startet die B-Seiten Mausbewegungen in einem separaten Thread.
    images_base_path: Pfad zum Ordner, der die Bilder für PyAutoGUI enthält.
    """
    print(f"Starte B-Seiten Automation im Thread (Fertigteilhöhe: {partheight_value})")

    # Sicherstellen, dass der Basispfad für Bilder korrekt ist
    if not images_base_path.is_dir():
        _show_flet_dialog_from_thread(page_instance, "Fehler B-Seite",
                                      f"Bilder-Ordner nicht gefunden: {images_base_path}", is_error=True)
        return

    automation_thread = threading.Thread(target=_perform_bseite_automation_steps,
                                         args=(page_instance, partheight_value, images_base_path),
                                         daemon=True)
    automation_thread.start()
    print("B-Seiten Automations-Thread gestartet.")