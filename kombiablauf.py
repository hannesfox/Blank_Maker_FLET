# kombiablauf.py

import multiprocessing
import os
import time
import traceback
import flet as ft
import pyautogui
import pyscreeze
import threading

# Importieren Sie die Funktion, die Sie nach dem Dialog aufrufen möchten
from autoesprit import run_program

# --- Verfügbarkeitsprüfungen für Bibliotheken ---
try:
    import tkinter as tk

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("WARNUNG: Tkinter nicht verfügbar. Der rote Punkt kann nicht angezeigt werden.")

if os.name == 'nt':
    try:
        import win32gui
        import win32con

        PYWIN32_AVAILABLE = True
    except ImportError:
        PYWIN32_AVAILABLE = False
        print("WARNUNG: pywin32 nicht installiert. Fokus kann nicht erzwungen werden.")
else:
    PYWIN32_AVAILABLE = False


# --- Tkinter Logik, ausgelagert in eine Top-Level-Funktion ---
# Diese Funktion wird als Ziel für den neuen Prozess dienen.

def show_red_dot_process_target(x: int, y: int, size: int = 20):
    """
    Erstellt und zeigt ein einfaches Tkinter-Fenster mit einem roten Punkt.
    Diese Funktion ist dafür gedacht, in einem separaten Prozess ausgeführt zu werden,
    um Konflikte mit anderen GUI-Toolkits wie Flet zu vermeiden.
    """
    if not TKINTER_AVAILABLE:
        return

    class RedDotOverlay(tk.Toplevel):
        def __init__(self, parent_tk_root, dot_x, dot_y, dot_size):
            super().__init__(parent_tk_root)
            self.overrideredirect(True)  # Kein Fensterrand
            self.attributes("-topmost", True)  # Immer im Vordergrund
            self.attributes("-transparentcolor", "white")  # Macht Weiß transparent
            self.attributes("-alpha", 0.8)  # Leichte Transparenz
            # Zentriert den Punkt auf den Koordinaten x, y
            geometry_x = dot_x - dot_size // 2
            geometry_y = dot_y - dot_size // 2
            self.geometry(f"{dot_size}x{dot_size}+{geometry_x}+{geometry_y}")

            canvas = tk.Canvas(self, width=dot_size, height=dot_size, bg="white", highlightthickness=0)
            canvas.pack()
            canvas.create_oval(0, 0, dot_size, dot_size, fill="red", outline="red")
            parent_tk_root.update()

    try:
        root = tk.Tk()
        root.withdraw()  # Das Hauptfenster von Tkinter verstecken
        _ = RedDotOverlay(root, x, y, size)
        root.mainloop()  # Startet die Tkinter-Event-Loop
    except (KeyboardInterrupt, SystemExit):
        # Prozess wurde von außen beendet (z.B. durch terminate())
        pass
    except Exception as e:
        # Fehler in eine Log-Datei schreiben, da print im Subprozess nicht sichtbar ist
        with open("red_dot_error.log", "a") as f:
            f.write(f"Error in red dot process: {e}\n{traceback.format_exc()}\n")


class Kombiablauf:
    def __init__(self, page: ft.Page, ctrl_v_field: ft.TextField, selection_dropdown: ft.Dropdown,
                 destination_field: ft.TextField, length_field: ft.TextField,
                 width_field: ft.TextField, height_field: ft.TextField):
        self.page = page
        self.ctrl_v_field = ctrl_v_field
        self.selection_dropdown = selection_dropdown
        self.destination_field = destination_field
        self.length_field = length_field
        self.width_field = width_field
        self.height_field = height_field
        self.flet_window_title = page.title
        self.active_dialog = None

        # NEU: Wir verwalten einen Prozess anstelle eines Threads für das Overlay
        self.red_dot_process: multiprocessing.Process | None = None

    def _bring_flet_window_to_front(self):
        """Bringt das Flet-Fenster in den Vordergrund (nur Windows)."""
        if not PYWIN32_AVAILABLE or os.name != 'nt':
            return False
        try:
            hwnd = win32gui.FindWindow(None, self.flet_window_title)
            if hwnd:
                # SetForegroundWindow kann fehlschlagen, wenn der Prozess nicht im Vordergrund ist.
                # Eine Kombination aus SW_RESTORE und SetForegroundWindow ist oft robuster.
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                return True
        except Exception as e:
            print(f"Fehler beim Fokussieren des Fensters: {e}")
        return False

    def _start_red_dot_overlay(self, x: int, y: int, size: int = 20):
        """Startet den roten Punkt in einem separaten Prozess."""
        if not TKINTER_AVAILABLE:
            return

        self._stop_red_dot_overlay()  # Sicherstellen, dass kein alter Prozess mehr läuft

        try:
            # 'spawn' ist auf Windows und macOS die sicherste Methode
            ctx = multiprocessing.get_context('spawn')
            self.red_dot_process = ctx.Process(
                target=show_red_dot_process_target,
                args=(x, y, size),
                daemon=True  # Prozess wird beendet, wenn das Hauptprogramm endet
            )
            self.red_dot_process.start()
        except Exception as e:
            print(f"Fehler beim Starten des roten Punkt-Prozesses: {e}")

    def _stop_red_dot_overlay(self):
        """Beendet den Prozess des roten Punktes, falls er läuft."""
        if self.red_dot_process and self.red_dot_process.is_alive():
            self.red_dot_process.terminate()  # Sendet ein Terminate-Signal
            self.red_dot_process.join(timeout=1)  # Wartet kurz auf die Beendigung
            self.red_dot_process = None

    def _handle_final_dialog_result(self, e: ft.ControlEvent):
        """Verarbeitet das Ergebnis des Ja/Nein-Dialogs."""
        dialog = self.active_dialog
        if dialog:
            self.page.close(dialog)
            self.active_dialog = None

        # Der rote Punkt wird durch on_dismiss sowieso geschlossen

        if e.control.data == "yes":
            print("[Flet] Prozess wird fortgesetzt...")
            try:
                # Konvertiere die Werte aus den Textfeldern in floats
                l = float(self.length_field.value.replace(',', '.'))
                w = float(self.width_field.value.replace(',', '.'))
                h = float(self.height_field.value.replace(',', '.'))
                # Führe das Esprit-Automatisierungsprogramm aus
                run_program(l, w, h)
            except (ValueError, TypeError) as ex:
                self._show_dialog_on_main_thread("Fehler bei Eingabe", f"Ungültige Maße: {ex}", is_error=True)
            except Exception as ex:
                self._show_dialog_on_main_thread("Fehler bei Fortsetzung", f"Fehler: {ex}", is_error=True)
        else:
            print("[Flet] Aktion vom Benutzer abgebrochen.")

    def _show_dialog_on_main_thread(self, title: str, content: str, is_error: bool = False, show_dot: bool = False,
                                    dot_x: int = 0, dot_y: int = 0):
        """Zeigt einen Dialog im Flet-Thread an und bringt das Fenster nach vorne."""

        self._bring_flet_window_to_front()
        time.sleep(0.1)  # Kurze Pause, damit das Fenster den Fokus erhalten kann

        if show_dot:
            self._start_red_dot_overlay(dot_x, dot_y)

        actions = []
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(content),
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: self._stop_red_dot_overlay()  # Wichtig: Punkt entfernen, wenn Dialog geschlossen wird
        )

        if is_error:
            actions.append(ft.TextButton("OK", on_click=lambda e: self.page.close(dialog)))
        else:
            actions.extend([
                ft.TextButton("Ja", on_click=self._handle_final_dialog_result, data="yes"),
                ft.TextButton("Nein", on_click=self._handle_final_dialog_result, data="no"),
            ])

        dialog.actions = actions

        # Sicherstellen, dass Flet-UI-Updates im Haupt-Thread stattfinden
        def open_dialog():
            if self.active_dialog:
                self.page.close(self.active_dialog)
            self.active_dialog = dialog
            self.page.open(dialog)
            # self.page.update() # page.open() macht implizit ein update

        # Da diese Funktion vom Worker-Thread aufgerufen wird, müssen wir den UI-Call
        # an den Flet-Thread übergeben. Flet macht dies intern automatisch.
        open_dialog()

    def _perform_actions(self):
        """Die eigentliche Automatisierungssequenz, die in einem Thread läuft."""
        try:
            # Die Aktionen bleiben unverändert
            time.sleep(0.2)
            self.action_1()
            self.action_2()
            self.action_3()
            self.action_4()
            self.action_5()
            self.action_6()
            self.action_7()

            # Zeige den finalen Dialog an
            self._show_dialog_on_main_thread(
                title="Pause!",
                content="Hallo Hannes, hab ich gute Arbeit geleistet? Soll ich noch weitere Aufgaben für dich übernehmen?",
                is_error=False,
                show_dot=True,
                dot_x=2205,
                dot_y=814
            )
        except Exception as e:
            msg = f"Unerwarteter Fehler in der Automation:\n{e}"
            traceback.print_exc()
            self._show_dialog_on_main_thread("Fehler im Ablauf", msg, is_error=True)

    def kombiablauf(self):
        """Startet die Automatisierung in einem separaten Thread."""
        print("kombiablauf(): Starte Automations-Thread...")
        self.flet_window_title = self.page.title
        action_thread = threading.Thread(target=self._perform_actions, daemon=True)
        action_thread.start()

    # --- Die 'action_'-Methoden bleiben identisch ---
    def _locate_and_click(self, image_name: str, confidence: float, action_name: str, click_type: str = "click",
                          grayscale: bool = False, wait_before_click: float = 0.1, wait_after_click: float = 0.5):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, image_name)
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Bilddatei '{image_path}' für Aktion '{action_name}' nicht gefunden.")

        pos = pyscreeze.locateOnScreen(image_path, confidence=confidence, grayscale=grayscale)
        if pos is None:
            raise Exception(f"Bild '{os.path.basename(image_path)}' für '{action_name}' nicht gefunden.")

        center = pyscreeze.center(pos)
        time.sleep(wait_before_click)
        if click_type == "click":
            pyautogui.click(center)
        elif click_type == "doubleclick":
            pyautogui.doubleClick(center)
        time.sleep(wait_after_click)

    def action_1(self):
        print("A1"); self._locate_and_click('Bilder/1.png', 0.5, "A1", wait_after_click=0.5); print("A1 ende")

    def action_2(self):
        print("A2"); self._locate_and_click('Bilder/2.png', 0.4, "A2", wait_after_click=0.9); print("A2 ende")

    def action_3(self):
        print("A3"); self._locate_and_click('Bilder/3.png', 0.5, "A3 (Bild)", click_type="doubleclick", grayscale=True,
                                            wait_after_click=0.4); time.sleep(0.2); pyautogui.press(
            'delete'); time.sleep(0.1); pyautogui.typewrite(self.ctrl_v_field.value + '_A'); time.sleep(0.1); print(
            "A3 ende")

    def action_4(self):
        print("A4"); pyautogui.press('tab', presses=2, interval=0.1); time.sleep(0.1); pyautogui.press(
            'delete'); time.sleep(0.1); pyautogui.typewrite(self.ctrl_v_field.value); time.sleep(0.1); print("A4 ende")

    def action_5(self):
        print("A5"); pyautogui.press('tab'); time.sleep(0.1); pyautogui.hotkey('ctrl', 'a'); pyautogui.press(
            'delete'); time.sleep(
            0.1); text = self.selection_dropdown.value; assert text and text != "Option", "Programmtyp auswählen!"; pyautogui.typewrite(
            text); time.sleep(0.1); print("A5 ende")

    def action_6(self):
        print("A6"); pyautogui.press('enter'); time.sleep(0.1); print("A6 ende")

    def action_7(self):
        print("A7"); d = self.destination_field.value; assert d and os.path.isdir(
            d), f"Zielordner '{d}' ungültig."; r = os.path.join(d, "!rohteil.dxf"); s = os.path.join(d,
                                                                                                     "!schraubstock.step"); assert os.path.isfile(
            r), f"Datei '{r}' nicht gefunden."; assert os.path.isfile(
            s), f"Datei '{s}' nicht gefunden."; pyautogui.doubleClick(974, 1047, duration=0.4); time.sleep(
            0.5); pyautogui.hotkey('ctrl', 'o'); time.sleep(0.5); pyautogui.typewrite(r); time.sleep(
            0.5); pyautogui.press('enter'); time.sleep(1.0); pyautogui.doubleClick(977, 1142, duration=0.4); time.sleep(
            0.5); pyautogui.hotkey('ctrl', 'o'); time.sleep(0.8); pyautogui.typewrite(s); time.sleep(
            0.8); pyautogui.press('enter'); time.sleep(1.0); print("A7 ende")