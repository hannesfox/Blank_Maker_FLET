import pyautogui
import pyscreeze
import os
import time
import flet as ft
import threading
import traceback
from pathlib import Path
IS_WINDOWS = os.name == 'nt'

# Import der Esprit Automationsfunktion
from .esprit_interactions import run_esprit_rohteil_definition_sequence  # Umbenannt aus run_program

# --- Plattformabhängige Importe für Fokus und Overlay ---
TKINTER_AVAILABLE = False
try:
    import tkinter as tk

    TKINTER_AVAILABLE = True
except ImportError:
    print("WARNUNG: Tkinter nicht verfügbar. Der rote Punkt kann nicht angezeigt werden.")

PYWIN32_AVAILABLE = False
if os.name == 'nt':
    try:
        import win32gui
        import win32con

        PYWIN32_AVAILABLE = True
    except ImportError:
        print("WARNUNG: pywin32 nicht installiert. Fokus kann nicht erzwungen werden.")

if TKINTER_AVAILABLE:
    class RedDotOverlay(tk.Toplevel):
        def __init__(self, parent_tk_root, x, y, size=10):
            super().__init__(parent_tk_root)
            self.overrideredirect(True)
            self.attributes("-topmost", True)
            self.attributes("-transparentcolor", "white")  # Farbe, die transparent wird
            self.attributes("-alpha", 0.8)  # Gesamttransparenz des Fensters
            self.geometry(f"{size}x{size}+{x - size // 2}+{y - size // 2}")

            self.canvas = tk.Canvas(self, width=size, height=size, bg="white", highlightthickness=0)
            self.canvas.pack()
            self.canvas.create_oval(0, 0, size, size, fill="red", outline="red")
            parent_tk_root.update_idletasks()  # Wichtig, damit das Fenster sofort gezeichnet wird
            parent_tk_root.update()


class KombiWorkflow:
    def __init__(self, page: ft.Page, ctrl_v_field: ft.TextField, selection_dropdown: ft.Dropdown,
                 destination_field: ft.TextField, length_field: ft.TextField,
                 width_field: ft.TextField, height_field: ft.TextField, images_base_path: Path):
        self.page = page
        self.ctrl_v_field = ctrl_v_field
        self.selection_dropdown = selection_dropdown
        self.destination_field = destination_field
        self.length_field = length_field
        self.width_field = width_field
        self.height_field = height_field
        self.images_base_path = images_base_path  # Pfad zum "Bilder" Ordner

        self.flet_window_title = page.title or "BlankMaker App"  # Fallback-Titel
        self.active_dialog_ref = None  # Referenz auf den aktuell offenen Flet-Dialog

        # Tkinter Overlay spezifische Attribute
        self.tk_root_for_overlay = None
        self.red_dot_window = None
        self.overlay_thread = None
        self.shutdown_overlay_event = threading.Event()

    def _get_image_path(self, image_name_with_ext) -> str:
        """Gibt den vollständigen Pfad zu einem Bild im Bilder-Ordner zurück."""
        path = self.images_base_path / image_name_with_ext
        if not path.exists():
            raise FileNotFoundError(f"Bilddatei nicht gefunden: {path}")
        return str(path)

    def _bring_flet_window_to_front(self):
        if not PYWIN32_AVAILABLE or os.name != 'nt':
            print("Info: pywin32 nicht verfügbar oder nicht Windows. Kann Fenster nicht in Vordergrund bringen.")
            return False

        print(f"Versuche, Flet-Fenster '{self.flet_window_title}' in den Vordergrund zu bringen...")
        try:
            hwnd = win32gui.FindWindow(None, self.flet_window_title)
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Fenster wiederherstellen, falls minimiert
                win32gui.SetForegroundWindow(hwnd)
                print(f"SetForegroundWindow für HWND {hwnd} aufgerufen.")
                time.sleep(0.1)  # Kurze Pause, damit das OS reagieren kann
                return True
            else:
                print(f"Flet-Fenster '{self.flet_window_title}' nicht gefunden.")
                return False
        except Exception as e:
            print(f"Fehler beim In-Vordergrund-Bringen des Fensters: {e}")
            traceback.print_exc()
            return False

    # --- Roter Punkt Overlay Methoden ---
    def _run_tkinter_dot_in_thread(self, x, y, size):
        """Diese Funktion läuft im Tkinter-Overlay-Thread."""
        print(f"[TkinterThread {threading.get_ident()}] Tkinter Overlay Thread gestartet.")
        try:
            self.tk_root_for_overlay = tk.Tk()
            self.tk_root_for_overlay.withdraw()  # Hauptfenster von Tkinter verstecken
            self.red_dot_window = RedDotOverlay(self.tk_root_for_overlay, x, y, size)

            while not self.shutdown_overlay_event.is_set():
                if self.red_dot_window and self.red_dot_window.winfo_exists():
                    self.tk_root_for_overlay.update_idletasks()
                    self.tk_root_for_overlay.update()
                else:
                    break  # Fenster wurde extern geschlossen oder existiert nicht mehr
                time.sleep(0.05)  # CPU-Last reduzieren

        except Exception as e_tk:
            print(f"[TkinterThread {threading.get_ident()}] Fehler im Tkinter Thread: {e_tk}")
            traceback.print_exc()
        finally:
            if self.red_dot_window and self.red_dot_window.winfo_exists():
                try:
                    self.red_dot_window.destroy()
                except:
                    pass
            if self.tk_root_for_overlay:
                try:
                    self.tk_root_for_overlay.quit()  # Sauberes Beenden der Tkinter-Schleife
                except:
                    pass
            self.red_dot_window = None
            self.tk_root_for_overlay = None
            print(f"[TkinterThread {threading.get_ident()}] Tkinter Overlay Thread beendet.")

    def _show_red_dot_overlay(self, x, y, size=20):
        if not TKINTER_AVAILABLE:
            print("Info: Tkinter nicht verfügbar, roter Punkt kann nicht angezeigt werden.")
            return

        self.shutdown_overlay_event.clear()  # Sicherstellen, dass Event nicht gesetzt ist
        if self.overlay_thread is None or not self.overlay_thread.is_alive():
            self.overlay_thread = threading.Thread(target=self._run_tkinter_dot_in_thread, args=(x, y, size),
                                                   daemon=True)
            self.overlay_thread.start()
        else:
            print("Info: Tkinter Overlay Thread läuft bereits.")

    def _close_red_dot_overlay(self):
        if not TKINTER_AVAILABLE or not self.overlay_thread or not self.overlay_thread.is_alive():
            return

        print("Signalisiere Tkinter Overlay Thread zum Beenden...")
        self.shutdown_overlay_event.set()
        # Optional: auf Thread warten, aber da er daemon=True ist, nicht zwingend
        # self.overlay_thread.join(timeout=1.0)
        # if self.overlay_thread.is_alive():
        # print("WARNUNG: Tkinter Overlay Thread hat sich nicht beendet.")

    # --- Flet Dialog Methoden (aufrufbar aus Worker Thread) ---
    def _close_current_flet_dialog(self):
        if self.active_dialog_ref and self.page.dialog == self.active_dialog_ref:
            self.page.close_dialog()
            # self.page.update() # close_dialog sollte update auslösen
            self.active_dialog_ref = None

    def _show_flet_dialog_from_thread(self, title: str, content_text: str, is_error: bool = False,
                                      is_confirmation: bool = False, dot_coords=None):
        """Zeigt einen Flet Dialog an. Muss sicherstellen, dass page.open im Flet UI Thread läuft."""

        self._bring_flet_window_to_front()  # Versuche Flet-Fenster nach vorne zu holen

        if dot_coords:
            self._show_red_dot_overlay(dot_coords[0], dot_coords[1])

        def _dialog_action(e=None):  # e ist optional, da on_dismiss kein e übergibt
            # Diese Funktion wird im Flet UI Thread ausgeführt
            self._close_red_dot_overlay()  # Roten Punkt schließen, wenn Dialog geschlossen/bestätigt wird

            # Dialog schließen
            if self.active_dialog_ref:
                self.page.close(self.active_dialog_ref)  # Nutze Referenz zum Schließen
                self.active_dialog_ref = None

            if e and hasattr(e, 'control') and e.control.data == "yes" and is_confirmation:
                print("Benutzer hat 'Ja' geklickt. Setze Esprit-Automatisierung fort.")
                try:
                    length = float(self.length_field.value.replace(',', '.'))
                    width = float(self.width_field.value.replace(',', '.'))
                    height = float(self.height_field.value.replace(',', '.'))
                    # Starte die Esprit Rohteil Definition (ehemals run_program)
                    # Dies ist eine blockierende PyAutoGUI-Sequenz.
                    # Sie sollte idealerweise auch in einem Thread laufen, wenn sie lange dauert.
                    # Fürs Erste direkt hier, da der Dialog bereits eine Pause war.
                    run_esprit_rohteil_definition_sequence(length, width, height, self.images_base_path)
                    self._show_flet_dialog_from_thread("Erfolg", "Rohteil in Esprit definiert.", is_error=False)

                except ValueError:
                    self._show_flet_dialog_from_thread("Eingabefehler", "Ungültige Zahlen für Maße.", is_error=True)
                except Exception as ex_run:
                    self._show_flet_dialog_from_thread("Fehler", f"Fehler bei Esprit Rohteil-Definition: {ex_run}",
                                                       is_error=True)
            elif e and hasattr(e, 'control') and e.control.data == "no" and is_confirmation:
                print("Benutzer hat 'Nein' geklickt. Breche weiteren Kombiablauf ab.")
                self._show_flet_dialog_from_thread("Info", "Kombiablauf abgebrochen.", is_error=False)

        # Definiere den Dialog, der im Flet UI Thread geöffnet werden soll
        def _open_dialog_on_flet_thread():
            self._close_current_flet_dialog()  # Schließe erst alten Dialog, falls offen

            dialog_actions = []
            if is_confirmation:
                dialog_actions = [
                    ft.TextButton("Ja", on_click=_dialog_action, data="yes"),
                    ft.TextButton("Nein", on_click=_dialog_action, data="no"),
                ]
            else:  # Nur OK-Button für Info/Fehler
                dialog_actions = [ft.TextButton("OK", on_click=_dialog_action)]

            new_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(title),
                content=ft.Text(content_text),
                actions=dialog_actions,
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=lambda _: (  # Wird aufgerufen, wenn außerhalb geklickt wird oder ESC
                    print(f"Dialog '{title}' abgewiesen (on_dismiss)."),
                    _dialog_action()  # Behandle dismiss wie einen Klick auf OK/Nein
                )
            )
            self.active_dialog_ref = new_dialog  # Speichere Referenz
            self.page.open(new_dialog)  # Flet's page.open ist thread-safe
            # self.page.update() # page.open sollte update auslösen

        # Führe das Öffnen des Dialogs im Flet-Hauptthread aus.
        # Flet's page.open() ist dafür gedacht, auch aus Threads aufgerufen zu werden.
        _open_dialog_on_flet_thread()

    # --- PyAutoGUI Aktionen ---
    def _locate_and_click(self, image_file_name, confidence, action_name, click_type="click", grayscale=False,
                          wait_before_click=0.1, wait_after_click=0.5, speed_factor=0.4):
        full_image_path = self._get_image_path(image_file_name)

        print(f"Suche Bild '{image_file_name}' für Aktion '{action_name}' (Pfad: {full_image_path})")
        image_position = pyscreeze.locateOnScreen(full_image_path, confidence=confidence, grayscale=grayscale)
        if image_position is None:
            raise Exception(f"Bild '{image_file_name}' für Aktion '{action_name}' nicht auf Bildschirm gefunden.")

        image_center = pyscreeze.center(image_position)
        time.sleep(wait_before_click * speed_factor)
        if click_type == "click":
            pyautogui.click(image_center)
        elif click_type == "doubleclick":
            pyautogui.doubleClick(image_center)
        time.sleep(wait_after_click * speed_factor)
        print(f"Aktion '{action_name}' ausgeführt.")

    def _action_1(self):
        self._locate_and_click('1.png', 0.5, "Dialog Öffnen")

    def _action_2(self):
        self._locate_and_click('2.png', 0.4, "Neues Projekt")

    def _action_3(self):  # Programmname A-Seite
        self._locate_and_click('3.png', 0.5, "Feld Programmname", click_type="doubleclick", grayscale=True,
                               wait_after_click=0.2)
        pyautogui.press('delete');
        time.sleep(0.1 * 0.4)
        pyautogui.typewrite(self.ctrl_v_field.value + '_A');
        time.sleep(0.1 * 0.4)

    def _action_4(self):  # Programmname
        pyautogui.press('tab', presses=2, interval=0.1 * 0.4);
        time.sleep(0.1 * 0.4)
        pyautogui.press('delete');
        time.sleep(0.1 * 0.4)
        pyautogui.typewrite(self.ctrl_v_field.value);
        time.sleep(0.1 * 0.4)

    def _action_5(self):  # Maschinentyp
        pyautogui.press('tab');
        time.sleep(0.1 * 0.4)
        pyautogui.hotkey('ctrl', 'a');
        pyautogui.press('delete');
        time.sleep(0.1 * 0.4)
        machine_type_text = self.selection_dropdown.value
        if not machine_type_text or machine_type_text == "Option":
            raise ValueError("Gültiger Maschinentyp muss in Dropdown ausgewählt sein.")
        pyautogui.typewrite(machine_type_text);
        time.sleep(0.1 * 0.4)

    def _action_6(self):
        pyautogui.press('enter'); time.sleep(0.1 * 0.4)  # Bestätigen

    def _action_7(self):  # Dateien laden
        worker_id = f"[WorkerThread {threading.get_ident()}]"
        print(f"{worker_id} A7: Starte Laden von Dateien")

        # 1. Hole den Basis-Zielordner-String aus dem Flet-Feld
        base_dest_folder_from_flet = self.destination_field.value
        if not base_dest_folder_from_flet:
            raise ValueError("Zielordner-String (destination_field.value) ist leer.")
        base_dest_folder_from_flet = str(base_dest_folder_from_flet)  # Sicherstellen, dass es ein String ist
        print(f"{worker_id} A7_STEP_1: Basis-Zielordner aus Flet-Feld: '{base_dest_folder_from_flet}'")

        # 2. Überprüfe, ob dieser Basisordner existiert (mit pathlib)
        if not Path(base_dest_folder_from_flet).is_dir():
            raise ValueError(f"Basis-Zielordner '{base_dest_folder_from_flet}' ist ungültig oder nicht existent.")
        print(f"{worker_id} A7_STEP_2: Basis-Zielordner '{base_dest_folder_from_flet}' existiert als Verzeichnis.")

        # Dateinamen
        rohteil_filename = "!rohteil.dxf"
        schraubstock_filename = "!schraubstock.step"

        # --- Rohteil Pfadkonstruktion und Überprüfung ---
        print(f"{worker_id} --- ROHTEIL START ---")
        # 3a. Konstruiere den Rohteil-Pfad mit os.path.join
        rohteil_path_str_constructed = os.path.join(base_dest_folder_from_flet, rohteil_filename)
        print(
            f"{worker_id} A7_STEP_3a (Rohteil): Konstruierter Pfad mit os.path.join: '{rohteil_path_str_constructed}'")

        # 4a. Überprüfe, ob die Rohteil-Datei existiert (mit pathlib auf dem konstruierten String)
        if not Path(rohteil_path_str_constructed).is_file():
            raise FileNotFoundError(f"Rohteil-Datei '{rohteil_path_str_constructed}' nicht gefunden.")
        print(f"{worker_id} A7_STEP_4a (Rohteil): Datei '{rohteil_path_str_constructed}' existiert.")
        print(f"{worker_id} --- ROHTEIL ENDE ---")

        # --- Schraubstock Pfadkonstruktion und Überprüfung ---
        print(f"{worker_id} --- SCHRAUBSTOCK START ---")
        # 3b. Konstruiere den Schraubstock-Pfad mit os.path.join
        schraubstock_path_str_constructed = os.path.join(base_dest_folder_from_flet, schraubstock_filename)
        print(
            f"{worker_id} A7_STEP_3b (Schraubstock): Konstruierter Pfad mit os.path.join: '{schraubstock_path_str_constructed}'")

        # 4b. Überprüfe, ob die Schraubstock-Datei existiert (mit pathlib auf dem konstruierten String)
        if not Path(schraubstock_path_str_constructed).is_file():
            raise FileNotFoundError(f"Schraubstock-Datei '{schraubstock_path_str_constructed}' nicht gefunden.")
        print(f"{worker_id} A7_STEP_4b (Schraubstock): Datei '{schraubstock_path_str_constructed}' existiert.")
        print(f"{worker_id} --- SCHRAUBSTOCK ENDE ---")

        speed = 0.4  # Dein Speed-Faktor

        # --- Rohteil laden in Esprit ---
        print(f"{worker_id} Lade Rohteil in Esprit. Pfad für typewrite: \"{rohteil_path_str_constructed}\"")
        pyautogui.doubleClick(974, 1047, duration=0.4 * speed)
        time.sleep(0.5 * speed)
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(0.5 * speed)
        pyautogui.typewrite(f'"{rohteil_path_str_constructed}"')  # In Anführungszeichen
        time.sleep(0.5 * speed)
        pyautogui.press('enter')
        time.sleep(1.0 * speed)
        print(f"{worker_id} Rohteil-Laden an Esprit gesendet.")

        # --- Schraubstock laden in Esprit ---
        print(f"{worker_id} Lade Schraubstock in Esprit. Pfad für typewrite: \"{schraubstock_path_str_constructed}\"")
        pyautogui.doubleClick(977, 1142, duration=0.4 * speed)
        time.sleep(0.5 * speed)
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(1.2 * speed)
        pyautogui.typewrite(f'"{schraubstock_path_str_constructed}"')  # In Anführungszeichen
        time.sleep(1.8 * speed)
        pyautogui.press('enter')
        time.sleep(1.0 * speed)

        print(f"{worker_id} Schraubstock-Laden an Esprit gesendet.")
        print(f"{worker_id} A7: Dateien sollten geladen sein.")

    def _perform_automation_sequence(self):
        """Führt die blockierenden PyAutoGUI-Aktionen aus."""
        worker_thread_id = threading.get_ident()
        print(f"[WorkerThread {worker_thread_id}] Kombiablauf Automationssequenz gestartet.")
        try:
            # Validierungen vorab
            if not self.ctrl_v_field.value: raise ValueError("Programmname (CTRL+V Feld) darf nicht leer sein.")
            if not self.selection_dropdown.value or self.selection_dropdown.value == "Option":
                raise ValueError("Gültiger Maschinentyp muss ausgewählt sein.")
            if not self.destination_field.value or not Path(self.destination_field.value).is_dir():
                raise ValueError("Gültiger Zielordner muss angegeben sein.")
            # Maße für run_esprit_rohteil_definition_sequence werden später validiert

            time.sleep(0.5)  # Kurze Pause bevor es losgeht
            self._action_1()
            time.sleep(0.5)
            self._action_2()
            time.sleep(0.5)
            self._action_3()
            self._action_4()
            self._action_5()
            self._action_6()
            self._action_7()  # Lädt Rohteil.dxf und Schraubstock.step

            print(f"[WorkerThread {worker_thread_id}] Vorbereitende Aktionen erfolgreich.")
            time.sleep(0.5)
            # Nach erfolgreichem Laden der Dateien, zeige den Bestätigungsdialog
            self._show_flet_dialog_from_thread(
                title="Pause & Bestätigung",
                content_text="Dateien geladen.\nSoll nun das Rohteil in Esprit definiert werden?",
                is_confirmation=True,
                dot_coords=(2205, 814)  # Koordinaten für den roten Punkt
            )

        except pyautogui.FailSafeException:
            msg = "Maus in Ecke bewegt (Fail-Safe). Kombiablauf abgebrochen."
            print(f"[WorkerThread {worker_thread_id}] PyAutoGUI FailSafe: {msg}")
            self._show_flet_dialog_from_thread("Abbruch (Fail-Safe)", msg, is_error=True)
        except FileNotFoundError as fnf_err:
            msg = f"Ein benötigtes Bild wurde nicht gefunden:\n{fnf_err}\nKombiablauf abgebrochen."
            print(f"[WorkerThread {worker_thread_id}] FileNotFoundError: {msg}")
            self._show_flet_dialog_from_thread("Bild nicht gefunden", msg, is_error=True)
        except ValueError as val_err:  # Für eigene Validierungsfehler
            msg = f"Ungültige Eingabe:\n{val_err}\nKombiablauf abgebrochen."
            print(f"[WorkerThread {worker_thread_id}] ValueError: {msg}")
            self._show_flet_dialog_from_thread("Ungültige Eingabe", msg, is_error=True)
        except Exception as e:
            msg = f"Ein unerwarteter Fehler ist im Kombiablauf aufgetreten:\n{e}"
            print(f"[WorkerThread {worker_thread_id}] Exception in Kombiablauf:")
            traceback.print_exc()
            self._show_flet_dialog_from_thread("Fehler im Kombiablauf", msg, is_error=True)

        print(f"[WorkerThread {worker_thread_id}] Kombiablauf Automationssequenz (bis zum Dialog) beendet.")

    def start_automation(self):
        """Startet die gesamte Kombiablauf-Automatisierung in einem neuen Thread."""
        print("KombiWorkflow: Starte Automations-Thread...")

        # Sicherstellen, dass der Fenstertitel aktuell ist
        current_flet_title = self.page.title
        if current_flet_title: self.flet_window_title = current_flet_title

        action_thread = threading.Thread(target=self._perform_automation_sequence, daemon=True)
        action_thread.start()
        print("KombiWorkflow: Automations-Thread gestartet.")