# kombiablauf.py
import threading

import pyautogui
import pyscreeze
import os
import time
import flet as ft
from autoesprit import run_program
import multiprocessing  # Geändert von threading
import traceback

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

# --- Tkinter Overlay Fenster (bleibt gleich) ---
if TKINTER_AVAILABLE:
    class RedDotOverlay(tk.Toplevel):
        def __init__(self, parent_tk_root, x, y, size=10):
            super().__init__(parent_tk_root)
            self.overrideredirect(True)
            self.attributes("-topmost", True)
            self.attributes("-transparentcolor", "white")
            self.attributes("-alpha", 0.8)
            self.geometry(f"{size}x{size}+{x - size // 2}+{y - size // 2}")
            self.canvas = tk.Canvas(self, width=size, height=size, bg="white", highlightthickness=0)
            self.canvas.pack()
            self.canvas.create_oval(0, 0, size, size, fill="red", outline="red")
            parent_tk_root.update_idletasks()
            parent_tk_root.update()


# NEU: Diese Funktion wird in einem separaten Prozess ausgeführt.
def show_red_dot_process_target(x: int, y: int, size: int):
    """
    Erstellt und zeigt das rote Punkt-Fenster in einer eigenen,
    isolierten Prozess-Schleife an.
    """
    try:
        root = tk.Tk()
        root.withdraw()
        dot = RedDotOverlay(root, x, y, size)
        # Einfache Schleife, die das Fenster am Leben hält.
        # Wird von außen durch process.terminate() beendet.
        while True:
            root.update_idletasks()
            root.update()
            time.sleep(0.05)
    except (KeyboardInterrupt, SystemExit):
        # Prozess wurde beendet.
        pass
    except Exception as e:
        # Fehler in einer Datei protokollieren, da print nicht sichtbar ist.
        with open("red_dot_error.log", "a") as f:
            f.write(f"Error in red dot process: {e}\n{traceback.format_exc()}\n")


# --- Hauptlogikklasse ---
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

        # GEÄNDERT: Wir verwalten jetzt einen Prozess statt eines Threads.
        self.red_dot_process = None

    # _bring_flet_window_to_front_windows bleibt unverändert...
    def _bring_flet_window_to_front_windows(self):
        if not PYWIN32_AVAILABLE or os.name != 'nt': return False
        try:
            hwnd = win32gui.FindWindow(None, self.flet_window_title)
            if hwnd: win32gui.ShowWindow(hwnd, win32con.SW_RESTORE); win32gui.SetForegroundWindow(hwnd); return True
        except Exception as e:
            print(f"Fehler beim Fokussieren: {e}"); return False

    # GEÄNDERT: Startet einen Prozess, kein Thread.
    def _show_red_dot_overlay(self, x: int, y: int, size: int = 20):
        if not TKINTER_AVAILABLE: return

        # Alten Prozess zuerst beenden, falls vorhanden
        self._close_red_dot_overlay()

        print("Starte roten Punkt in separatem Prozess...")
        try:
            # 'spawn' ist auf macOS und Windows am stabilsten.
            ctx = multiprocessing.get_context('spawn')
            self.red_dot_process = ctx.Process(
                target=show_red_dot_process_target,
                args=(x, y, size),
                daemon=True  # Prozess wird mit dem Hauptprogramm beendet
            )
            self.red_dot_process.start()
            print(f"Roter Punkt Prozess gestartet mit PID: {self.red_dot_process.pid}")
        except Exception as e:
            print(f"Fehler beim Starten des roten Punkt Prozesses: {e}")

    # GEÄNDERT: Beendet den Prozess.
    def _close_red_dot_overlay(self):
        if self.red_dot_process and self.red_dot_process.is_alive():
            print(f"Beende roten Punkt Prozess PID: {self.red_dot_process.pid}...")
            self.red_dot_process.terminate()  # Sendet SIGTERM
            self.red_dot_process.join(timeout=1)  # Warte kurz auf Beendigung
            if self.red_dot_process.is_alive():
                print(f"Warnung: Prozess {self.red_dot_process.pid} konnte nicht sauber beendet werden.")
            else:
                print("Roter Punkt Prozess erfolgreich beendet.")
            self.red_dot_process = None
        else:
            print("Kein aktiver roter Punkt Prozess zum Beenden gefunden.")

    # Der Rest des Codes bleibt strukturell gleich, ruft aber die neuen Methoden auf.
    # _handle_final_dialog_result, _show_dialog_from_thread, etc.
    def _handle_final_dialog_result(self, e: ft.ControlEvent, dialog_ref: ft.AlertDialog):
        self.page.close(dialog_ref)
        self.active_dialog = None
        if e.control.data == "yes":
            print("[Flet] Prozess wird fortgesetzt...")
            try:
                l, w, h = (float(f.value.replace(',', '.')) for f in
                           [self.length_field, self.width_field, self.height_field])
                run_program(l, w, h)
            except Exception as ex:
                self._show_dialog_from_thread("Fehler bei Fortsetzung", f"Fehler: {ex}", True)
        else:
            print("[Flet] Aktion abgebrochen.")

    def _show_dialog_from_thread(self, title: str, content: str, is_error: bool = False, show_dot: bool = False,
                                 dot_x: int = 0, dot_y: int = 0):
        self._bring_flet_window_to_front_windows()
        time.sleep(0.2)
        if show_dot:
            self._show_red_dot_overlay(dot_x, dot_y)

        def open_dialog_on_flet_thread():
            actions = []
            dialog = ft.AlertDialog(
                modal=True, title=ft.Text(title), content=ft.Text(content),
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=lambda e: self._close_red_dot_overlay()
            )
            if is_error:
                actions.append(ft.TextButton("OK", on_click=lambda e: self.page.close(dialog)))
            else:
                actions.extend([
                    ft.TextButton("Ja", on_click=lambda ev: self._handle_final_dialog_result(ev, dialog), data="yes"),
                    ft.TextButton("Nein", on_click=lambda ev: self._handle_final_dialog_result(ev, dialog), data="no"),
                ])
            dialog.actions = actions
            if self.active_dialog: self.page.close(self.active_dialog)
            self.active_dialog = dialog
            self.page.open(dialog)
            self.page.update()

        open_dialog_on_flet_thread()

    # Der Rest der Klasse (perform_actions, kombiablauf, action_1, etc.) bleibt unverändert.
    def _perform_actions(self):
        worker_thread_id = threading.get_ident()
        print(f"[WorkerThread {worker_thread_id}] _perform_actions gestartet.")
        try:
            time.sleep(0.2)
            self.action_1();
            self.action_2();
            self.action_3();
            self.action_4();
            self.action_5();
            self.action_6();
            self.action_7()
            print(f"[WorkerThread {worker_thread_id}] Aktionen erfolgreich beendet.")
            time.sleep(0.5)
            self._show_dialog_from_thread(
                "Pause!",
                "Hallo Hannes, hab ich gute Arbeit geleistet? Soll ich noch weitere Aufgaben für dich übernehmen?",
                is_error=False, show_dot=True, dot_x=2205, dot_y=814
            )
        except Exception as e:
            msg = f"Unerwarteter Fehler in der Automation:\n{e}"
            traceback.print_exc()
            self._show_dialog_from_thread("Fehler im Ablauf", msg, is_error=True)
        print(f"[WorkerThread {worker_thread_id}] _perform_actions beendet.")

    def kombiablauf(self):
        print("kombiablauf(): Starte Automations-Thread...")
        self.flet_window_title = self.page.title or "Blank Maker Master 7.7 by Gschwendtner Johannes"
        action_thread = threading.Thread(target=self._perform_actions, daemon=True)
        action_thread.start()
        print("kombiablauf(): Automations-Thread gestartet.")

    def _locate_and_click(self, image_name: str, confidence: float, action_name: str, click_type: str = "click",
                          grayscale: bool = False, wait_before_click: float = 0.1, wait_after_click: float = 0.5):
        if not os.path.isabs(image_name) and not os.path.exists(image_name):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path_in_script_dir = os.path.join(script_dir, image_name)
            if not os.path.exists(image_path_in_script_dir):
                raise FileNotFoundError(f"Bilddatei '{image_name}' für Aktion '{action_name}' nicht gefunden.")
            image_to_find = image_path_in_script_dir
        else:
            image_to_find = image_name
        pos = pyscreeze.locateOnScreen(image_to_find, confidence=confidence, grayscale=grayscale)
        if pos is None: raise Exception(f"Bild '{os.path.basename(image_to_find)}' für '{action_name}' nicht gefunden.")
        center = pyscreeze.center(pos)
        time.sleep(wait_before_click)
        if click_type == "click":
            pyautogui.click(center)
        elif click_type == "doubleclick":
            pyautogui.doubleClick(center)
        time.sleep(wait_after_click)

    def action_1(self):
        print(f"A1"), self._locate_and_click('Bilder/1.png', 0.5, "A1", wait_after_click=0.5), print(f"A1 ende")

    def action_2(self):
        print(f"A2"), self._locate_and_click('Bilder/2.png', 0.4, "A2", wait_after_click=0.9), print(f"A2 ende")

    def action_3(self):
        print(f"A3"), self._locate_and_click('Bilder/3.png', 0.5, "A3 (Bild)", click_type="doubleclick", grayscale=True,
                                             wait_after_click=0.4), time.sleep(0.2), pyautogui.press(
            'delete'), time.sleep(0.1), pyautogui.typewrite(self.ctrl_v_field.value + '_A'), time.sleep(0.1), print(
            f"A3 ende")

    def action_4(self):
        print(f"A4"), pyautogui.press('tab', presses=2, interval=0.1), time.sleep(0.1), pyautogui.press(
            'delete'), time.sleep(0.1), pyautogui.typewrite(self.ctrl_v_field.value), time.sleep(0.1), print(f"A4 ende")

    def action_5(self):
        print(f"A5"), pyautogui.press('tab'), time.sleep(0.1), pyautogui.hotkey('ctrl', 'a'), pyautogui.press(
            'delete'), time.sleep(
            0.1); text = self.selection_dropdown.value; assert text and text != "Option", "Programmtyp auswählen!"; pyautogui.typewrite(
            text); time.sleep(0.1); print(f"A5 ende")

    def action_6(self):
        print(f"A6"), pyautogui.press('enter'), time.sleep(0.1), print(f"A6 ende")

    def action_7(self):
        print(f"A7"); d = self.destination_field.value; assert d and os.path.isdir(
            d), f"Zielordner '{d}' ungültig."; r, s = os.path.join(d, "!rohteil.dxf"), os.path.join(d,
                                                                                                    "!schraubstock.step"); assert os.path.isfile(
            r), f"Datei '{r}' nicht gefunden."; assert os.path.isfile(
            s), f"Datei '{s}' nicht gefunden."; pyautogui.doubleClick(974, 1047, duration=0.4); time.sleep(
            0.5); pyautogui.hotkey('ctrl', 'o'); time.sleep(0.5); pyautogui.typewrite(r); time.sleep(
            0.5); pyautogui.press('enter'); time.sleep(1.0); pyautogui.doubleClick(977, 1142, duration=0.4); time.sleep(
            0.5); pyautogui.hotkey('ctrl', 'o'); time.sleep(0.8); pyautogui.typewrite(s); time.sleep(
            0.8); pyautogui.press('enter'); time.sleep(1.0); print(f"A7 ende")