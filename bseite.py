# bseite.py
import pyautogui
import time
import flet as ft  # Tkinter-Importe hier nicht mehr nötig für den Dialog
import threading
import traceback  # Für detaillierte Fehlerausgabe
import os  # Für Bildpfade

# Verweilzeit global (oder als Parameter übergeben, falls flexibler sein soll)
VERWEILZEIT = 0.5


# --- Hilfsfunktion zum Anzeigen von Flet-Dialogen ---
def _show_flet_dialog(page_ref: ft.Page, title: str, content: str, is_error: bool = False):
    """
    Zeigt einen Flet-Dialog an. Diese Funktion wird vom Worker-Thread aufgerufen,
    um sicherzustellen, dass UI-Operationen korrekt an Flet übergeben werden.
    """
    current_thread_id = threading.get_ident()
    print(f"[Thread {current_thread_id}] _show_flet_dialog - Titel: '{title}'")

    # Optional: Versuchen, das Flet-Fenster in den Vordergrund zu bringen (Windows-spezifisch)
    if os.name == 'nt':
        try:
            import win32gui
            import win32con
            flet_window_title = page_ref.title  # Annahme: page.title ist gesetzt und eindeutig
            if flet_window_title:
                hwnd = win32gui.FindWindow(None, flet_window_title)
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    print(f"[Thread {current_thread_id}] Flet-Fenster in den Vordergrund gebracht.")
                    time.sleep(0.1)  # Kurze Pause
                else:
                    print(f"[Thread {current_thread_id}] Flet-Fenster mit Titel '{flet_window_title}' nicht gefunden.")
            else:
                print(f"[Thread {current_thread_id}] Flet-Fenstertitel ist leer, Vordergrund nicht möglich.")
        except ImportError:
            print(f"[Thread {current_thread_id}] pywin32 nicht installiert, Vordergrund nicht möglich.")
        except Exception as e_fg:
            print(f"[Thread {current_thread_id}] Fehler beim In-Vordergrund-Bringen: {e_fg}")

    # Die Funktion, die den Dialog tatsächlich öffnet (wird von Flet im UI-Thread ausgeführt)
    def open_dialog_action():
        flet_thread_id = threading.get_ident()  # Sollte der Flet-Hauptthread sein
        print(f"[FletThread {flet_thread_id}] open_dialog_action - Titel: '{title}'")

        dialog_to_show = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[
                ft.TextButton("OK", on_click=lambda _: page_ref.close(dialog_to_show))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda _: print(f"Dialog '{title}' abgewiesen (on_dismiss)")
        )
        page_ref.open(dialog_to_show)  # Flet-Methode zum Öffnen des Dialogs
        print(f"[FletThread {flet_thread_id}] page.open('{title}') aufgerufen.")

    # Führe das Öffnen des Dialogs im Flet-Hauptthread aus.
    # Flet's page.open ist so konzipiert, dass es aus Threads aufgerufen werden kann.
    open_dialog_action()


# --- Die eigentlichen Mausbewegungen in einer separaten Funktion ---
def _perform_bseite_automation(page_for_dialog: ft.Page, partheight_value: float, base_image_path: str):
    """Führt die blockierenden PyAutoGUI-Aktionen aus."""
    current_thread_id = threading.get_ident()
    print(f"[WorkerThread {current_thread_id}] _perform_bseite_automation gestartet mit partheight: {partheight_value}")
    try:
        # HILFSFUNKTION für Bildpfade (angenommen, Bilder sind in einem Unterordner "Bilder")
        def get_image_path(image_name):
            # Erwartet, dass base_image_path das Verzeichnis ist, in dem bseite.py liegt
            # oder ein übergeordnetes Verzeichnis, das "Bilder" enthält.
            # Besser: Mache base_image_path zum expliziten Pfad des "Bilder"-Ordners.
            # Für jetzt: Annahme, dass base_image_path der Ordner des Skripts ist.
            img_path = os.path.join(base_image_path, "Bilder", image_name)
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Bilddatei nicht gefunden: {img_path}")
            return img_path

        # HILFSFUNKTION für die Bildsuche
        def find_image_on_screen(image_name_with_ext, threshold=0.8, action_description="Bild"):
            full_path = get_image_path(image_name_with_ext)
            print(f"[WorkerThread {current_thread_id}] Suche nach {action_description}: '{full_path}'")
            location = pyautogui.locateOnScreen(full_path, confidence=threshold)
            if location:
                print(
                    f"[WorkerThread {current_thread_id}] {action_description} '{image_name_with_ext}' gefunden bei {location}.")
            else:
                print(
                    f"[WorkerThread {current_thread_id}] {action_description} '{image_name_with_ext}' NICHT gefunden.")
            return location

        time.sleep(VERWEILZEIT)  # Kurze Startverzögerung

        #  Masken - feature u werkzeugweg abwählen
        print(f"[WorkerThread {current_thread_id}] Masken abwählen...")
        pyautogui.click(x=3111, y=1289, duration=1)
        time.sleep(VERWEILZEIT)
        pyautogui.click(x=3111, y=1306)
        time.sleep(VERWEILZEIT)

        pyautogui.hotkey('ctrl', 'a');
        time.sleep(VERWEILZEIT)
        pyautogui.click(x=1685, y=81);
        time.sleep(VERWEILZEIT)
        pyautogui.click(x=1685, y=191);
        time.sleep(VERWEILZEIT)  # Arbeitsebene vorne
        pyautogui.hotkey('ctrl', 'c');
        time.sleep(0.2)
        print(f"[WorkerThread {current_thread_id}] Arbeitsebene vorne kopiert.")

        # Rotieren
        print(f"[WorkerThread {current_thread_id}] Rotiere...")
        pyautogui.press('r');
        time.sleep(0.1)
        pyautogui.press('o');
        time.sleep(0.1)
        pyautogui.click(x=2119, y=660);
        time.sleep(0.1)  # Originale
        pyautogui.press('tab');
        time.sleep(0.1)  # Einmal Tab
        pyautogui.typewrite("180");
        time.sleep(0.2)

        # Schleife für die Suche nach b1 und b2
        print(f"[WorkerThread {current_thread_id}] Suche b1/b2...")
        b1_found = False
        for _ in range(10):  # Maximal 10 Versuche (10 Sekunden)
            b1_location = find_image_on_screen('b1.png', action_description="b1")
            if b1_location:
                pyautogui.click(pyautogui.center(b1_location));
                time.sleep(0.5)
                pyautogui.click(x=2153, y=816);
                b1_found = True;
                break

            b2_location = find_image_on_screen('b2.png', action_description="b2")
            if b2_location:  # b1 nicht gefunden, aber b2
                pyautogui.click(x=2153, y=816);
                time.sleep(0.5);
                b1_found = True;
                break  # b1_found hier auch True setzen, da es ein Endzustand ist
            print(f"[WorkerThread {current_thread_id}] b1/b2 noch nicht gefunden, warte 1 Sek...")
            time.sleep(1)
        if not b1_found:
            raise Exception("Bilder b1.png oder b2.png konnten nicht gefunden werden.")
        print(f"[WorkerThread {current_thread_id}] b1/b2 Verarbeitung abgeschlossen.")
        time.sleep(VERWEILZEIT)

        # Arbeitsebene xyz auswählen
        pyautogui.click(x=1685, y=80);
        time.sleep(VERWEILZEIT)
        pyautogui.click(x=1685, y=116);
        time.sleep(VERWEILZEIT)
        pyautogui.hotkey('ctrl', 'c');
        time.sleep(0.2)
        print(f"[WorkerThread {current_thread_id}] Arbeitsebene XYZ kopiert.")

        # Verschieben suchen
        pyautogui.press('v');
        time.sleep(0.1)
        pyautogui.click(x=2119, y=660);
        time.sleep(0.1)  # Originale

        for _ in range(2): pyautogui.press('tab')  # 2x Tab
        pyautogui.typewrite("0");
        pyautogui.press('tab')  # X 0
        pyautogui.typewrite("0");
        pyautogui.press('tab')  # Y 0
        pyautogui.typewrite(str(partheight_value));
        time.sleep(VERWEILZEIT)  # Z partheight
        pyautogui.press('enter')
        print(f"[WorkerThread {current_thread_id}] Bauteil verschoben um Z: {partheight_value}.")

        pyautogui.click(x=1021, y=177);
        time.sleep(VERWEILZEIT)  # Freiklick
        pyautogui.press('F8');
        time.sleep(VERWEILZEIT)  # ISO Ansicht

        # Masken einblenden
        pyautogui.click(x=3103, y=1290);
        time.sleep(VERWEILZEIT)
        pyautogui.click(x=3118, y=1307);
        time.sleep(VERWEILZEIT)
        print(f"[WorkerThread {current_thread_id}] Masken eingeblendet.")

        # Feature auswählen
        pyautogui.click(x=1477, y=80);
        time.sleep(VERWEILZEIT)
        pyautogui.click(x=1477, y=132);
        time.sleep(VERWEILZEIT)
        pyautogui.hotkey('ctrl', 'a');
        time.sleep(VERWEILZEIT)
        pyautogui.hotkey('ctrl', 'c');
        time.sleep(2)  # Längere Pause nach Copy
        print(f"[WorkerThread {current_thread_id}] Features kopiert.")

        # Symmetrie
        pyautogui.press('s');
        time.sleep(0.1)
        pyautogui.press('y');
        time.sleep(0.1)
        pyautogui.click(x=2119, y=660);
        time.sleep(0.1)  # Originale
        pyautogui.click(x=2088, y=751);
        time.sleep(0.1)  # Y Achse
        print(f"[WorkerThread {current_thread_id}] Symmetrie Y-Achse.")

        pyautogui.click(x=1021, y=177);
        time.sleep(VERWEILZEIT)  # Freiklick

        # Schleife für die Suche nach b3 und b4
        print(f"[WorkerThread {current_thread_id}] Suche b3/b4...")
        b3_found = False
        for _ in range(10):  # Maximal 10 Versuche
            b3_location = find_image_on_screen('b3.png', action_description="b3")
            if b3_location:
                pyautogui.click(pyautogui.center(b3_location));
                time.sleep(0.5)
                pyautogui.click(x=2153, y=816);
                b3_found = True;
                break

            b4_location = find_image_on_screen('b4.png',
                                               action_description="b4")  # find_image_on_screen statt find_image
            if b4_location:
                pyautogui.click(x=2153, y=816);
                time.sleep(0.5);
                b3_found = True;
                break
            print(f"[WorkerThread {current_thread_id}] b3/b4 noch nicht gefunden, warte 1 Sek...")
            time.sleep(1)
        if not b3_found:
            raise Exception("Bilder b3.png oder b4.png konnten nicht gefunden werden.")
        print(f"[WorkerThread {current_thread_id}] b3/b4 Verarbeitung abgeschlossen.")

        pyautogui.click(x=2152, y=815);
        time.sleep(VERWEILZEIT)  # Eine Position anklicken
        pyautogui.press('enter');
        time.sleep(VERWEILZEIT)

        # Konturzug
        pyautogui.click(x=1477, y=82);
        time.sleep(VERWEILZEIT)  # Alles
        pyautogui.click(x=1477, y=251);
        time.sleep(VERWEILZEIT)  # Konturzug
        pyautogui.hotkey('ctrl', 'a');
        time.sleep(VERWEILZEIT)
        print(f"[WorkerThread {current_thread_id}] Konturzug ausgewählt.")

        # Bearbeitungsseite
        pyautogui.click(x=239, y=701);
        time.sleep(VERWEILZEIT)
        pyautogui.press('up');
        time.sleep(0.2)
        pyautogui.press('up');
        time.sleep(VERWEILZEIT)
        print(f"[WorkerThread {current_thread_id}] Bearbeitungsseite eingestellt.")

        pyautogui.click(x=1020, y=175);
        time.sleep(VERWEILZEIT)  # Freiklick

        # Alles
        pyautogui.click(x=1477, y=80, duration=1);
        time.sleep(VERWEILZEIT)
        pyautogui.click(x=1477, y=101);
        time.sleep(VERWEILZEIT)  # Alles eins unterhalb

        # Neuberechnen
        pyautogui.click(x=1514, y=137, duration=1)
        print(f"[WorkerThread {current_thread_id}] Neuberechnung gestartet.")
        time.sleep(2)  # Gib Zeit für Neuberechnung

        # Automatisierung abgeschlossen, zeige Flet-Dialog
        _show_flet_dialog(page_for_dialog,
                          "B-Seiten Automatisierung",
                          "B-Seiten Automatisierung erfolgreich abgeschlossen.\nKlicke auf OK um weiter Programmieren zu können.")
        print(f"[WorkerThread {current_thread_id}] _perform_bseite_automation beendet.")

    except pyautogui.FailSafeException:
        message = "Maus wurde in eine Ecke bewegt (Fail-Safe). B-Seiten Automatisierung abgebrochen."
        print(f"[WorkerThread {current_thread_id}] PyAutoGUI FailSafe: {message}")
        _show_flet_dialog(page_for_dialog, "Abbruch durch Fail-Safe", message, is_error=True)
    except FileNotFoundError as fnf_err:
        message = f"Ein benötigtes Bild wurde nicht gefunden:\n{fnf_err}\nB-Seiten Automatisierung abgebrochen."
        print(f"[WorkerThread {current_thread_id}] FileNotFoundError: {message}")
        _show_flet_dialog(page_for_dialog, "Bild nicht gefunden", message, is_error=True)
    except Exception as e:
        message = f"Ein unerwarteter Fehler ist in der B-Seiten Automatisierung aufgetreten:\n{e}"
        print(f"[WorkerThread {current_thread_id}] Exception in _perform_bseite_automation:")
        traceback.print_exc()
        _show_flet_dialog(page_for_dialog, "Fehler in B-Seite", message, is_error=True)


# --- Hauptfunktion, die von Flet aufgerufen wird ---
def start_mausbewegungen(page_instance: ft.Page, partheight: float):
    """
    Startet die B-Seiten Mausbewegungen in einem separaten Thread.
    page_instance: Die Flet Page Instanz für Dialoge.
    partheight: Die zu verwendende Fertigteilhöhe.
    """
    print(f"start_mausbewegungen aufgerufen mit partheight: {partheight}")

    # Pfad zum Ordner, in dem dieses Skript (bseite.py) liegt.
    # Angenommen, der "Bilder"-Ordner ist ein Unterordner davon.
    script_folder_path = os.path.dirname(os.path.abspath(__file__))

    # Erstelle und starte einen neuen Thread für die blockierenden PyAutoGUI-Aktionen
    automation_thread = threading.Thread(target=_perform_bseite_automation,
                                         args=(page_instance, partheight, script_folder_path),
                                         daemon=True)
    automation_thread.start()
    print("B-Seiten Automations-Thread gestartet.")
    # Die Funktion kehrt sofort zurück, Flet UI bleibt responsiv.