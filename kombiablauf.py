# kombiablauf.py

import pyautogui
import pyscreeze
import os
import time
import flet as ft
from autoesprit import run_program
import threading
import traceback

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
            # Wichtig: Sicherstellen, dass das Fenster gezeichnet wird, bevor der Thread weiterläuft
            parent_tk_root.update_idletasks()
            parent_tk_root.update()


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

        # --- Tkinter Overlay spezifische Attribute ---
        self.tk_root_for_overlay = None
        self.red_dot_window_instance = None  # Umbenannt von red_dot_window, um Konflikt zu vermeiden
        self.overlay_thread = None
        self.shutdown_overlay_event = threading.Event()  # Event zum Signalisieren des Herunterfahrens

    def _bring_flet_window_to_front_windows(self):
        # ... ( bleibt gleich ) ...
        if not PYWIN32_AVAILABLE or os.name != 'nt': return False
        print(
            f"[FletThread {threading.get_ident()}] Versuche, Flet-Fenster mit Titel '{self.flet_window_title}' in den Vordergrund zu bringen...")
        try:
            hwnd = win32gui.FindWindow(None, self.flet_window_title)
            if hwnd:
                print(f"[FletThread {threading.get_ident()}] Fenster-Handle gefunden: {hwnd}")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE);
                win32gui.SetForegroundWindow(hwnd)
                print(f"[FletThread {threading.get_ident()}] SetForegroundWindow für HWND {hwnd} aufgerufen.")
                return True
            else:
                print(
                    f"[FletThread {threading.get_ident()}] Flet-Fenster mit Titel '{self.flet_window_title}' nicht gefunden.")
                return False
        except Exception as e_fg:
            print(
                f"[FletThread {threading.get_ident()}] Fehler beim Versuch, Fenster in Vordergrund zu bringen: {e_fg}");
            traceback.print_exc();
            return False

    def _run_tkinter_dot_thread(self, x, y, size):
        """Diese Funktion läuft im Tkinter-Overlay-Thread."""
        print(f"[TkinterThread {threading.get_ident()}] Tkinter-Thread gestartet.")
        try:
            self.tk_root_for_overlay = tk.Tk()
            self.tk_root_for_overlay.withdraw()
            self.red_dot_window_instance = RedDotOverlay(self.tk_root_for_overlay, x, y, size)

            # Event-Loop für das Overlay-Fenster
            while not self.shutdown_overlay_event.is_set():
                if self.red_dot_window_instance and self.red_dot_window_instance.winfo_exists():
                    self.tk_root_for_overlay.update_idletasks()
                    self.tk_root_for_overlay.update()
                else:  # Fenster wurde extern geschlossen oder existiert nicht mehr
                    break
                time.sleep(0.05)  # Reduziert CPU-Last

            print(
                f"[TkinterThread {threading.get_ident()}] Shutdown-Signal empfangen oder Fenster existiert nicht mehr.")

        except Exception as e_tk:
            print(f"[TkinterThread {threading.get_ident()}] Fehler im Tkinter-Thread: {e_tk}")
            traceback.print_exc()
        finally:
            # Aufräumen im Tkinter-Thread
            if self.red_dot_window_instance and self.red_dot_window_instance.winfo_exists():
                try:
                    self.red_dot_window_instance.destroy()
                    print(f"[TkinterThread {threading.get_ident()}] RedDotOverlay zerstört.")
                except Exception as e_destroy_dot:
                    print(
                        f"[TkinterThread {threading.get_ident()}] Fehler beim Zerstören von RedDotOverlay: {e_destroy_dot}")

            if self.tk_root_for_overlay:
                try:
                    self.tk_root_for_overlay.quit()  # Beendet die Tkinter-Hauptschleife sauber
                    # self.tk_root_for_overlay.destroy() # Zerstört das Haupt-Tk-Fenster
                    print(f"[TkinterThread {threading.get_ident()}] Tkinter-Root gequittet.")
                except Exception as e_quit_root:
                    print(
                        f"[TkinterThread {threading.get_ident()}] Fehler beim Quitten von Tkinter-Root: {e_quit_root}")

            self.red_dot_window_instance = None
            self.tk_root_for_overlay = None
            print(f"[TkinterThread {threading.get_ident()}] Tkinter-Thread beendet und Ressourcen freigegeben.")

    def _show_red_dot_overlay(self, x, y, size=20):
        if not TKINTER_AVAILABLE:
            print("[FletThread] Tkinter nicht verfügbar, kann roten Punkt nicht anzeigen.")
            return

        self.shutdown_overlay_event.clear()  # Stelle sicher, dass das Event nicht von vorherigen Aufrufen gesetzt ist

        if self.overlay_thread is None or not self.overlay_thread.is_alive():
            self.overlay_thread = threading.Thread(target=self._run_tkinter_dot_thread, args=(x, y, size), daemon=True)
            self.overlay_thread.start()
            print(f"[FletThread {threading.get_ident()}] Tkinter Overlay-Thread gestartet.")
        else:
            print(f"[FletThread {threading.get_ident()}] Tkinter Overlay-Thread läuft bereits.")

    def _close_red_dot_overlay(self):
        if not TKINTER_AVAILABLE:
            return

        current_thread_id = threading.get_ident()
        print(f"[FletThread {current_thread_id}] _close_red_dot_overlay aufgerufen.")

        if self.overlay_thread and self.overlay_thread.is_alive():
            print(f"[FletThread {current_thread_id}] Signalisiere Tkinter-Thread zum Beenden...")
            self.shutdown_overlay_event.set()  # Signal an den Tkinter-Thread senden
            # Warte kurz, damit der Tkinter-Thread Zeit hat, aufzuräumen
            # self.overlay_thread.join(timeout=1.0) # Optional: Warte auf Thread-Ende
            # if self.overlay_thread.is_alive():
            #     print(f"[FletThread {current_thread_id}] WARNUNG: Tkinter-Thread hat sich nicht innerhalb des Timeouts beendet.")
        else:
            print(f"[FletThread {current_thread_id}] Kein aktiver Tkinter-Overlay-Thread zum Schließen gefunden.")

        # Setze Referenzen zurück, falls der Thread nicht mehr läuft oder nicht gestartet wurde
        self.red_dot_window_instance = None
        self.tk_root_for_overlay = None

    def _handle_final_dialog_result(self, e, dialog_ref: ft.AlertDialog):
        # Diese Methode wird vom Flet-Hauptthread aufgerufen (durch Dialog-Event)
        current_thread_id = threading.get_ident()
        print(
            f"[FletThread {current_thread_id} - Dialog Event] _handle_final_dialog_result: Button '{e.control.text}' geklickt.")

        self._close_red_dot_overlay()  # Signalisiert dem Tkinter-Thread, sich zu beenden

        self.page.close(dialog_ref)
        self.active_dialog = None

        if e.control.data == "yes":
            print(f"[FletThread {current_thread_id}] Prozess wird fortgesetzt (Flet Dialog).")
            try:
                # ... (run_program Logik) ...
                length_str = self.length_field.value.replace(',', '.')
                width_str = self.width_field.value.replace(',', '.')
                height_str = self.height_field.value.replace(',', '.')
                length = float(length_str);
                width = float(width_str);
                height = float(height_str)
                run_program(length, width, height)
            except ValueError:
                self._show_dialog_from_thread(title="Eingabefehler", content="Ungültige Zahlenwerte.", is_error=True)
            except Exception as ex_run:
                self._show_dialog_from_thread(title="Fehler bei Fortsetzung", content=f"Fehler: {ex_run}",
                                              is_error=True)
        else:
            print(f"[FletThread {current_thread_id}] Aktion beendet oder Prozess abgebrochen.")

    def _show_dialog_from_thread(self, title: str, content: str, is_error: bool = False, show_dot: bool = False,
                                 dot_x=0, dot_y=0):
        # Diese Methode wird vom _perform_actions Thread aufgerufen
        worker_thread_id = threading.get_ident()
        print(
            f"[WorkerThread {worker_thread_id}] _show_dialog_from_thread - Titel: '{title}', IstFehler: {is_error}, ShowDot: {show_dot}")

        self._bring_flet_window_to_front_windows()
        time.sleep(0.2)  # Wichtig: Gib dem OS Zeit, den Fokus zu wechseln

        if show_dot:  # Dies ist der Erfolgsfall ("Pause!")
            self._show_red_dot_overlay(dot_x, dot_y)

        # Callback, der im Flet-Thread ausgeführt wird, um den Dialog zu öffnen
        def open_dialog_on_flet_thread():
            flet_thread_id = threading.get_ident()
            print(f"[FletThread {flet_thread_id}] open_dialog_on_flet_thread - Titel: '{title}'")

            dialog_actions = []
            dialog_to_show = ft.AlertDialog(
                modal=True,
                title=ft.Text(title),
                content=ft.Text(content),
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=lambda e: (
                    print(f"[FletThread {flet_thread_id} - Dialog Event] Dialog '{title}' abgewiesen (on_dismiss)!"),
                    self._close_red_dot_overlay()  # Roten Punkt auch bei dismiss schließen
                )
            )

            if is_error:
                dialog_actions.append(
                    ft.TextButton("OK",
                                  on_click=lambda e: (self._close_red_dot_overlay(), self.page.close(dialog_to_show)))
                )
            else:  # "Pause!" Dialog
                dialog_actions.extend([
                    ft.TextButton("Ja", on_click=lambda ev: self._handle_final_dialog_result(ev, dialog_to_show),
                                  data="yes"),
                    ft.TextButton("Nein", on_click=lambda ev: self._handle_final_dialog_result(ev, dialog_to_show),
                                  data="no"),
                ])
            dialog_to_show.actions = dialog_actions

            self.active_dialog = dialog_to_show
            self.page.open(dialog_to_show)
            print(f"[FletThread {flet_thread_id}] page.open({dialog_to_show.title.value}) aufgerufen.")

        # Führe das Öffnen des Dialogs im Flet-Hauptthread aus
        # Da page.open() bereits UI-Updates handhabt, sollte dies ausreichen.
        # Flet's page.update() ist thread-safe, und page.open() sollte dies auch sein.
        # Wenn nicht, wäre ein page.run_thread_safe(open_dialog_on_flet_thread) nötig,
        # aber das Attribut existiert nicht. Flet's Design zielt darauf ab, dass
        # Methoden wie page.add, page.open, page.update direkt aus Threads aufgerufen werden können.
        open_dialog_on_flet_thread()

    def _perform_actions(self):
        # ... (Aktionen 1-7) ...
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
                title="Pause!",
                content="Hallo Hannes, hab ich gute Arbeit geleistet? Soll ich noch weitere Aufgaben für dich übernehmen?",
                is_error=False,
                show_dot=True, dot_x=2205, dot_y=814
            )
        except pyautogui.FailSafeException:
            message = "Maus in Ecke (Fail-Safe)."
            print(f"[WorkerThread {worker_thread_id}] PyAutoGUI FailSafe: {message}")
            self._show_dialog_from_thread(title="Abbruch", content=message, is_error=True)
        except FileNotFoundError as fnf_err:
            message = f"Bild nicht gefunden:\n{fnf_err}"
            print(f"[WorkerThread {worker_thread_id}] FileNotFoundError: {message}")
            self._show_dialog_from_thread(title="Bild nicht gefunden", content=message, is_error=True)
        except Exception as e:
            message = f"Fehler in Automation:\n{e}"
            print(f"[WorkerThread {worker_thread_id}] Exception in _perform_actions:")
            traceback.print_exc()
            self._show_dialog_from_thread(title="Fehler im Ablauf", content=message, is_error=True)
        print(f"[WorkerThread {worker_thread_id}] _perform_actions beendet.")

    def kombiablauf(self):
        # ... (bleibt gleich) ...
        print("kombiablauf(): Starte Automations-Thread...")
        self.flet_window_title = self.page.title
        if not self.flet_window_title: self.flet_window_title = "Blank Maker Master 7.7 by Gschwendtner Johannes"
        action_thread = threading.Thread(target=self._perform_actions, daemon=True)
        action_thread.start()
        print("kombiablauf(): Automations-Thread gestartet.")

    # --- action_X Methoden und _locate_and_click bleiben unverändert ---
    def _locate_and_click(self, image_name, confidence, action_name, click_type="click", grayscale=False,
                          wait_before_click=0.1, wait_after_click=0.5):
        if not os.path.exists(image_name):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path_in_script_dir = os.path.join(script_dir, image_name)
            if os.path.exists(image_path_in_script_dir):
                image_to_find = image_path_in_script_dir
            else:
                raise FileNotFoundError(f"Bilddatei '{image_name}' für {action_name} nicht gefunden.")
        else:
            image_to_find = image_name
        image_position = pyscreeze.locateOnScreen(image_to_find, confidence=confidence, grayscale=grayscale)
        if image_position is None: raise Exception(
            f"Bild '{os.path.basename(image_to_find)}' für {action_name} nicht auf dem Bildschirm gefunden.")
        image_center = pyscreeze.center(image_position);
        time.sleep(wait_before_click)
        if click_type == "click":
            pyautogui.click(image_center)
        elif click_type == "doubleclick":
            pyautogui.doubleClick(image_center)
        time.sleep(wait_after_click)

    def action_1(self):
        print(f"[WorkerThread {threading.get_ident()}] A1"); self._locate_and_click('Bilder/1.png', 0.5, "A1",
                                                                                    wait_after_click=0.5); print(
            f"[WorkerThread {threading.get_ident()}] A1 ende")

    def action_2(self):
        print(f"[WorkerThread {threading.get_ident()}] A2"); self._locate_and_click('Bilder/2.png', 0.4, "A2",
                                                                                    wait_after_click=0.9); print(
            f"[WorkerThread {threading.get_ident()}] A2 ende")

    def action_3(self):
        print(f"[WorkerThread {threading.get_ident()}] A3"); self._locate_and_click('Bilder/3.png', 0.5, "A3 (Bild)",
                                                                                    click_type="doubleclick",
                                                                                    grayscale=True,
                                                                                    wait_after_click=0.4); time.sleep(
            0.2); pyautogui.press('delete'); time.sleep(0.1); pyautogui.typewrite(
            self.ctrl_v_field.value + '_A'); time.sleep(0.1); print(f"[WorkerThread {threading.get_ident()}] A3 ende")

    def action_4(self):
        print(f"[WorkerThread {threading.get_ident()}] A4"); pyautogui.press('tab', presses=2,
                                                                             interval=0.1); time.sleep(
            0.1); pyautogui.press('delete'); time.sleep(0.1); pyautogui.typewrite(self.ctrl_v_field.value); time.sleep(
            0.1); print(f"[WorkerThread {threading.get_ident()}] A4 ende")

    def action_5(self):
        print(f"[WorkerThread {threading.get_ident()}] A5"); pyautogui.press('tab'); time.sleep(0.1); pyautogui.hotkey(
            'ctrl', 'a'); pyautogui.press('delete'); time.sleep(
            0.1); text = self.selection_dropdown.value; assert text and text != "Option", "Gültigen Programmtyp auswählen für A5."; pyautogui.typewrite(
            text); time.sleep(0.1); print(f"[WorkerThread {threading.get_ident()}] A5 ende")

    def action_6(self):
        print(f"[WorkerThread {threading.get_ident()}] A6"); pyautogui.press('enter'); time.sleep(0.1); print(
            f"[WorkerThread {threading.get_ident()}] A6 ende")

    def action_7(self):
        print(f"[WorkerThread {threading.get_ident()}] A7");
        dest_folder = self.destination_field.value;
        assert dest_folder and os.path.isdir(dest_folder), f"Zielordner '{dest_folder}' ungültig/nicht existent für A7."
        rt = os.path.join(dest_folder, "!rohteil.dxf");
        ss = os.path.join(dest_folder, "!schraubstock.step");
        assert os.path.isfile(rt), f"Datei '{rt}' nicht gefunden für A7.";
        assert os.path.isfile(ss), f"Datei '{ss}' nicht gefunden für A7."
        pyautogui.doubleClick(974, 1047, duration=0.4);
        time.sleep(0.5);
        pyautogui.hotkey('ctrl', 'o');
        time.sleep(0.5);
        pyautogui.typewrite(rt);
        time.sleep(0.5);
        pyautogui.press('enter');
        time.sleep(1.0)
        pyautogui.doubleClick(977, 1142, duration=0.4);
        time.sleep(0.5);
        pyautogui.hotkey('ctrl', 'o');
        time.sleep(0.8);
        pyautogui.typewrite(ss);
        time.sleep(0.8);
        pyautogui.press('enter');
        time.sleep(1.0);
        print(f"[WorkerThread {threading.get_ident()}] A7 ende")