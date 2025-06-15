# Rohteil Master


# Dieses Programm dient dazu, Rohteil-Rechtecke sowie Kreise und Spannmittel zu erstellen.
# Dazu ist es noch möglich, Esprit automatisch auszufüllen.
# Dieses Programm ersetzt vollständig den Total Commander!

# Zielpfad Änderung: ändere nur hier die Ordnerpfade!

# Autor: [Gschwendtner Johannes]
# Datum: [30.05.2025]
# Version: [9.5 - Flet Version mit neuem Design]

import flet as ft
from program1 import create_rectangle
from program2 import create_circle
from autoesprit import run_program
from bseite import start_mausbewegungen
import shutil
import os
import pyautogui
import pyscreeze
import time
import re
import glob
import subprocess
import datetime
import asyncio
from pathlib import Path
from rohteilrechner import process_step_file
from kombiablauf import Kombiablauf
import actions

# ==============================================================================
#  KONFIGURATION: PFADE FÜR WINDOWS & MAC
# ==============================================================================


# Automatische Erkennung des Betriebssystems
IS_WINDOWS = os.name == 'nt'

if IS_WINDOWS:
    user_profile = Path.home()
    # Netzlaufwerke
    net_drive_k = Path(r"K:")

    # Basispfade für Windows
    base_path1 = user_profile / "Desktop" / "Spannmittel"
    base_path2 = net_drive_k / "NC-PGM"
    esprit_base_path = net_drive_k / "Esprit"
    base_path5 = user_profile / "PycharmProjects" / "Blank_Maker_FLET" / "prozess.pyw"
    PATH_TO_EXTERNAL_FLET_APP = user_profile / "PycharmProjects" / "ProzessORC" / "Flet-ProzessOCR-1.0.py"

else:
    # --- MACOS PFADE  ---
    base_path1 = Path("/Users/hannes/Desktop/Blank_Maker_FLET/Pfade-Mac/Spannmittel")
    base_path2 = Path("/Pfade-Mac/NC-PGM")
    esprit_base_path = Path("/Pfade-Mac/Esprit")
    base_path5 = Path("/prozess.pyw")

    # PFAD FÜR EXTERNE APP:
    PATH_TO_EXTERNAL_FLET_APP = Path("/Users/hannes/Desktop/ProzessORC/Flet-ProzessOCR-1.0.py")
    #WKS pfad
    base_path3 = Path("WKS05")

# ==============================================================================
#  ENDE DER KONFIGURATION
# ==============================================================================


class BlankMakerApp:
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page

        current_date = datetime.datetime.now()
        kalenderwoche = int(current_date.strftime("%V"))
        wochentag_num_python = current_date.weekday()
        wochentag_ordner_num = (wochentag_num_python + 1) % 7
        if wochentag_ordner_num == 0:  # Sonntag
            wochentag_ordner_num = 7

        # Deutsch
        deutsche_wochentage_kurz = {
            0: "MO",  # Montag
            1: "DI",  # Dienstag
            2: "MI",  # Mittwoch
            3: "DO",  # Donnerstag
            4: "FR",  # Freitag
            5: "SA",  # Samstag
            6: "SO"  # Sonntag
        }
        wochentag_kuerzel = deutsche_wochentage_kurz[wochentag_num_python]

        # pathlib neu
        self.base_path4 = Path(
            f"K:/Esprit/NC-Files/AT-25-KW{kalenderwoche}/Gschwendtner/{wochentag_ordner_num}.{wochentag_kuerzel}")

        self.history = []  # Für Zurück-Button
        self.updating = False  # Flag zur Vermeidung von rekursiven Aufrufen
        self.current_value = ""
        self.script_process = None
        self.external_flet_process = None  # NEU: Für die externe Flet App

        # UI-Elemente erstellen
        self.create_ui_elements()
        self.folder_options = self.get_folder_options()
        self.folder_dropdown.options = [ft.dropdown.Option(folder) for folder in self.folder_options]

        self.build_ui()
        self.check_dxf_files()

    def create_ui_elements(self):
        # Eingabefelder

        self.length_field = ft.TextField(label="X Länge:", width=150, on_change=self.update_folder_selection,
                                         # Diese Eigenschaften hinzufügen:
                                         filled=True,
                                         bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                         border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                         border_radius=5,  # Runde Ecken
                                         border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                         focused_border_color="#05cfea",
                                         )

        self.width_field = ft.TextField(label="Y Breite:", width=150, on_change=self.on_width_change,
                                        # Diese Eigenschaften hinzufügen:
                                        filled=True,
                                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                        border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                        border_radius=5,  # Runde Ecken
                                        border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                        focused_border_color="#05cfea",
                                        )
        self.height_field = ft.TextField(label="Z Höhe:", width=150,
                                         # Diese Eigenschaften hinzufügen:
                                         filled=True,
                                         bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                         border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                         border_radius=5,  # Runde Ecken
                                         border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                         focused_border_color="#05cfea",
                                         )

        self.diameter_field = ft.TextField(label="Durchmesser:", width=150,
                                           # Diese Eigenschaften hinzufügen:
                                           filled=True,
                                           bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                           border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                           border_radius=5,  # Runde Ecken
                                           border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                           focused_border_color="#05cfea",
                                           )
        self.height2_field = ft.TextField(label="Höhe:", width=150,
                                          # Diese Eigenschaften hinzufügen:
                                          filled=True,
                                          bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                          border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                          border_radius=5,  # Runde Ecken
                                          border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                          focused_border_color="#05cfea",
                                          )
        self.value_field = ft.TextField(label="Wert in mm:", width=300,
                                        # Diese Eigenschaften hinzufügen:
                                        filled=True,
                                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                        border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                        border_radius=5,  # Runde Ecken
                                        border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                        focused_border_color="#05cfea",
                                        )
        self.ctrl_v_field = ft.TextField(label="Text für CTRL+V eingeben:", width=300,
                                         # Diese Eigenschaften hinzufügen:
                                         filled=True,
                                         bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                         border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                         border_radius=5,  # Runde Ecken
                                         border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                         focused_border_color="#05cfea",
                                         )
        self.at_prefix_field = ft.TextField(label="AT-..", value="25", width=100,
                                            # Diese Eigenschaften hinzufügen:
                                            filled=True,
                                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                            border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                            border_radius=5,  # Runde Ecken
                                            border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                            focused_border_color="#05cfea",
                                            )
        self.project_name_field = ft.TextField(label="Projektname: zB.0815", width=200, max_length=4,
                                               on_change=self.on_entry_change,
                                               # Diese Eigenschaften hinzufügen:
                                               filled=True,
                                               bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                               border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                               border_radius=5,  # Runde Ecken
                                               border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                               focused_border_color="#05cfea",
                                               )
        self.destination_field = ft.TextField(label="Zielordner:", width=500, value=str(self.base_path4),
                                              # Diese Eigenschaften hinzufügen:
                                              filled=True,
                                              bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                              border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                              border_radius=5,  # Runde Ecken
                                              border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                              focused_border_color="#05cfea",
                                              )
        self.blength_field = ft.TextField(label="Fertigteilhöhe:", width=150,
                                          # Diese Eigenschaften hinzufügen:
                                          filled=True,
                                          bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                          border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                          border_radius=5,  # Runde Ecken
                                          border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                          focused_border_color="#05cfea",
                                          )
        self.maße_field = ft.TextField(label="Rohteil Maße (L*B*H):", width=300,
                                       on_change=self.update_dimensions_from_input,
                                       # Diese Eigenschaften hinzufügen:
                                       filled=True,
                                       bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                       border=ft.InputBorder.OUTLINE,  # Erzeugt den Kasten
                                       border_radius=5,  # Runde Ecken
                                       border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                                       focused_border_color="#05cfea",
                                       )

        # Dropdown-Menüs
        self.folder_dropdown = ft.Dropdown(
            label="Ordner auswählen:",
            width=300,
            options=[],
            filled=True,
            bgcolor=ft.Colors.GREY_800,
            border=ft.InputBorder.OUTLINE,
            border_radius=5,
            border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
            focused_border_color="#05cfea",
        )

        self.selection_dropdown = ft.Dropdown(
            label="Maschinenart:",
            width=300, filled=True,
            bgcolor=ft.Colors.GREY_800,
            border=ft.InputBorder.OUTLINE,
            border_radius=5,
            border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
            focused_border_color="#05cfea",
            value="Option",
            options=[
                ft.dropdown.Option('5 Achs  3 Achs'),
                ft.dropdown.Option('5 Achs  5 Achs'),
                ft.dropdown.Option('3 Achs  3 Achs'),
                ft.dropdown.Option('5 Achs'),
                ft.dropdown.Option('3 Achs')
            ],
            on_change=self.update_folder_selection
        )

        # Buttons
        self.back_button = ft.ElevatedButton("Zurück", on_click=self.go_back, disabled=True)

        # Status Labels
        self.status_label = ft.Text("", size=15)  # Farbe wird dynamisch gesetzt
        self.status_label1 = ft.Text("", size=15, color="primary")  # Nutzt die Primärfarbe des Themes
        self.original_size_label = ft.Text("", size=8)

        # Prozess Öffnen button
        self.start_button = ft.ElevatedButton(
            "Prozess Start",
            on_click=self.run_python_script,
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
            disabled=False
        )

        self.stop_button = ft.ElevatedButton(
            "Prozess Stop",
            on_click=self.kill_python_script,
            bgcolor=ft.Colors.RED_700,
            color=ft.Colors.WHITE,
            disabled=True
        )

        self.status_icon = ft.Icon(
            ft.Icons.CIRCLE,
            color=ft.Colors.RED_600,
            size=25
        )

        self.status_text = ft.Text(
            "Gestoppt",
            size=12,
            color=ft.Colors.RED_600
        )

        # Buttons und Status für die externe Flet-Anwendung
        self.start_external_flet_button = ft.ElevatedButton(
            "Externe Flet App STARTEN",
            on_click=self.start_external_flet_app,
            bgcolor=ft.Colors.GREEN_800,
            color=ft.Colors.WHITE,
        )
        self.stop_external_flet_button = ft.ElevatedButton(
            "Externe Flet App STOPPEN",
            on_click=self.stop_external_flet_app,
            bgcolor=ft.Colors.RED_800,
            color=ft.Colors.WHITE,
            disabled=True
        )
        self.external_flet_status_text = ft.Text(
            "Externe Flet App: Gestoppt",
            size=12,
            color="onsurfacevariant"  # Theme-abhängige graue Farbe
        )
        self.rect_make_button = ft.ElevatedButton(
            "MAKE ..",
            on_click=self.handle_rect_creation
        )
        # Prozessleiste für das Rechteck
        self.rect_progress = ft.ProgressBar(
            width=200,
            height=10,
            visible=False,
            border_radius=5
        )

        self.rect_make_button.animate_bgcolor = ft.Animation(
            duration=150,
            curve=ft.AnimationCurve.EASE_IN_OUT
        )

        self.circle_make_button = ft.ElevatedButton(
            "MAKE ..",
            on_click=self.handle_circle_creation
        )
        # Prozessleiste für den Kreis
        self.circle_progress = ft.ProgressBar(
            width=200,
            height=10,
            visible=False,
            border_radius=5
        )

        self.circle_make_button.animate_bgcolor = ft.Animation(
            duration=150,
            curve=ft.AnimationCurve.EASE_IN_OUT
        )
        self.vice_create_button = ft.ElevatedButton(
            "Schraubstock erstellen",
            on_click=self.handle_vice_creation
        )

        # Prozessleiste für den Schraubstock
        self.vice_progress = ft.ProgressBar(
            width=200,
            height=10,
            visible=False,
            border_radius=5
        )

        # programm ausgeben button
        self.export_button = ft.ElevatedButton(
            text="PROGRAMM AUSGEBEN",
            icon=ft.Icons.SAVE,
            on_click=self.animate_and_move_files,
            width=300,
            height=40,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_600,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=5),
                padding=10,
                elevation=5,
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
            ),
            tooltip="Gibt die fertigen Programm aus."
        )

        self.export_button.animate_bgcolor = ft.Animation(
            duration=2500,
            curve=ft.AnimationCurve.EASE_IN_OUT
        )

    # -----------------------------------------ENDE Create ui Elements----------------------------------------

    def build_ui(self):
        # UI Layout erstellen
        self.page.add(
            ft.Column([
                # Programmname Sektion
                ft.Text("Programmname:", size=16, weight=ft.FontWeight.BOLD),
                self.ctrl_v_field,
                self.selection_dropdown,

                ft.Divider(height=40),

                ft.Text("Rohteil Erstellung:", size=16, weight=ft.FontWeight.BOLD),

                # tabs
                ft.Container(
                    height=250,
                    content=ft.Tabs(
                        selected_index=0,
                        animation_duration=2000,
                        tabs=[
                            # Tab 1: Rechteck erstellen
                            ft.Tab(
                                text="Rechteck",
                                icon=ft.Icons.RECTANGLE,
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Row([self.length_field, self.width_field, self.height_field]),
                                            ft.Row(
                                                [
                                                    self.rect_make_button,
                                                    self.rect_progress,
                                                ],
                                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                                            ),
                                            self.original_size_label,
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND
                                    ),
                                    padding=ft.padding.symmetric(horizontal=5),
                                )
                            ),

                            # Tab 2: Kreis erstellen
                            ft.Tab(
                                text="Kreis",
                                icon=ft.Icons.CIRCLE_OUTLINED,
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Row([self.diameter_field, self.height2_field]),
                                            ft.Row(
                                                [
                                                    self.circle_make_button,
                                                    self.circle_progress,
                                                ],
                                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                                            ),
                                            self.original_size_label,
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND
                                    ),
                                    padding=ft.padding.symmetric(horizontal=5),
                                )
                            ),
                        ],
                        expand=True,
                    ),
                    # Rahmen nutzt jetzt Theme-Farbe
                    border=ft.border.all(2, "outlinevariant"),
                    border_radius=ft.border_radius.all(8),
                    padding=5,
                ),

                # Spannmittel Sektion
                ft.Text("Spannmittel Auswahl:", size=16, weight=ft.FontWeight.BOLD),
                self.value_field,
                self.folder_dropdown,
                ft.Text("Zielordner:"),
                self.destination_field,

                # Button und Prozessleiste in eine Zeile packen
                ft.Row(
                    [
                        self.vice_create_button,
                        self.vice_progress,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),

                ft.Divider(height=20),

                # Button Kombiablauf mit Play-Icon
                ft.Container(
                    content=ft.ElevatedButton(
                        text="Kombiablauf Starten",
                        icon=ft.Icons.AUTO_FIX_HIGH_OUTLINED,
                        on_click=self.start_kombiablauf,
                        width=300,
                        height=40,
                        style=ft.ButtonStyle(
                            # Nutzt jetzt die Theme-Farben für einen passenden Look
                            bgcolor="primaryContainer",
                            color="onPrimaryContainer",
                            shape=ft.RoundedRectangleBorder(radius=5),
                            padding=10,
                            elevation=5
                        ),
                        tooltip="Auto Ausfüllen, Laden der DXF u. Schraubstockes, Pause:-) , Rohteil Definierung und Erstellung."
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=10)
                ),

                ft.Divider(height=10),

                # B-Seite
                ft.Row([
                    self.blength_field,
                    ft.ElevatedButton("   B-Start   ", on_click=self.start_bseite)
                ]),

                ft.Divider(height=10),

                # Python Commander aufgeteilt auf links und rechts
                ft.Row(
                    controls=[
                        # Linke Spalte: Python Commander
                        ft.Column(
                            controls=[
                                ft.Text("PythonCommander:", size=12, weight=ft.FontWeight.BOLD),
                                ft.Row([
                                    self.at_prefix_field,
                                    ft.ElevatedButton("     Switch    ", on_click=self.toggle_value)
                                ]),
                                ft.Row([
                                    self.project_name_field,
                                    self.back_button
                                ]),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            expand=True
                        ),

                        # Rechte Spalte: Status Labels
                        ft.Column(
                            controls=[
                                self.status_label,
                                self.status_label1
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            expand=True
                        )
                    ]
                ),

                # Button Programm Ausgeben
                ft.Container(
                    content=self.export_button,
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=20)
                ),

                ft.Divider(height=10),

                ft.Row(
                    controls=[
                        # Linke Spalte
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Prozess Öffnen:", size=12, weight=ft.FontWeight.BOLD),
                                    ft.Row(
                                        [self.start_button, self.stop_button],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                    ft.Row(
                                        [self.status_icon, self.status_text],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            expand=True,
                            padding=10,
                            border=ft.border.all(1, "outlinevariant"),
                            border_radius=ft.border_radius.all(8),
                        ),

                        # Vertikale Trennlinie
                        ft.VerticalDivider(width=10, thickness=1),

                        # Rechte Spalte: Externe Flet App
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Externe Flet Anwendung (ProzessOCR):", size=12, weight=ft.FontWeight.BOLD,
                                            text_align=ft.TextAlign.CENTER),
                                    ft.Row(
                                        [
                                            self.start_external_flet_button,
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                    ft.Row(
                                        [self.external_flet_status_text],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            expand=True,
                            padding=10,
                            border=ft.border.all(1, "outlinevariant"),
                            border_radius=ft.border_radius.all(8),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
                scroll=ft.ScrollMode.ADAPTIVE,
                expand=True,
            )
        )

    # -----------------------------------------UI Ende---------------------------------------

    async def handle_vice_creation(self, e):
        """Neuer Event-Handler für den Schraubstock-Button."""
        await self.run_task_with_progress(e, self.vice_create_button, self.vice_progress, self.copy_file)

    async def run_task_with_progress(self, e, button: ft.ElevatedButton, progress_bar: ft.ProgressBar,
                                     task_function):
        """
        Eine allgemeine Funktion, die eine Prozessleiste anzeigt, eine Aufgabe ausführt und die UI aktualisiert.
        """
        button.disabled = True
        progress_bar.visible = True
        progress_bar.value = None
        self.page.update()

        await asyncio.sleep(2)

        try:
            task_function(e)
            progress_bar.color = ft.Colors.GREEN
            progress_bar.value = 1
            self.page.update()
            await asyncio.sleep(0.5)

        except Exception as ex:
            progress_bar.color = ft.Colors.RED
            progress_bar.value = 1
            self.page.update()
            await asyncio.sleep(1)
            self.show_dialog("Fehler bei der Ausführung", str(ex))

        finally:
            progress_bar.visible = False
            progress_bar.color = None
            progress_bar.value = None
            button.disabled = False
            self.page.update()

    async def handle_rect_creation(self, e):
        """Neuer Event-Handler für den Rechteck-Button."""
        await self.run_task_with_progress(e, self.rect_make_button, self.rect_progress, self.create_rect)

    async def handle_circle_creation(self, e):
        """Neuer Event-Handler für den Kreis-Button."""
        await self.run_task_with_progress(e, self.circle_make_button, self.circle_progress, self.create_circle)

    async def animate_and_move_files(self, e):
        self.export_button.disabled = True
        self.page.update()

        self.export_button.bgcolor = ft.Colors.GREEN_600
        self.page.update()

        await asyncio.sleep(1)

        self.export_button.bgcolor = ft.Colors.RED_600
        self.page.update()

        await asyncio.sleep(2.5)

        self.export_button.disabled = False
        self.page.update()

        self.move_files(e)

    def on_width_change(self, e):
        self.update_value_entry()
        self.update_folder_selection(e)

    def toggle_value(self, e):
        current_value = self.at_prefix_field.value
        if current_value == "25":
            self.at_prefix_field.value = "24"
        else:
            self.at_prefix_field.value = "25"
        self.page.update()

    def start_kombiablauf(self, e):
        kombi = Kombiablauf(self.page,
                            self.ctrl_v_field,
                            self.selection_dropdown,
                            self.destination_field,
                            self.length_field,
                            self.width_field,
                            self.height_field)
        try:
            kombi.kombiablauf()
        except Exception as ex_kombi_start:
            self.show_dialog("Fehler Kombiablauf", f"Startfehler im Kombiablauf: {ex_kombi_start}")

    def on_entry_change(self, e):
        if self.updating:
            return
        new_value = self.project_name_field.value
        if len(new_value) != 4:
            if len(new_value) > 4:
                self.updating = True
                self.project_name_field.value = new_value[:4]
                self.updating = False
                self.page.update()
            return
        if not new_value.isdigit():
            self.show_dialog("Ungültige Eingabe", "Bitte geben Sie nur 4-stellige Zahlen ein.")
            self.updating = True
            self.project_name_field.value = self.current_value
            self.updating = False
            self.page.update()
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
            if not self.history:
                self.back_button.disabled = True
            self.page.update()

    def create_rect(self, e):
        try:
            length = float(self.length_field.value)
            width = float(self.width_field.value)
            height = float(self.height_field.value)
            create_rectangle(length, width, height)
            shutil.copy("!rohteil.dxf", self.destination_field.value)
        except ValueError:
            self.show_dialog("Fehler", "Ungültige Eingabe für Rechteck-Maße")
        except Exception as e:
            self.show_dialog("Fehler", f"Fehler beim Erstellen des Rechtecks: {e}")

    def create_circle(self, e):
        try:
            diameter = float(self.diameter_field.value)
            height = float(self.height2_field.value)
            create_circle(diameter, height)
            shutil.copy("!rohteil.dxf", self.destination_field.value)
        except ValueError:
            self.show_dialog("Fehler", "Ungültige Eingabe für Kreis-Maße")
        except Exception as e:
            self.show_dialog("Fehler", f"Fehler beim Erstellen des Kreises: {e}")

    def get_folder_options(self):
        initial_dir = f"{base_path1}"
        folder_options = []
        try:
            for folder_name in os.listdir(initial_dir):
                folder_path = os.path.join(initial_dir, folder_name)
                if os.path.isdir(folder_path):
                    folder_options.append(folder_name)

            def get_folder_number(folder_name):
                return int(folder_name.split("_")[0])

            folder_options.sort(key=get_folder_number)
        except:
            pass
        return folder_options

    def copy_file(self, e):
        try:
            folder_name = self.folder_dropdown.value
            folder_path = os.path.join(f"{base_path1}", folder_name)
            value = self.value_field.value
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".step"):
                    if re.search(r"\b{}\b".format(value), file_name):
                        source_path = os.path.join(folder_path, file_name)
                        destination_path = os.path.join(self.destination_field.value, "!schraubstock.step")
                        shutil.copyfile(source_path, destination_path)
                elif file_name.endswith(".dxf"):
                    source_path = os.path.join(folder_path, file_name)
                    destination_path = os.path.join(self.destination_field.value, file_name)
                    shutil.copyfile(source_path, destination_path)
        except Exception as e:
            self.show_dialog("Fehler", f"Fehler beim Kopieren der Datei: {e}")

    def execute_actions(self, e):
        try:
            program_name = self.ctrl_v_field.value
            machine_type = self.selection_dropdown.value
            destination_folder = self.destination_field.value

            if not program_name or not machine_type:
                self.show_dialog("Eingabe fehlt", "Bitte Programmnamen und Maschinenart angeben.")
                return

            actions.action_1()
            actions.action_2()
            actions.action_3(program_name)
            actions.action_4(program_name)
            actions.action_5(machine_type)
            actions.action_6()
            actions.action_7(destination_folder)

        except Exception as e:
            self.show_dialog("Fehler", f"Fehler beim Ausführen der Aktionen: {e}")

    def move_files(self, e):
        at_prefix = self.at_prefix_field.value
        project_name = self.project_name_field.value
        if not at_prefix:
            self.status_label.value = "Fehler: Gebe AT- .. ein!"
            self.status_label.color = ft.Colors.RED_600
            self.page.update()
            return
        if not project_name:
            self.status_label.value = "Fehler: Projektnamen fehlt!"
            self.status_label.color = ft.Colors.RED_600
            self.page.update()
            return

        machines = ["HERMLE-C40", "HERMLE-C400", "DMU-EVO60", "DMU-100EVO", "DMC650V", "DMC1035V"]
        files_to_move = []
        for machine in machines:
            source_path = f"{base_path2}/{machine}/{base_path3}/*.h"
            machine_files = glob.glob(source_path)
            if not machine_files:
                self.status_label.value = f"Warnung: Keine Dateien zum Verschieben gefunden in {machine}!"
                self.status_label.color = ft.Colors.ORANGE_400
            else:
                files_to_move += machine_files

        if not files_to_move:
            self.status_label.value = "Fehler: Nichts gefunden und verschoben!"
            self.status_label.color = ft.Colors.RED_600
            self.page.update()
            return

        for machine in machines:
            source_path = f"{base_path2}/{machine}/{base_path3}/*.H"
            machine_files = glob.glob(source_path)
            if not machine_files:
                continue
            destination_path = f"{base_path2}/{machine}/AT{at_prefix}-{project_name}"
            if not os.path.exists(destination_path):
                os.mkdir(destination_path)
            for file_path in machine_files:
                shutil.copy2(file_path, destination_path)
                os.remove(file_path)

        self.status_label.value = "Programme verschoben!"
        self.status_label.color = ft.Colors.GREEN_600
        self.page.update()

    def check_dxf_files(self):
        ordner = ["HERMLE-C40", "HERMLE-C400", "DMU-EVO60", "DMU-100EVO", "DMC650V", "DMC1035V"]
        dxf_files = []
        for maschine in ordner:
            verzeichnis = f"{base_path2}/{maschine}/{base_path3}/*.H"
            dxf_files += glob.glob(verzeichnis)

        if dxf_files:
            status_text = f"Status: {len(dxf_files)} Programm(e) gefunden ;-)"
            self.status_label1.color = ft.Colors.GREEN_600
        else:
            status_text = "Status: Kein Programm gefunden!"
            self.status_label1.color = ft.Colors.RED_600

        self.status_label1.value = status_text
        self.page.update()

        self.page.run_task(self.delayed_check)

    async def delayed_check(self):
        await asyncio.sleep(1)
        self.check_dxf_files()

    def start_program(self, e):
        try:
            length = float(self.length_field.value)
            width = float(self.width_field.value)
            height = float(self.height_field.value)
            run_program(length, width, height)
        except ValueError:
            self.show_dialog("Fehler", "Ungültige Eingabe für Maße")
        except Exception as e:
            self.show_dialog("Fehler", f"Fehler beim Starten des Programms: {e}")

    def run_python_script(self, e):
        try:
            script_path = base_path5

            if self.script_process is not None and self.script_process.poll() is None:
                self.show_dialog("Info", "Prozess läuft bereits!")
                return

            self.script_process = subprocess.Popen(
                ["python", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.status_icon.color = ft.Colors.GREEN_600
            self.status_text.value = "Läuft"
            self.status_text.color = ft.Colors.GREEN_600
            self.page.update()

            self.page.run_task(self.monitor_process)

        except FileNotFoundError:
            self.show_dialog("Fehler", f"Skript nicht gefunden: {base_path5}")
        except Exception as e:
            self.show_dialog("Fehler", f"Fehler beim Starten des Skripts: {e}")

    def kill_python_script(self, e):
        if self.script_process is None:
            self.show_dialog("Info", "Kein Prozess läuft!")
            return

        try:
            if self.script_process.poll() is not None:
                self.show_dialog("Info", "Prozess ist bereits beendet!")
                self.reset_ui_to_stopped()
                return

            self.script_process.terminate()

            try:
                self.script_process.wait(timeout=3)
                print("Prozess erfolgreich beendet")
            except subprocess.TimeoutExpired:
                print("Prozess antwortet nicht, force kill...")
                self.script_process.kill()
                self.script_process.wait(timeout=2)

        except Exception as ex:
            print(f"Fehler beim Beenden: {ex}")
            try:
                import os, signal
                if hasattr(self.script_process, 'pid'):
                    os.kill(self.script_process.pid, signal.SIGTERM)
            except:
                pass
        finally:
            self.script_process = None
            self.reset_ui_to_stopped()

    def reset_ui_to_stopped(self):
        """Setzt die UI auf 'gestoppt' zurück"""
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.status_icon.color = ft.Colors.RED_600
        self.status_text.value = "Gestoppt"
        self.status_text.color = ft.Colors.RED_600
        self.page.update()

    async def monitor_process(self):
        """Überwacht den Prozess-Status"""
        while self.script_process is not None:
            if self.script_process.poll() is not None:
                print("Prozess wurde beendet")
                self.script_process = None
                self.reset_ui_to_stopped()
                break
            await asyncio.sleep(1)

    def start_external_flet_app(self, e):
        try:
            if not os.path.exists(PATH_TO_EXTERNAL_FLET_APP):
                self.show_dialog("Fehler", f"Externe Flet App nicht gefunden unter: {PATH_TO_EXTERNAL_FLET_APP}")
                return

            if self.external_flet_process is not None and self.external_flet_process.poll() is None:
                self.show_dialog("Info", "Externe Flet App läuft bereits!")
                return

            self.external_flet_process = subprocess.Popen(
                ["python", PATH_TO_EXTERNAL_FLET_APP],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            self.start_external_flet_button.disabled = True
            self.stop_external_flet_button.disabled = False
            self.external_flet_status_text.value = "Externe Flet App: Läuft"
            self.external_flet_status_text.color = ft.Colors.GREEN_700
            self.page.update()
            self.page.run_task(self.monitor_external_flet_process)

        except Exception as ex:
            self.show_dialog("Fehler", f"Fehler beim Starten der externen Flet App: {ex}")
            self.external_flet_status_text.value = f"Externe Flet App: Startfehler"
            self.external_flet_status_text.color = ft.Colors.RED_600
            self.start_external_flet_button.disabled = False
            self.stop_external_flet_button.disabled = True
            self.page.update()

    def stop_external_flet_app(self, e):
        if self.external_flet_process is None or self.external_flet_process.poll() is not None:
            self.show_dialog("Info", "Externe Flet App läuft nicht oder wurde bereits beendet.")
            self.reset_external_flet_ui_to_stopped()
            return

        try:
            self.external_flet_process.terminate()
            try:
                self.external_flet_process.wait(timeout=10)
                print("Externe Flet App erfolgreich via terminate() beendet.")
            except subprocess.TimeoutExpired:
                print("Externe Flet App reagiert nicht auf terminate(), versuche kill()...")
                self.external_flet_process.kill()
                self.external_flet_process.wait(timeout=2)
                print("Externe Flet App via kill() beendet.")
        except Exception as ex:
            self.show_dialog("Fehler", f"Problem beim Beenden der externen Flet App: {ex}")
            print(f"Fehler beim Stoppen der externen Flet App: {ex}")
        finally:
            self.external_flet_process = None
            self.reset_external_flet_ui_to_stopped()

    def reset_external_flet_ui_to_stopped(self):
        self.start_external_flet_button.disabled = False
        self.stop_external_flet_button.disabled = True
        self.external_flet_status_text.value = "Externe Flet App: Gestoppt"
        self.external_flet_status_text.color = "onsurfacevariant"
        self.page.update()

    async def monitor_external_flet_process(self):
        """Überwacht den externen Flet-Prozess-Status"""
        while self.external_flet_process is not None:
            if self.external_flet_process.poll() is not None:
                print("Externe Flet App wurde beendet.")
                self.external_flet_process = None
                self.reset_external_flet_ui_to_stopped()
                break
            await asyncio.sleep(1)

    def start_bseite(self, e):
        try:
            partheight_str = self.blength_field.value.replace(',', '.')
            if not partheight_str:
                self.show_dialog("Fehler", "Bitte Fertigteilhöhe für B-Seite eingeben.")
                return
            partheight = float(partheight_str)
            start_mausbewegungen(self.page, partheight)
        except ValueError:
            self.show_dialog("Fehler", "Ungültige Eingabe für Fertigteilhöhe. Bitte eine Zahl eingeben.")
        except Exception as ex:
            self.show_dialog("Fehler", f"Fehler beim Starten der B-Seite: {ex}")

    def load_step_file(self, e):
        file_name = self.ctrl_v_field.value.strip()
        if not file_name:
            self.show_dialog("UUUPS", "Gib einen Programmnamen ein.")
            return

        step_file_path = os.path.join(self.base_path4, f"{file_name}.step")
        stp_file_path = os.path.join(self.base_path4, f"{file_name}.stp")

        if os.path.isfile(step_file_path):
            file_path = step_file_path
        elif os.path.isfile(stp_file_path):
            file_path = stp_file_path
        else:
            self.show_dialog("UUUPS",
                             f"Die Datei '{file_name}.step' oder '{file_name}.stp' wurde im Ordner NC-Files nicht gefunden.")
            return

        try:
            result = process_step_file(file_path)
            original_size = result['original_size']
            raw_part_size = result['raw_part_size']
            result_text = (f"Originalgröße:\n"
                           f"X={original_size['X']:.2f}, Y={original_size['Y']:.2f}, Z={original_size['Z']:.2f}\n\n"
                           f"Rohteilgröße:\n"
                           f"X={raw_part_size['X']}, Y={raw_part_size['Y']}, Z={raw_part_size['Z']}")
            self.original_size_label.value = result_text

            self.length_field.value = f"{raw_part_size['X']}"
            self.width_field.value = f"{raw_part_size['Y']}"
            self.height_field.value = f"{raw_part_size['Z']}"
            self.value_field.value = f"{raw_part_size['Y']}"
            self.page.update()
        except Exception as e:
            self.show_dialog("Fehler", f"Fehler beim Laden der Datei: {e}")

    def update_dimensions_from_input(self, e):
        input_text = self.maße_field.value
        dimensions = input_text.split('*')
        if len(dimensions) == 3:
            try:
                length = float(dimensions[2])
                width = float(dimensions[0])
                height = float(dimensions[1])

                self.length_field.value = str(int(length)) if length.is_integer() else str(length)
                self.width_field.value = str(int(width)) if width.is_integer() else str(width)
                self.height_field.value = str(int(height)) if height.is_integer() else str(height)
                self.value_field.value = str(int(width)) if width.is_integer() else str(width)

                self.update_folder_selection(e)
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
    # Fensterkonfiguration
    page.title = "BMM 9.FLET by Gschwendtner Johannes"
    page.window.width = 600
    page.window.height = 1405
    page.window.resizable = True
    page.window.maximizable = True
    page.window.left = -5
    page.window.top = 0

    # NEU: Definition der Farbthemen mit deinen Hex-Codes
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#049fb4",  # Dein Haupt-Cyan
            primary_container="#e0f7fa",  # Ein sehr heller Cyan-Ton für Container-Hintergründe
            on_primary_container="#036f7e",  # Dein dunkler Cyan-Ton als Text auf hellen Containern
            secondary_container=ft.Colors.BLUE_GREY_200,
            on_secondary_container=ft.Colors.BLUE_GREY_900,
            outline_variant=ft.Colors.GREY_400,
        ),
        use_material3=True,
    )
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#05cfea",  # Dein hellster Cyan-Ton für gute Sichtbarkeit im Dark Mode
            primary_container="#036f7e",  # Dein dunkelster Cyan-Ton für Container-Hintergründe
            on_primary_container=ft.Colors.WHITE,  # Heller Text auf dem dunklen Container
            secondary_container=ft.Colors.BLUE_GREY_700,
            on_secondary_container=ft.Colors.BLUE_GREY_100,
            outline_variant=ft.Colors.GREY_700,
        ),
        use_material3=True,
    )

    # Passt sich automatisch dem OS-Modus (Light/Dark) an
    page.theme_mode = ft.ThemeMode.DARK

    app = BlankMakerApp(page)


if __name__ == '__main__':
    ft.app(target=main)