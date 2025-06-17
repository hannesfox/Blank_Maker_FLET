# Rohteil Master
# Dieses Programm dient dazu, Rohteil-Rechtecke sowie Kreise und Spannmittel zu erstellen.
# Dazu ist es noch möglich, Esprit automatisch auszufüllen.
# Dieses Programm ersetzt vollständig den Total Commander!
#
# Zielpfad Änderung: ändere nur hier die Ordnerpfade!
#
# Autor: [Gschwendtner Johannes]
# Datum: [30.05.2025]
# Version: [9.5 - Flet Version mit neuem Design - Refactored]

import flet as ft
import shutil
import os
import asyncio
import subprocess
import datetime
import glob
import re
from pathlib import Path

# Annahme: Diese Module sind im selben Projektverzeichnis vorhanden und funktionsfähig.
# Wenn sie sich in Unterordnern befinden, müssen die Importe entsprechend angepasst werden.
from program1 import create_rectangle
from program2 import create_circle
from autoesprit import run_program
from bseite import start_mausbewegungen
from rohteilrechner import process_step_file
from kombiablauf import Kombiablauf
import actions

# --- Globale Pfadkonfiguration ---
# Pfade zum Ändern mit pathlib für bessere Lesbarkeit und Betriebssystemkompatibilität
base_path1 = Path(r"C:\Users\Gschwendtner\Desktop\Spannmittel")  # Pfad für Spannmittelordner
base_path2 = Path(r"K:\NC-PGM")  # NC-PGM Ausgabeordner Esprit
base_path3 = Path("WKS05")  # Auswahl von WKS Ordner (relativer Pfad)
base_path5 = Path(r"C:\Users\Gschwendtner\PycharmProjects\Blank_Maker_FLET\prozess.pyw")  # Flet-App-Pfad
PATH_TO_EXTERNAL_FLET_APP = Path(r"C:\Users\Gschwendtner\PycharmProjects\ProzessORC\Flet-ProzessOCR-1.0.py")


class BlankMakerApp:
    """
    Die Hauptanwendungsklasse für den Blank Maker.
    Sie kapselt die gesamte UI-Logik und die Anwendungsfunktionalität.
    """

    def __init__(self, page: ft.Page):
        self.page = page

        # --- Initialisierung der Anwendungszustände ---
        self.history = []  # Für den "Zurück"-Button des Projektnamens
        self.updating = False  # Flag zur Vermeidung von rekursiven Aufrufen bei UI-Updates
        self.current_value = ""
        self.script_process = None  # Prozess für das interne Skript
        self.external_flet_process = None  # Prozess für die externe Flet-App

        # --- Datumsabhängige Pfade dynamisch erstellen ---
        self.base_path4 = self.get_daily_folder_path()

        # --- UI-Erstellung ---
        self.create_ui_elements()
        self.folder_options = self.get_folder_options()
        self.folder_dropdown.options = [ft.dropdown.Option(folder) for folder in self.folder_options]
        self.build_ui()

        # --- Asynchrone Aufgabe starten ---
        self.page.run_task(self.continuously_check_dxf_files)

    def get_daily_folder_path(self) -> Path:
        """Ermittelt den Pfad für den aktuellen Wochentag."""
        current_date = datetime.datetime.now()
        kalenderwoche = int(current_date.strftime("%V"))
        wochentag_num_python = current_date.weekday()  # Montag = 0, Sonntag = 6
        wochentag_ordner_num = wochentag_num_python + 1  # Montag = 1, ...

        deutsche_wochentage_kurz = {0: "MO", 1: "DI", 2: "MI", 3: "DO", 4: "FR", 5: "SA", 6: "SO"}
        wochentag_kuerzel = deutsche_wochentage_kurz[wochentag_num_python]

        return Path(
            f"K:/Esprit/NC-Files/AT-25-KW{kalenderwoche}/Gschwendtner/{wochentag_ordner_num}.{wochentag_kuerzel}")

    def create_ui_elements(self):
        """
        Erstellt und konfiguriert alle UI-Widgets.
        Das Design wird hier zentral definiert.
        """
        # --- Design-Konstanten für einheitliches Aussehen ---
        textfield_style = {
            "filled": True,
            "bgcolor": ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
            "border": ft.InputBorder.OUTLINE,
            "border_radius": 5,
            "border_color": ft.Colors.with_opacity(0.3, ft.Colors.ON_SURFACE),
            "focused_border_color": ft.Colors.PRIMARY,
        }
        dropdown_style = {
            "filled": True,
            "bgcolor": "primaryContainer",
            "border": ft.InputBorder.OUTLINE,
            "border_radius": 5,
            "border_color": ft.Colors.with_opacity(0.3, ft.Colors.ON_SURFACE),
            "focused_border_color": ft.Colors.PRIMARY,
        }

        # --- Eingabefelder ---
        self.length_field = ft.TextField(label="X Länge:", width=150, on_change=self.update_folder_selection,
                                         **textfield_style)
        self.width_field = ft.TextField(label="Y Breite:", width=150, on_change=self.on_width_change, **textfield_style)
        self.height_field = ft.TextField(label="Z Höhe:", width=150, **textfield_style)
        self.diameter_field = ft.TextField(label="Durchmesser:", width=150, **textfield_style)
        self.height2_field = ft.TextField(label="Höhe:", width=150, **textfield_style)
        self.value_field = ft.TextField(label="Wert in mm:", width=300, **textfield_style)
        self.ctrl_v_field = ft.TextField(label="Text für CTRL+V eingeben:", width=300, **textfield_style)
        self.at_prefix_field = ft.TextField(label="AT-..", value="25", width=100, **textfield_style)
        self.project_name_field = ft.TextField(label="Projektname: zB.0815", width=200, max_length=4,
                                               on_change=self.on_entry_change, **textfield_style)
        self.destination_field = ft.TextField(label="Zielordner:", width=500, value=str(self.base_path4),
                                              **textfield_style)
        self.blength_field = ft.TextField(label="Fertigteilhöhe:", width=150, **textfield_style)
        self.maße_field = ft.TextField(label="Rohteil Maße (L*B*H):", width=300,
                                       on_change=self.update_dimensions_from_input, **textfield_style)

        # --- Dropdown-Menüs ---
        self.folder_dropdown = ft.Dropdown(label="Ordner auswählen:", width=300, options=[], **dropdown_style)
        self.selection_dropdown = ft.Dropdown(
            label="Maschinenart:", width=300, value="Option",
            options=[
                ft.dropdown.Option('5 Achs  3 Achs'), ft.dropdown.Option('5 Achs  5 Achs'),
                ft.dropdown.Option('3 Achs  3 Achs'), ft.dropdown.Option('5 Achs'), ft.dropdown.Option('3 Achs')
            ],
            on_change=self.update_folder_selection, **dropdown_style
        )

        # --- Buttons ---
        self.back_button = ft.ElevatedButton("Zurück", on_click=self.go_back, disabled=True)
        self.rect_make_button = ft.ElevatedButton("MAKE ..", on_click=self.handle_rect_creation)
        self.circle_make_button = ft.ElevatedButton("MAKE ..", on_click=self.handle_circle_creation)
        self.vice_create_button = ft.ElevatedButton("Schraubstock erstellen", on_click=self.handle_vice_creation)
        self.start_button = ft.ElevatedButton("Prozess Start", on_click=self.run_python_script,
                                              bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
        self.stop_button = ft.ElevatedButton("Prozess Stop", on_click=self.kill_python_script,
                                             bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, disabled=True)
        self.start_external_flet_button = ft.ElevatedButton("Externe Flet App STARTEN",
                                                            on_click=self.start_external_flet_app,
                                                            bgcolor=ft.Colors.GREEN_800, color=ft.Colors.WHITE)
        self.stop_external_flet_button = ft.ElevatedButton("Externe Flet App STOPPEN",
                                                           on_click=self.stop_external_flet_app,
                                                           bgcolor=ft.Colors.RED_800, color=ft.Colors.WHITE,
                                                           disabled=True)

        self.export_button = ft.ElevatedButton(
            text="PROGRAMM AUSGEBEN", icon=ft.Icons.SAVE, on_click=self.animate_and_move_files, width=300, height=40,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=5),
                padding=10, elevation=5, text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
            ),
            tooltip="Gibt die fertigen Programme aus."
        )
        self.export_button.animate_bgcolor = ft.Animation(duration=2500, curve=ft.AnimationCurve.EASE_IN_OUT)

        # --- Status-Anzeigen und Prozessleisten ---
        self.status_label = ft.Text("", size=15)

        #self.status_label1 = ft.Text("", size=15, color="primary")
        # Ein Container (Row), der dynamisch mit Icons oder Text gefüllt wird
        self.dxf_status_container = ft.Row(
            controls=[],
            wrap=True,  # Sorgt für einen Zeilenumbruch, falls zu viele Icons angezeigt werden
            spacing=2  # Kleiner Abstand zwischen den Icons
        )
        self.original_size_label = ft.Text("", size=8)
        self.status_icon = ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.RED_600, size=25)
        self.status_text = ft.Text("Gestoppt", size=12, color=ft.Colors.RED_600)
        self.external_flet_status_text = ft.Text("Externe Flet App: Gestoppt", size=12, color="onsurfacevariant")

        progress_bar_style = {"width": 200, "height": 10, "visible": False, "border_radius": 5}
        self.rect_progress = ft.ProgressBar(**progress_bar_style)
        self.circle_progress = ft.ProgressBar(**progress_bar_style)
        self.vice_progress = ft.ProgressBar(**progress_bar_style)

    def build_ui(self):
        """
        Stellt die erstellten UI-Elemente in einem strukturierten Layout zusammen.
        """
        self.page.add(
            ft.Column([
                ft.Text("Programmname:", size=16, weight=ft.FontWeight.BOLD),
                self.ctrl_v_field,
                self.selection_dropdown,
                ft.Divider(height=40),
                ft.Text("Rohteil Erstellung:", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    height=250,
                    content=ft.Tabs(
                        selected_index=0, animation_duration=300,
                        tabs=[
                            ft.Tab(
                                text="Rechteck", icon=ft.Icons.RECTANGLE,
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Row([self.length_field, self.width_field, self.height_field]),
                                        ft.Row([self.rect_make_button, self.rect_progress],
                                               vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                        self.original_size_label,
                                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                                    padding=ft.padding.symmetric(horizontal=5),
                                )
                            ),
                            ft.Tab(
                                text="Kreis", icon=ft.Icons.CIRCLE_OUTLINED,
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Row([self.diameter_field, self.height2_field]),
                                        ft.Row([self.circle_make_button, self.circle_progress],
                                               vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                                    padding=ft.padding.symmetric(horizontal=5),
                                )
                            ),
                        ], expand=True,
                    ),
                    border=ft.border.all(2, "outlinevariant"), border_radius=ft.border_radius.all(8), padding=5,
                ),
                ft.Text("Spannmittel Auswahl:", size=16, weight=ft.FontWeight.BOLD),
                self.value_field,
                self.folder_dropdown,
                ft.Text("Zielordner:"),
                self.destination_field,
                ft.Row([self.vice_create_button, self.vice_progress], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=20),
                ft.Container(
                    content=ft.ElevatedButton(
                        text="Kombiablauf Starten", icon=ft.Icons.AUTO_FIX_HIGH_OUTLINED,
                        on_click=self.start_kombiablauf,
                        width=300, height=40,
                        style=ft.ButtonStyle(
                            bgcolor="primaryContainer", color="onPrimaryContainer",
                            shape=ft.RoundedRectangleBorder(radius=5), padding=10, elevation=5
                        ),
                        tooltip="Auto Ausfüllen, Laden der DXF u. Schraubstockes, Pause, Rohteil Definierung und Erstellung."
                    ),
                    alignment=ft.alignment.center, padding=ft.padding.symmetric(vertical=10)
                ),
                ft.Divider(height=10),
                ft.Row([self.blength_field, ft.ElevatedButton("   B-Start   ", on_click=self.start_bseite)]),
                ft.Divider(height=10),
                ft.Row(controls=[
                    ft.Column(controls=[
                        ft.Text("PythonCommander:", size=12, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            [self.at_prefix_field, ft.ElevatedButton("     Switch    ", on_click=self.toggle_value)]),
                        ft.Row([self.project_name_field, self.back_button]),
                    ], alignment=ft.MainAxisAlignment.START, expand=True),
                    ft.Column(controls=[self.status_label, self.dxf_status_container],
                              alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.END,
                              expand=True)
                ]),
                ft.Container(content=self.export_button, alignment=ft.alignment.center,
                             padding=ft.padding.symmetric(vertical=20)),
                ft.Divider(height=10),
                ft.Row(controls=[
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Prozess Öffnen:", size=12, weight=ft.FontWeight.BOLD),
                            ft.Row([self.start_button, self.stop_button], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([self.status_icon, self.status_text], alignment=ft.MainAxisAlignment.CENTER),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=True, padding=10, border=ft.border.all(1, "outlinevariant"),
                        border_radius=ft.border_radius.all(8),
                    ),
                    ft.VerticalDivider(width=10, thickness=1),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Externe Flet Anwendung (ProzessOCR):", size=12, weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER),
                            ft.Row([self.start_external_flet_button], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([self.external_flet_status_text], alignment=ft.MainAxisAlignment.CENTER),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=True, padding=10, border=ft.border.all(1, "outlinevariant"),
                        border_radius=ft.border_radius.all(8),
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.START),
            ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        )

    # --- Asynchrone Event-Handler und UI-Updaters ---

    async def run_task_with_progress(self, e, button: ft.ElevatedButton, progress_bar: ft.ProgressBar, task_function):
        """Zeigt eine Prozessleiste an, führt eine Aufgabe aus und aktualisiert die UI."""
        button.disabled = True
        progress_bar.visible = True
        progress_bar.value = None  # Indeterminate progress
        self.page.update()

        await asyncio.sleep(0.5)  # Kurze Pause für den visuellen Effekt

        try:
            task_function(e)
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

        self.move_files(e)  # Führe die eigentliche Aktion aus

        self.export_button.bgcolor = ft.Colors.RED_600
        self.export_button.disabled = False
        self.page.update()

    async def continuously_check_dxf_files(self):
        """Überprüft periodisch das Vorhandensein von .H-Dateien."""
        while True:
            self.check_dxf_files()
            await asyncio.sleep(5)  # Überprüft alle 5 Sekunden

    async def monitor_process(self, process, on_stop_callback):
        """Überwacht einen Subprozess und ruft bei Beendigung eine Callback-Funktion auf."""
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

    def create_rect(self, e):
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

    def create_circle(self, e):
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
            folders = [d.name for d in base_path1.iterdir() if d.is_dir()]
            folders.sort(key=lambda name: int(name.split("_")[0]))
            return folders
        except (FileNotFoundError, IndexError, ValueError):
            return []

    def copy_file(self, e):
        try:
            folder_name = self.folder_dropdown.value
            value = self.value_field.value
            if not folder_name or not value:
                raise ValueError("Ordner oder Wert nicht ausgewählt.")

            source_folder = base_path1 / folder_name
            destination_folder = Path(self.destination_field.value)

            found = False
            for file in source_folder.iterdir():
                if (file.suffix.lower() == ".step" and re.search(r"\b{}\b".format(value),
                                                                 file.name)) or file.suffix.lower() == ".dxf":
                    shutil.copy2(file,
                                 destination_folder / f"!schraubstock{file.suffix}" if file.suffix.lower() == ".step" else destination_folder / file.name)
                    found = True
            if not found:
                self.show_dialog("Info", f"Keine passende Datei für Wert '{value}' gefunden.")

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
            source_dir = base_path2 / machine / base_path3
            if not source_dir.exists(): continue

            destination_dir = base_path2 / machine / f"AT{at_prefix}-{project_name}"
            destination_dir.mkdir(exist_ok=True)

            for file_path in source_dir.glob("*.H"):
                shutil.move(str(file_path), str(destination_dir / file_path.name))
                moved_count += 1

        if moved_count > 0:
            #self.status_label.value = f"{moved_count} Programme verschoben!"
            self.status_label.color = ft.Colors.GREEN_600
        else:
            self.status_label.value = "Keine .H-Dateien zum Verschieben gefunden."
            self.status_label.color = ft.Colors.ORANGE_400
        self.page.update()

    def check_dxf_files(self):
        """
        Überprüft das Vorhandensein von .H-Dateien und zeigt den Status
        dynamisch mit Icons oder einem Platzhalter an.
        """
        machines = ["HERMLE-C40", "HERMLE-C400", "DMU-EVO60", "DMU-100EVO", "DMC650V", "DMC1035V"]
        h_files_count = sum(len(list((base_path2 / machine / base_path3).glob("*.H"))) for machine in machines)

        # 1. Leere den Container, bevor du ihn neu befüllst
        self.dxf_status_container.controls.clear()

        if h_files_count > 0:
            # 2. Füge für jede gefundene Datei ein Icon hinzu
            for _ in range(h_files_count):
                self.dxf_status_container.controls.append(
                    ft.Icon(
                        name=ft.Icons.CHECK_CIRCLE_OUTLINED,  # Ein passendes Icon
                        color=ft.Colors.GREEN_600,
                        size=20
                    )
                )
        else:
            # 3. Zeige den Platzhalter an, wenn keine Dateien gefunden wurden
            self.dxf_status_container.controls.append(
                ft.Icon(
                    name=ft.Icons.ERROR_OUTLINE,  # Ein anderes passendes Icon
                    color=ft.Colors.RED_600,
                    size=16  # Etwas kleiner, um gut zum Text zu passen
                )
            )
            self.dxf_status_container.controls.append(
                ft.Text(
                    "Keine Programme",
                    color=ft.Colors.RED_600,
                    size=12,
                    weight=ft.FontWeight.BOLD
                )
            )

        # 4. Aktualisiere die Seite, um die Änderungen anzuzeigen
        self.page.update()

    def run_python_script(self, e):
        if self.script_process and self.script_process.poll() is None:
            self.show_dialog("Info", "Prozess läuft bereits!")
            return
        try:
            self.script_process = subprocess.Popen(["python", base_path5], creationflags=subprocess.CREATE_NO_WINDOW)
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.status_icon.color = ft.Colors.GREEN_600
            self.status_text.value = "Läuft"
            self.status_text.color = ft.Colors.GREEN_600
            self.page.update()
            self.page.run_task(self.monitor_process, self.script_process, self.reset_ui_to_stopped)
        except Exception as ex:
            self.show_dialog("Fehler", f"Fehler beim Starten des Skripts: {ex}")

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
            self.external_flet_process = subprocess.Popen(["python", PATH_TO_EXTERNAL_FLET_APP],
                                                          creationflags=subprocess.CREATE_NO_WINDOW)
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
            partheight = float(self.blength_field.value.replace(',', '.'))
            start_mausbewegungen(self.page, partheight)
        except (ValueError, TypeError):
            self.show_dialog("Fehler", "Ungültige Eingabe für Fertigteilhöhe.")
        except Exception as ex:
            self.show_dialog("Fehler", f"Fehler beim Starten der B-Seite: {ex}")

    def update_dimensions_from_input(self, e):
        parts = self.maße_field.value.replace(',', '.').split('*')
        if len(parts) == 3:
            try:
                length, width, height = parts[2], parts[0], parts[1]
                self.length_field.value = str(float(length))
                self.width_field.value = str(float(width))
                self.height_field.value = str(float(height))
                self.value_field.value = str(float(width))
                self.update_folder_selection()
                self.page.update()
            except ValueError:
                pass

    def update_folder_selection(self, e=None):
        try:
            length = float(self.length_field.value) if self.length_field.value else 0
            width = float(self.width_field.value) if self.width_field.value else 0
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
            if length <= 130:
                folder_name = '01_Präger_125'
            elif 130 < length <= 360:
                folder_name = '04_Dopppelpräger_125'

        if folder_name and folder_name in self.folder_options:
            self.folder_dropdown.value = folder_name
            self.page.update()

    def update_value_entry(self):
        if self.width_field.value:
            self.value_field.value = self.width_field.value
            self.page.update()

    def show_dialog(self, title, message):
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: self.close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()


def main(page: ft.Page):
    # --- Fensterkonfiguration ---
    page.title = "BMM 9.FLET by Gschwendtner Johannes"
    page.window.width = 600
    page.window.height = 1420  # Höhe angepasst für bessere Darstellung ohne Scrollen
    page.window.resizable = True
    page.window.maximizable = True
    page.window.left = -5
    page.window.top = 0

    # --- Definition der Farbthemen (Light & Dark) ---
    # Hier werden die Farben zentral für die gesamte App festgelegt.
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#049fb4",
            primary_container="#e0f7fa",
            on_primary_container="#036f7e",
            secondary_container=ft.Colors.BLUE_GREY_200,
            on_secondary_container=ft.Colors.BLUE_GREY_900,
            outline_variant=ft.Colors.GREY_400,
        ),
        use_material3=True,
    )
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#05cfea",
            primary_container="#036f7e",
            on_primary_container=ft.Colors.WHITE,
            secondary_container=ft.Colors.BLUE_GREY_700,
            on_secondary_container=ft.Colors.BLUE_GREY_100,
            outline_variant=ft.Colors.GREY_700,
            on_surface=ft.Colors.WHITE,  # Besserer Kontrast für Text im Dark Mode
        ),
        use_material3=True,
    )

    # Passt sich automatisch dem OS-Modus (Light/Dark) an
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- App-Instanz erstellen und ausführen ---
    app = BlankMakerApp(page)


if __name__ == '__main__':
    ft.app(target=main)