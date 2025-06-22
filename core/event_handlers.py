import flet as ft
import asyncio
import re
from pathlib import Path

# Lokale Projektimporte (angepasst an neue Struktur)
import config
from .file_operations import (
    create_rectangle_file,
    create_circle_file,
    copy_vice_files,
    move_program_files
)
from .automation.process_management import (
    run_script_async,
    kill_script_async
    # monitor_process_async wird intern von run_script_async verwendet
)
from .automation.kombi_workflow import KombiWorkflow
from .automation.esprit_interactions import start_bseite_automation_threaded


class EventHandlersBase:
    # self ist die Instanz von BlankMakerApp

    def __init__(self):
        # Wird verwendet, um eine Referenz auf den aktuell von dieser Klasse
        # geöffneten Dialog zu halten.
        self._active_dialog_instance = None
        # Prozessreferenzen initialisieren (werden von process_management.py gesetzt/zurückgesetzt)
        # self.script_process = None # Wird in BlankMakerApp initialisiert
        # self.external_flet_process = None # Wird in BlankMakerApp initialisiert
        pass

    # --- Asynchrone Hilfsfunktionen für UI-Updates ---
    async def _run_task_with_progress(self, e, button: ft.ElevatedButton, progress_bar: ft.ProgressBar,
                                      task_function_sync, *args):
        button.disabled = True
        progress_bar.visible = True
        progress_bar.value = None  # Indeterminate
        self.page.update()
        await asyncio.sleep(0.1)

        try:
            task_function_sync(*args)  # Direkter Aufruf der synchronen Funktion
            progress_bar.color = ft.Colors.GREEN
            progress_bar.value = 1  # Complete
        except Exception as ex:
            progress_bar.color = ft.Colors.RED
            progress_bar.value = 1  # Complete (aber mit Fehler)
            self.show_dialog("Fehler bei Ausführung", f"{ex}")  # Nutzt die korrigierte show_dialog
        finally:
            self.page.update()
            await asyncio.sleep(1 if progress_bar.color == ft.Colors.GREEN else 1.5)
            progress_bar.visible = False
            progress_bar.color = None
            progress_bar.value = None
            button.disabled = False
            self.page.update()

    # --- UI-Interaktionsmethoden (meist asynchron für Progress Bars) ---
    async def handle_rect_creation(self, e):
        try:
            length_str = self.length_field.value.replace(',', '.')
            width_str = self.width_field.value.replace(',', '.')
            height_str = self.height_field.value.replace(',', '.')

            if not length_str or not width_str or not height_str:
                self.show_dialog("Eingabefehler", "Alle Maße für das Rechteck müssen ausgefüllt sein.")
                return

            length = float(length_str)
            width = float(width_str)
            height = float(height_str)
            destination_folder = Path(self.destination_field.value)
            await self._run_task_with_progress(e, self.rect_make_button, self.rect_progress,
                                               create_rectangle_file, length, width, height, destination_folder)
        except ValueError:
            self.show_dialog("Eingabefehler", "Ungültige Zahlen für Rechteck-Maße.")
        except Exception as ex:
            self.show_dialog("Fehler", f"Unerwarteter Fehler bei Rechteckerstellung: {ex}")

    async def handle_circle_creation(self, e):
        try:
            diameter_str = self.diameter_field.value.replace(',', '.')
            height_str = self.height2_field.value.replace(',', '.')

            if not diameter_str or not height_str:
                self.show_dialog("Eingabefehler", "Durchmesser und Höhe für den Kreis müssen ausgefüllt sein.")
                return

            diameter = float(diameter_str)
            height = float(height_str)
            destination_folder = Path(self.destination_field.value)
            await self._run_task_with_progress(e, self.circle_make_button, self.circle_progress,
                                               create_circle_file, diameter, height, destination_folder)
        except ValueError:
            self.show_dialog("Eingabefehler", "Ungültige Zahlen für Kreis-Maße.")
        except Exception as ex:
            self.show_dialog("Fehler", f"Unerwarteter Fehler bei Kreiserstellung: {ex}")

    async def handle_vice_creation(self, e):
        try:
            folder_name = self.folder_dropdown.value
            value_str = self.value_field.value.replace(',', '.')

            if not folder_name:
                self.show_dialog("Eingabefehler", "Kein Ordner für Schraubstock ausgewählt.")
                return
            if not value_str:
                self.show_dialog("Eingabefehler", "Kein Wert (Breite) für Schraubstockauswahl eingegeben.")
                return

            destination_folder = Path(self.destination_field.value)
            # show_dialog wird als Callback an copy_vice_files übergeben
            await self._run_task_with_progress(e, self.vice_create_button, self.vice_progress,
                                               copy_vice_files, folder_name, value_str, destination_folder,
                                               self.show_dialog)
        except ValueError:  # Sollte durch Prüfungen oben abgefangen werden, aber als Fallback
            self.show_dialog("Eingabefehler", "Ungültiger Wert für Schraubstock.")
        except Exception as ex:
            self.show_dialog("Fehler", f"Unerwarteter Fehler bei Schraubstockerstellung: {ex}")

    async def animate_and_move_files(self, e):
        self.export_button.disabled = True
        original_bgcolor = self.export_button.style.bgcolor if self.export_button.style else ft.Colors.RED_600  # Fallback

        # Sicherstellen, dass ein Style-Objekt existiert
        if not self.export_button.style:
            self.export_button.style = ft.ButtonStyle()
        self.export_button.style.bgcolor = ft.Colors.GREEN_600
        self.export_button.update()

        await asyncio.sleep(0.2)
        try:
            at_prefix = self.at_prefix_field.value
            project_name = self.project_name_field.value
            if not at_prefix or not project_name:
                self.status_label.value = "Fehler: AT-Präfix oder Projektname fehlt!"
                self.status_label.color = ft.Colors.RED_600
                self.page.update()
                return  # Frühzeitiger Ausstieg

            moved_count = move_program_files(at_prefix, project_name, self.show_dialog)

            if moved_count > 0:
                self.status_label.value = f"{moved_count} Programme verschoben!"
                self.status_label.color = ft.Colors.GREEN_600
            else:
                self.status_label.value = "Keine .H-Dateien zum Verschieben gefunden."
                self.status_label.color = ft.Colors.ORANGE_400
            self.page.update()

        except Exception as ex:
            self.show_dialog("Fehler beim Verschieben", f"Ein Fehler ist aufgetreten: {ex}")
            self.status_label.value = "Fehler beim Verschieben!"
            self.status_label.color = ft.Colors.RED_600
            self.page.update()
        finally:
            await asyncio.sleep(1.5 if self.status_label.color == ft.Colors.GREEN_600 else 0.5)
            if self.export_button.style:  # Nur zugreifen, wenn Style existiert
                self.export_button.style.bgcolor = original_bgcolor
            self.export_button.disabled = False
            self.export_button.update()

    async def continuously_check_dxf_files(self):
        while True:
            self.check_dxf_files_status()
            await asyncio.sleep(5)

    # --- Synchrone Event-Handler und Logikfunktionen ---
    def on_width_change(self, e):
        self.update_value_entry_from_width()
        self.update_folder_selection(e)

    def toggle_value(self, e):
        self.at_prefix_field.value = "24" if self.at_prefix_field.value == "25" else "25"
        self.page.update()

    def on_entry_change(self, e):
        if self.updating: return
        new_value = self.project_name_field.value
        if len(new_value) > 4:
            self.updating = True
            self.project_name_field.value = new_value[:4]
            self.page.update()
            self.updating = False  # Wichtig, dies zurückzusetzen

        # Erlaube leeres Feld, aber wenn nicht leer, dann nur Zahlen
        if new_value and not new_value.isdigit():
            self.show_dialog("Ungültige Eingabe", "Projektname: Bitte nur Zahlen eingeben.")
            self.updating = True
            self.project_name_field.value = self.current_value  # Zurück zum letzten gültigen Wert
            self.page.update()
            self.updating = False
            return

        if new_value != self.current_value:
            # Speichere auch leere Werte in History, wenn sie nicht der aktuelle Wert sind
            if self.current_value is not None:  # Nur wenn current_value initialisiert wurde
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

    def get_folder_options(self):
        try:
            if not config.BASE_PATH1.exists():
                self.show_dialog("Fehler", f"Spannmittel-Basisordner {config.BASE_PATH1} nicht gefunden.")
                return []
            folders = [d.name for d in config.BASE_PATH1.iterdir() if d.is_dir()]
            folders.sort(
                key=lambda name: int(re.match(r"(\d+)_.*", name).group(1)) if re.match(r"(\d+)_.*", name) else float(
                    'inf'))
            return folders
        except FileNotFoundError:  # Sollte durch die Prüfung oben abgedeckt sein, aber als Fallback
            self.show_dialog("Fehler", f"Spannmittel-Ordner {config.BASE_PATH1} nicht gefunden.")
            return []
        except Exception as ex:
            self.show_dialog("Fehler Ordneroptionen", f"Konnte Ordneroptionen nicht laden: {ex}")
            return []

    def check_dxf_files_status(self):
        machines = ["HERMLE-C40", "HERMLE-C400", "DMU-EVO60", "DMU-100EVO", "DMC650V", "DMC1035V"]
        h_files_count = 0
        for machine in machines:
            machine_path = config.BASE_PATH2 / machine / config.BASE_PATH3
            if machine_path.is_dir():  # Prüfe, ob es ein Verzeichnis ist
                h_files_count += sum(1 for _ in machine_path.glob("*.H"))

        self.dxf_status_container.controls.clear()
        if h_files_count > 0:
            for i in range(min(h_files_count, 10)):
                self.dxf_status_container.controls.append(
                    ft.Icon(name=ft.Icons.CHECK_CIRCLE_OUTLINED, color=ft.Colors.GREEN_600, size=20,
                            tooltip=f"Programm {i + 1}")
                )
            if h_files_count > 10:
                self.dxf_status_container.controls.append(
                    ft.Text(f"+{h_files_count - 10}", size=12, weight=ft.FontWeight.BOLD))
        else:
            self.dxf_status_container.controls.append(
                ft.Icon(name=ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED_600, size=16, tooltip="Keine Programme")
            )
            self.dxf_status_container.controls.append(
                ft.Text("Keine Progs", color=ft.Colors.RED_600, size=12, weight=ft.FontWeight.BOLD)
            )
        self.page.update()

    # --- Prozess Start/Stop Handler ---
    # self.script_process und self.external_flet_process werden in BlankMakerApp initialisiert
    def run_prozess_listener_script_ui_toggle(self, e):
        self.script_process = run_script_async(
            self.page,
            config.PATH_TO_PROZESS_LISTENER,
            self.script_process,  # Aktuelle Prozessreferenz übergeben
            self.start_button,
            self.stop_button,
            self.status_icon,
            self.status_text,
            "Prozess Listener",
            self._reset_prozess_listener_ui_to_stopped  # Callback für UI-Reset
        )

    def kill_prozess_listener_script_ui_toggle(self, e):
        kill_script_async(
            self.script_process,
            "Prozess Listener"
        )
        # Der Callback _reset_prozess_listener_ui_to_stopped wird durch monitor_process_async aufgerufen,
        # wenn der Prozess tatsächlich beendet ist.

    def _reset_prozess_listener_ui_to_stopped(self):
        self.script_process = None  # Wichtig, um den Zustand zurückzusetzen
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.status_icon.color = ft.Colors.RED_600
        self.status_text.value = "Gestoppt"
        self.status_text.color = ft.Colors.RED_600
        self.page.update()

    def start_external_flet_app_ui_toggle(self, e):
        self.external_flet_process = run_script_async(
            self.page,
            config.PATH_TO_EXTERNAL_FLET_APP,
            self.external_flet_process,
            self.start_external_flet_button,
            None,  # <<< HIER None ÜBERGEBEN für den stop_button
            None,
            self.external_flet_status_text,
            "Externe Flet App",
            self._reset_external_flet_ui_to_stopped,
            status_running_text="Externe Flet App: Läuft",
            status_stopped_text="Externe Flet App: Gestoppt",
            running_color=ft.Colors.GREEN_700
        )

    def stop_external_flet_app_ui_toggle(self, e):
        kill_script_async(
            self.external_flet_process,
            "Externe Flet App"
        )

    def _reset_external_flet_ui_to_stopped(self):
        self.external_flet_process = None
        self.start_external_flet_button.disabled = False
        #self.stop_external_flet_button.disabled = True
        self.external_flet_status_text.value = "Externe Flet App: Gestoppt"
        self.external_flet_status_text.color = "onsurfacevariant"
        self.page.update()

    # --- Automations-Workflows ---
    def start_kombiablauf_workflow(self, e):
        kombi_workflow_instance = KombiWorkflow(
            page=self.page,
            ctrl_v_field=self.ctrl_v_field,
            selection_dropdown=self.selection_dropdown,
            destination_field=self.destination_field,
            length_field=self.length_field,
            width_field=self.width_field,
            height_field=self.height_field,
            images_base_path=config.PATH_TO_IMAGES_FOLDER
        )
        try:
            kombi_workflow_instance.start_automation()
        except Exception as ex:
            self.show_dialog("Fehler Kombiablauf", f"Startfehler im Kombiablauf: {ex}")

    def start_bseite_automation_ui_toggle(self, e):
        try:
            partheight_str = self.blength_field.value.replace(',', '.')
            if not partheight_str:
                self.show_dialog("Eingabefehler", "Fertigteilhöhe für B-Seite darf nicht leer sein.")
                return
            partheight = float(partheight_str)

            start_bseite_automation_threaded(
                page_instance=self.page,
                partheight_value=partheight,
                images_base_path=config.PATH_TO_IMAGES_FOLDER
            )
        except ValueError:
            self.show_dialog("Eingabefehler", "Ungültige Zahl für Fertigteilhöhe (B-Seite).")
        except Exception as ex:
            self.show_dialog("Fehler B-Seite", f"Fehler beim Start der B-Seiten Automatisierung: {ex}")

    # --- Hilfsfunktionen für UI-Logik ---
    def update_dimensions_from_input(self, e):
        input_str = self.maße_field.value.replace(',', '.')
        parts = input_str.split('*')
        if len(parts) == 3:
            try:
                breite_str, hoehe_str, laenge_str = parts[0].strip(), parts[1].strip(), parts[2].strip()

                # Validierung, ob es Zahlen sind, bevor Zuweisung
                laenge = float(laenge_str)
                breite = float(breite_str)
                hoehe = float(hoehe_str)

                self.length_field.value = laenge_str
                self.width_field.value = breite_str
                self.height_field.value = hoehe_str
                self.value_field.value = breite_str  # value_field mit Breite befüllen

                self.update_folder_selection()
                self.page.update()
            except ValueError:
                self.show_dialog("Eingabefehler", "Ungültige Zahlen in Rohteil Maße. Format: Breite*Höhe*Länge.")
        elif input_str:
            self.show_dialog("Eingabefehler", "Ungültiges Format für Rohteil Maße. Erwartet: Breite*Höhe*Länge.")

    def update_folder_selection(self, e=None):
        try:
            length_str = self.length_field.value.replace(',', '.')
            width_str = self.width_field.value.replace(',', '.')
            length = float(length_str) if length_str else 0
            width = float(width_str) if width_str else 0
        except ValueError:
            return

        selection = self.selection_dropdown.value
        folder_name = None

        if selection in ['5 Achs  3 Achs', '5 Achs  5 Achs', '5 Achs']:
            if length <= 50 and 10 <= width <= 60:
                folder_name = '03_Präger_MINI'
            elif 50 < length <= 80 and 10 <= width <= 130:
                folder_name = '02_Präger_77'
            elif 80 < length <= 155 and 10 <= width <= 360:
                folder_name = '01_Präger_125'
            elif 155 < length <= 350 and 10 <= width <= 360:
                folder_name = '04_Dopppelpräger_125'
            elif 130 < length <= 250 and 10 <= width <= 130:
                folder_name = '05_Dopppelpräger_77'
        elif selection in ['3 Achs  3 Achs', '3 Achs']:
            if length <= 130 and width > 0:
                folder_name = '01_Präger_125'
            elif 130 < length <= 360 and width > 0:
                folder_name = '04_Dopppelpräger_125'

        if folder_name and folder_name in self.folder_options:
            if self.folder_dropdown.value != folder_name:
                self.folder_dropdown.value = folder_name
                self.page.update()
        # Optional: Dropdown zurücksetzen, wenn keine Regel zutrifft
        # elif self.folder_dropdown.value is not None and not folder_name:
        #     self.folder_dropdown.value = None
        #     self.page.update()

    def update_value_entry_from_width(self):
        if self.width_field.value:
            try:
                width_val_str = self.width_field.value.replace(',', '.')
                float(width_val_str)  # Nur zur Validierung
                self.value_field.value = width_val_str
                self.page.update()
            except ValueError:
                pass  # Breite ist keine Zahl, value_field nicht ändern

    # --- Dialog Helfer (korrigierte Version) ---
    def show_dialog(self, title: str, message_content: str):
        # Schließe zuerst einen eventuell offenen Dialog, der von dieser Klasse verwaltet wird.
        if self._active_dialog_instance and self._active_dialog_instance.open:
            print(
                f"Versuche, vorherigen Dialog '{self._active_dialog_instance.title.value if self._active_dialog_instance.title else ''}' zu schließen.")
            self.page.close(self._active_dialog_instance)
            # self.page.update() # close sollte update auslösen
            self._active_dialog_instance = None

        def _close_current_dialog_action(e):
            # Diese Funktion wird vom "OK"-Button des aktuellen Dialogs aufgerufen.
            # `current_dialog_for_action` wird per Closure erfasst.
            self.page.close(current_dialog_for_action)
            # self.page.update()
            if self._active_dialog_instance == current_dialog_for_action:
                self._active_dialog_instance = None

        current_dialog_for_action = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(str(message_content)),
            actions=[ft.TextButton("OK", on_click=_close_current_dialog_action)],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: (
                print(f"Dialog '{title}' dismissed (on_dismiss)."),
                # Wenn der Dialog durch Klick außerhalb geschlossen wird, auch die Referenz löschen.
                # Prüfe, ob es der aktive Dialog ist, bevor die Referenz gelöscht wird.
                (setattr(self, '_active_dialog_instance',
                         None) if self._active_dialog_instance == current_dialog_for_action else None)
            )
        )
        self._active_dialog_instance = current_dialog_for_action  # Referenz auf den NEUEN Dialog setzen
        self.page.open(current_dialog_for_action)
        # self.page.update() # page.open sollte update auslösen