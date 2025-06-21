#event_handlers.py
import flet as ft
import shutil
import os
import asyncio
import subprocess
import datetime
import glob
import re
from pathlib import Path

import config # Globale Pfade
# Annahme: Diese Module sind im selben Projektverzeichnis vorhanden und funktionsfähig.
from program1 import create_rectangle
from program2 import create_circle
# from autoesprit import run_program # Wird anscheinend nicht direkt hier genutzt
from bseite import start_mausbewegungen
# from rohteilrechner import process_step_file # Wird anscheinend nicht direkt hier genutzt
from kombiablauf import Kombiablauf
# import actions # Wird anscheinend nicht direkt hier genutzt

class EventHandlersBase:
    # Beachten Sie: self wird hier die Instanz von BlankMakerApp sein,
    # die von dieser Klasse erbt.
    # Alle UI-Elemente (z.B. self.length_field) und self.page werden in BlankMakerApp.__init__ gesetzt.

    def get_daily_folder_path(self) -> Path:
        """Ermittelt den Pfad für den aktuellen Wochentag. Wird von __init__ der Hauptapp verwendet."""
        # Diese Funktion ist identisch zur config-Version, könnte auch von dort importiert werden,
        # aber hier belassen, falls spezifische Logik benötigt wird oder um Redundanz zu vermeiden,
        # wenn config.BASE_PATH4 bereits das Richtige tut. Für Konsistenz nutzen wir config.
        return config.get_daily_folder_path_config()


    # --- Asynchrone Event-Handler und UI-Updaters ---
    async def run_task_with_progress(self, e, button: ft.ElevatedButton, progress_bar: ft.ProgressBar, task_function):
        button.disabled = True
        progress_bar.visible = True
        progress_bar.value = None
        self.page.update()
        await asyncio.sleep(0.5)
        try:
            task_function(e) # e wird übergeben, falls task_function es benötigt
            progress_bar.color = ft.Colors.GREEN
            progress_bar.value = 1
            self.page.update()
            await asyncio.sleep(1)
        except Exception as ex:
            progress_bar.color = ft.Colors.RED
            progress_bar.value = 1
            self.page.update()
            await asyncio.sleep(1.5)
            self.show_dialog("Fehler bei der Ausführung", str(ex))
        finally:
            progress_bar.visible = False
            progress_bar.color = None
            progress_bar.value = None
            button.disabled = False
            self.page.update()

    async def handle_rect_creation(self, e):
        await self.run_task_with_progress(e, self.rect_make_button, self.rect_progress, self.create_rect)

    async def handle_circle_creation(self, e):
        await self.run_task_with_progress(e, self.circle_make_button, self.circle_progress, self.create_circle)

    async def handle_vice_creation(self, e):
        await self.run_task_with_progress(e, self.vice_create_button, self.vice_progress, self.copy_file)

    async def animate_and_move_files(self, e):
        self.export_button.disabled = True
        self.export_button.bgcolor = ft.Colors.GREEN_600
        self.page.update()
        await asyncio.sleep(0.2)
        self.move_files(e)
        self.export_button.bgcolor = ft.Colors.RED_600
        self.export_button.disabled = False
        self.page.update()

    async def continuously_check_dxf_files(self):
        while True:
            self.check_dxf_files()
            await asyncio.sleep(5)

    async def monitor_process(self, process, on_stop_callback):
        while process is not None:
            if process.poll() is not None:
                on_stop_callback()
                break
            await asyncio.sleep(1)

    # --- Synchrone Event-Handler und Logikfunktionen ---
    def on_width_change(self, e):
        self.update_value_entry()
        self.update_folder_selection(e)

    def toggle_value(self, e):
        self.at_prefix_field.value = "24" if self.at_prefix_field.value == "25" else "25"
        self.page.update()

    def start_kombiablauf(self, e):
        kombi = Kombiablauf(self.page, self.ctrl_v_field, self.selection_dropdown, self.destination_field,
                            self.length_field, self.width_field, self.height_field)
        try:
            kombi.kombiablauf()
        except Exception as ex:
            self.show_dialog("Fehler Kombiablauf", f"Startfehler im Kombiablauf: {ex}")

    def on_entry_change(self, e):
        if self.updating: return
        new_value = self.project_name_field.value
        if len(new_value) > 4:
            self.updating = True
            self.project_name_field.value = new_value[:4]
            self.page.update()
            self.updating = False
        if not new_value.isdigit() and new_value:
            self.show_dialog("Ungültige Eingabe", "Bitte geben Sie nur Zahlen ein.")
            self.updating = True
            self.project_name_field.value = self.current_value
            self.page.update()
            self.updating = False
            return
        if new_value != self.current_value:
            if self.current_value:
                self.history.append(self.current_value)
                self.back_button.disabled = False
            self.current_value = new_value
            self.page.update()

    def go_back(self, e):
        if self.history:
            previous_value = self.history.pop()
            self.updating = True
            self.project_name_field.value = previous_value
            self.current_value = previous_value
            self.updating = False
            self.back_button.disabled = not self.history
            self.page.update()

    def create_rect(self, e): # e Parameter hinzugefügt, da run_task_with_progress es übergibt
        try:
            length = float(self.length_field.value)
            width = float(self.width_field.value)
            height = float(self.height_field.value)
            create_rectangle(length, width, height)
            shutil.copy("!rohteil.dxf", self.destination_field.value)
        except (ValueError, TypeError):
            raise ValueError("Ungültige Eingabe für Rechteck-Maße. Bitte Zahlen eingeben.")
        except Exception as ex:
            raise IOError(f"Fehler beim Erstellen/Kopieren des Rechtecks: {ex}")

    def create_circle(self, e): # e Parameter hinzugefügt
        try:
            diameter = float(self.diameter_field.value)
            height = float(self.height2_field.value)
            create_circle(diameter, height)
            shutil.copy("!rohteil.dxf", self.destination_field.value)
        except (ValueError, TypeError):
            raise ValueError("Ungültige Eingabe für Kreis-Maße. Bitte Zahlen eingeben.")
        except Exception as ex:
            raise IOError(f"Fehler beim Erstellen/Kopieren des Kreises: {ex}")

    def get_folder_options(self):
        try:
            # Verwende config.BASE_PATH1
            folders = [d.name for d in config.BASE_PATH1.iterdir() if d.is_dir()]
            folders.sort(key=lambda name: int(name.split("_")[0]))
            return folders
        except (FileNotFoundError, IndexError, ValueError):
            self.show_dialog("Fehler", f"Konnte Ordneroptionen von {config.BASE_PATH1} nicht laden.")
            return []

    def copy_file(self, e): # e Parameter hinzugefügt
        try:
            folder_name = self.folder_dropdown.value
            value = self.value_field.value
            if not folder_name or not value:
                raise ValueError("Ordner oder Wert nicht ausgewählt.")

            source_folder = config.BASE_PATH1 / folder_name
            destination_folder = Path(self.destination_field.value)
            destination_folder.mkdir(parents=True, exist_ok=True) # Stelle sicher, dass Zielordner existiert

            found = False
            for file_path in source_folder.iterdir(): # Geändert zu file_path für Klarheit
                if (file_path.suffix.lower() == ".step" and re.search(r"\b{}\b".format(value),
                                                                 file_path.name)) or file_path.suffix.lower() == ".dxf":
                    shutil.copy2(file_path,
                                 destination_folder / f"!schraubstock{file_path.suffix}" if file_path.suffix.lower() == ".step" else destination_folder / file_path.name)
                    found = True
            if not found:
                self.show_dialog("Info", f"Keine passende Datei für Wert '{value}' in '{source_folder}' gefunden.")

        except Exception as ex:
            raise IOError(f"Fehler beim Kopieren der Datei: {ex}")

    def move_files(self, e):
        at_prefix = self.at_prefix_field.value
        project_name = self.project_name_field.value
        if not at_prefix or not project_name:
            self.status_label.value = "Fehler: AT-Präfix oder Projektname fehlt!"
            self.status_label.color = ft.Colors.RED_600
            self.page.update()
            return

        machines = ["HERMLE-C40", "HERMLE-C400", "DMU-EVO60", "DMU-100EVO", "DMC650V", "DMC1035V"]
        moved_count = 0
        for machine in machines:
            source_dir = config.BASE_PATH2 / machine / config.BASE_PATH3
            if not source_dir.exists(): continue

            destination_dir = config.BASE_PATH2 / machine / f"AT{at_prefix}-{project_name}"
            destination_dir.mkdir(exist_ok=True)

            for file_path in source_dir.glob("*.H"):
                try:
                    shutil.move(str(file_path), str(destination_dir / file_path.name))
                    moved_count += 1
                except Exception as ex_move:
                    self.show_dialog("Fehler beim Verschieben", f"Konnte {file_path.name} nicht verschieben: {ex_move}")


        if moved_count > 0:
            self.status_label.value = f"{moved_count} Programme verschoben!" # Status Label aktualisiert
            self.status_label.color = ft.Colors.GREEN_600
        else:
            self.status_label.value = "Keine .H-Dateien zum Verschieben gefunden."
            self.status_label.color = ft.Colors.ORANGE_400
        self.page.update()

    def check_dxf_files(self):
        machines = ["HERMLE-C40", "HERMLE-C400", "DMU-EVO60", "DMU-100EVO", "DMC650V", "DMC1035V"]
        h_files_count = 0
        for machine in machines:
            machine_path = config.BASE_PATH2 / machine / config.BASE_PATH3
            if machine_path.exists():
                 h_files_count += sum(1 for _ in machine_path.glob("*.H"))


        self.dxf_status_container.controls.clear()
        if h_files_count > 0:
            for _ in range(h_files_count):
                self.dxf_status_container.controls.append(
                    ft.Icon(name=ft.Icons.CHECK_CIRCLE_OUTLINED, color=ft.Colors.GREEN_600, size=20)
                )
        else:
            self.dxf_status_container.controls.append(
                ft.Icon(name=ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED_600, size=16)
            )
            self.dxf_status_container.controls.append(
                ft.Text("Keine Programme", color=ft.Colors.RED_600, size=12, weight=ft.FontWeight.BOLD)
            )
        self.page.update()

    def run_python_script(self, e):
        if self.script_process and self.script_process.poll() is None:
            self.show_dialog("Info", "Prozess läuft bereits!")
            return
        try:
            self.script_process = subprocess.Popen(["python", config.BASE_PATH5], creationflags=subprocess.CREATE_NO_WINDOW)
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.status_icon.color = ft.Colors.GREEN_600
            self.status_text.value = "Läuft"
            self.status_text.color = ft.Colors.GREEN_600
            self.page.update()
            self.page.run_task(self.monitor_process, self.script_process, self.reset_ui_to_stopped)
        except Exception as ex:
            self.show_dialog("Fehler", f"Fehler beim Starten des Skripts: {ex}")
            self.reset_ui_to_stopped() # UI zurücksetzen, falls Start fehlschlägt

    def kill_python_script(self, e):
        if self.script_process and self.script_process.poll() is None:
            self.script_process.terminate()
            try:
                self.script_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.script_process.kill()
        self.script_process = None
        self.reset_ui_to_stopped()

    def reset_ui_to_stopped(self):
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.status_icon.color = ft.Colors.RED_600
        self.status_text.value = "Gestoppt"
        self.status_text.color = ft.Colors.RED_600
        self.page.update()

    def start_external_flet_app(self, e):
        if self.external_flet_process and self.external_flet_process.poll() is None:
            self.show_dialog("Info", "Externe Flet App läuft bereits!")
            return
        try:
            self.external_flet_process = subprocess.Popen(["python", config.PATH_TO_EXTERNAL_FLET_APP], creationflags=subprocess.CREATE_NO_WINDOW)
            self.start_external_flet_button.disabled = True
            self.stop_external_flet_button.disabled = False
            self.external_flet_status_text.value = "Externe Flet App: Läuft"
            self.external_flet_status_text.color = ft.Colors.GREEN_700
            self.page.update()
            self.page.run_task(self.monitor_process, self.external_flet_process, self.reset_external_flet_ui_to_stopped)
        except Exception as ex:
            self.show_dialog("Fehler", f"Fehler beim Starten der externen Flet App: {ex}")
            self.reset_external_flet_ui_to_stopped()

    def stop_external_flet_app(self, e):
        if self.external_flet_process and self.external_flet_process.poll() is None:
            self.external_flet_process.terminate()
            try:
                self.external_flet_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.external_flet_process.kill()
        self.external_flet_process = None
        self.reset_external_flet_ui_to_stopped()

    def reset_external_flet_ui_to_stopped(self):
        self.start_external_flet_button.disabled = False
        self.stop_external_flet_button.disabled = True
        self.external_flet_status_text.value = "Externe Flet App: Gestoppt"
        self.external_flet_status_text.color = "onsurfacevariant"
        self.page.update()

    def start_bseite(self, e):
        try:
            partheight_str = self.blength_field.value.replace(',', '.')
            if not partheight_str: # Prüfen ob Feld leer ist
                self.show_dialog("Fehler", "Fertigteilhöhe darf nicht leer sein.")
                return
            partheight = float(partheight_str)
            start_mausbewegungen(self.page, partheight)
        except ValueError: # Spezifischer Fehler für ungültige Zahl
            self.show_dialog("Fehler", "Ungültige Eingabe für Fertigteilhöhe. Bitte eine Zahl eingeben.")
        except Exception as ex:
            self.show_dialog("Fehler", f"Fehler beim Starten der B-Seite: {ex}")


    def update_dimensions_from_input(self, e):
        parts = self.maße_field.value.replace(',', '.').split('*')
        if len(parts) == 3:
            try:
                length, width, height = parts[2].strip(), parts[0].strip(), parts[1].strip() # strip() entfernt Leerzeichen
                self.length_field.value = str(float(length))
                self.width_field.value = str(float(width))
                self.height_field.value = str(float(height))
                self.value_field.value = str(float(width)) # value_field auf Breite setzen
                self.update_folder_selection() # folder selection aktualisieren
                self.page.update()
            except ValueError:
                self.show_dialog("Fehler", "Ungültige Eingabe in Rohteil Maße. Format: B*H*L (Zahlen).")


    def update_folder_selection(self, e=None):
        try:
            length_str = self.length_field.value.replace(',', '.')
            width_str = self.width_field.value.replace(',', '.')
            length = float(length_str) if length_str else 0
            width = float(width_str) if width_str else 0
        except ValueError:
            # Optional: Dialog anzeigen oder einfach ignorieren
            # self.show_dialog("Info", "Bitte gültige Zahlen für Länge/Breite eingeben für automatische Ordnerwahl.")
            return

        selection = self.selection_dropdown.value
        folder_name = None
        # Logik für Ordnerauswahl...
        if selection in ['5 Achs  3 Achs', '5 Achs  5 Achs', '5 Achs']:
            if length <= 50 and 10 <= width <= 60: folder_name = '03_Präger_MINI'
            elif 50 < length <= 80 and 10 <= width <= 130: folder_name = '02_Präger_77'
            elif 80 < length <= 155 and 10 <= width <= 360: folder_name = '01_Präger_125'
            elif 155 < length <= 350 and 10 <= width <= 360: folder_name = '04_Dopppelpräger_125'
            elif 130 < length <= 250 and 10 <= width <= 130: folder_name = '05_Dopppelpräger_77'
        elif selection in ['3 Achs  3 Achs', '3 Achs']:
            if length <= 130: folder_name = '01_Präger_125'
            elif 130 < length <= 360: folder_name = '04_Dopppelpräger_125'

        if folder_name and folder_name in self.folder_options:
            self.folder_dropdown.value = folder_name
        # Falls kein passender Ordner, Wert nicht ändern oder auf None/Default setzen
        # else:
        # self.folder_dropdown.value = None # Oder einen Standardwert
        self.page.update()

    def update_value_entry(self):
        if self.width_field.value:
            try:
                # Sicherstellen, dass es eine gültige Zahl ist, bevor es zugewiesen wird
                width_val = float(self.width_field.value.replace(',', '.'))
                self.value_field.value = str(width_val) # Als String zurückgeben
                self.page.update()
            except ValueError:
                # Optional: Fehlerbehandlung, falls Breite keine Zahl ist
                pass


    def show_dialog(self, title, message):
        # Diese Methode ist Teil der App-Klasse und hat Zugriff auf self.page
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: self.close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self, dialog):
        # Diese Methode ist Teil der App-Klasse
        dialog.open = False
        self.page.update()