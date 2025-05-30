# Rohteil Master
import traceback

# Dieses Programm dient dazu, Rohteil-Rechtecke sowie Kreise und Spannmittel zu erstellen.
# Dazu ist es noch möglich, Esprit automatisch auszufüllen.
# Dieses Programm ersetzt vollständig den Total Commander!

# Zielpfad Änderung: ändere nur hier die Ordnerpfade!

# Autor: [Gschwendtner Johannes]
# Datum: [28.05.2025]
# Version: [7.8 - Flet Version]

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
from rohteilrechner import process_step_file
from kombiablauf import Kombiablauf
import winsound

# Startsound
notes = [
    (440, 300),  # A4
    (554, 300),  # C#5
    (659, 300),  # E5
    (880, 500)  # A5
]

for freq, dur in notes:
    winsound.Beep(freq, dur)

# Pfade zum Ändern
base_path1 = "C:\\Users\\Gschwendtner\\Desktop\\Spannmittel\\"  # Pfad für Spannmittelordner
base_path2 = "K:\\NC-PGM\\"  # NC-PGM Ausgabeordner Esprit
base_path3 = "WKS05"  # Auswahl von WKS Ordner
# base_path4 wird in init belegt
#base_path5 = "C:\\Users\\Gschwendtner\\Desktop\\Blank_Master_6.6\\prozess.pyw"  # Pfad für Prozessöffnen.py
base_path5 = "C:\\Users\\Gschwendtner\\PycharmProjects\\Blank_Maker_FLET\\prozess.pyw"

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

        self.base_path4 = f"K:\\Esprit\\NC-Files\\AT-25-KW{kalenderwoche}\\Gschwendtner\\{wochentag_ordner_num}.{wochentag_kuerzel}"

        self.history = []  # Für Zurück-Button
        self.updating = False  # Flag zur Vermeidung von rekursiven Aufrufen
        self.current_value = ""
        self.script_process = None

        # UI-Elemente erstellen
        self.create_ui_elements()
        self.folder_options = self.get_folder_options()
        self.folder_dropdown.options = [ft.dropdown.Option(folder) for folder in self.folder_options]

        self.build_ui()
        self.check_dxf_files()


    def create_ui_elements(self):
        # Eingabefelder
        self.length_field = ft.TextField(label="X Länge:", width=150, on_change=self.update_folder_selection)
        self.width_field = ft.TextField(label="Y Breite:", width=150, on_change=self.on_width_change)
        self.height_field = ft.TextField(label="Z Höhe:", width=150)
        self.diameter_field = ft.TextField(label="Durchmesser:", width=150)
        self.height2_field = ft.TextField(label="Höhe:", width=150)
        self.value_field = ft.TextField(label="Wert in mm:", width=300)
        self.ctrl_v_field = ft.TextField(label="Text für CTRL+V eingeben:", width=300)
        self.at_prefix_field = ft.TextField(label="AT-..", value="25", width=100)
        self.project_name_field = ft.TextField(label="Projektname: zB.0815", width=200, max_length=4,
                                               on_change=self.on_entry_change)
        self.destination_field = ft.TextField(label="Zielordner:", width=500, value=self.base_path4)
        self.blength_field = ft.TextField(label="Fertigteilhöhe:", width=150)
        self.maße_field = ft.TextField(label="Rohteil Maße (L*B*H):", width=300,
                                       on_change=self.update_dimensions_from_input)

        # Dropdown-Menüs
        self.folder_dropdown = ft.Dropdown(
            label="Ordner auswählen:",
            width=300,
            options=[]
        )

        self.selection_dropdown = ft.Dropdown(
            label="Maschienenart:",
            width=300,
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

        # Status Labels - Fixed deprecated color usage
        self.status_label = ft.Text("", size=12, color=ft.Colors.GREEN)
        self.status_label1 = ft.Text("", size=12, color=ft.Colors.BLUE)
        self.original_size_label = ft.Text("", size=8)



    def build_ui(self):
        # UI Layout erstellen
        self.page.add(
            ft.Column([
                # Programmname Sektion
                ft.Text("Programmname:", size=14, weight=ft.FontWeight.BOLD),
                self.ctrl_v_field,
                self.selection_dropdown,

                ft.Divider(height=20),

                # Rohteil Maße Eingabe
                ft.Row([
                    ft.Text("Erzeuge Rechteck", size=14, weight=ft.FontWeight.BOLD),
                    #self.maße_field,
                    #ft.ElevatedButton("STEP Analyse", on_click=self.load_step_file,
                                      #tooltip="Sucht nach Eingabe von Programmnamen die STEP-Datei und berechnet Fertigteilgröße und Rohteilgröße.")
                ]),

                # Rechteck Eingabefelder
                ft.Row([self.length_field, self.width_field, self.height_field]),
                ft.ElevatedButton("MAKE ..", on_click=self.create_rect),
                self.original_size_label,

                ft.Divider(height=10),

                # Kreis Sektion
                ft.Text("Erzeuge Kreis", size=14, weight=ft.FontWeight.BOLD),
                ft.Row([self.diameter_field, self.height2_field]),
                ft.ElevatedButton("MAKE ..", on_click=self.create_circle),

                ft.Divider(height=10),

                # Spannmittel Sektion
                ft.Text("Spannmittel Auswahl:", size=14, weight=ft.FontWeight.BOLD),
                self.value_field,
                self.folder_dropdown,
                ft.Text("Zielordner:"),
                self.destination_field,
                ft.ElevatedButton("Schraubstock erstellen", on_click=self.copy_file),


                # Button Kombiablauf mit Play-Icon
                ft.Container(
                    content=ft.ElevatedButton(
                        text="Kombiablauf Starten",
                        icon=ft.Icons.PLAY_CIRCLE_FILL,  # aktualisierte Enum-Variante
                        on_click=self.start_kombiablauf,
                        width=300,
                        height=40,
                        style=ft.ButtonStyle(
                            bgcolor="#ADD8E6",  # Pastellgrün
                            color=ft.Colors.BLACK,
                            shape=ft.RoundedRectangleBorder(radius=5),
                            padding=10,
                            elevation=5
                        ),
                        tooltip="Auto Ausfüllen, Laden der DXF u. Schraubstockes, Pause:-) , Rohteil Definierung und Erstellung."
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=10)
                ),

                ft.Divider(height=20),

                # B-Seite
                ft.Row([
                    self.blength_field,
                    ft.ElevatedButton("B-Start", on_click=self.start_bseite)
                ]),

                ft.Divider(height=20),

                #Python Commander aufgeteilt auf links und rechts
                ft.Row(
                    controls=[
                        # Linke Spalte: Python Commander
                        ft.Column(
                            controls=[
                                ft.Text("PythonCommander:", size=12, weight=ft.FontWeight.BOLD),
                                ft.Row([
                                    self.at_prefix_field,
                                    ft.ElevatedButton("switch reloaded", on_click=self.toggle_value)
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


                # Button Programm Ausgeben mit Play-Icon in Rot
                ft.Container(
                    content=ft.ElevatedButton(
                        text="PROGRAMM AUSGEBEN",
                        icon=ft.Icons.SAVE,
                        on_click=self.move_files,
                        width=300,
                        height=40,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.RED,  # kräftiges Rot
                            color=ft.Colors.WHITE,  # weiße Schrift
                            shape=ft.RoundedRectangleBorder(radius=5),
                            padding=10,
                            elevation=5,
                            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                        ),
                        tooltip="Gibt das fertige Programm aus und kopiert die Daten in die Ablage."
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=20)
                ),

                ft.Divider(height=20),

                # Prozess Buttons - Fixed deprecated color usage #############################################
                ft.Text("Prozess Öffnen:", size=12, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.ElevatedButton(
                        "Prozess Start",
                        on_click=self.run_python_script,
                        bgcolor=ft.Colors.GREEN,
                        color=ft.Colors.WHITE,
                        disabled=self.script_process is not None
                    ),
                    ft.ElevatedButton(
                        "Prozess Stop",
                        on_click=self.kill_python_script,
                        bgcolor=ft.Colors.RED,
                        color=ft.Colors.WHITE,
                        disabled=self.script_process is None
                    )
                ]),
                ##############################################################################################
            ],
                scroll=ft.ScrollMode.ADAPTIVE,  # Besseres Scroll
                expand=True,  # Column soll verfügbaren Platz ausfüllen
            )
        )

    # Event Handler Funktionen
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
        # Übergebe self.page und die Flet-Steuerelemente
        kombi = Kombiablauf(self.page, # Hinzugefügt: Die Flet Page Instanz
                           self.ctrl_v_field,
                           self.selection_dropdown,
                           self.destination_field,
                           self.length_field,
                           self.width_field,
                           self.height_field)
        try:
            kombi.kombiablauf()
        except Exception as ex_kombi_start:
            # Falls kombiablauf() selbst eine Exception wirft, bevor die interne Fehlerbehandlung greift
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
            self.action_1()
            self.action_2()
            self.action_3()
            self.action_4()
            self.action_5()
            self.action_6()
            self.action_7()
        except Exception as e:
            self.show_dialog("Fehler", f"Fehler beim Ausführen der Aktionen: {e}")

    def action_1(self):
        image_position = pyscreeze.locateOnScreen('Bilder/1.png', confidence=0.5)
        image_center = pyscreeze.center(image_position)
        time.sleep(0.5)
        pyautogui.click(image_center)
        time.sleep(0.5)

    def action_2(self):
        image_position = pyscreeze.locateOnScreen('Bilder/2.png', confidence=0.4)
        image_center = pyscreeze.center(image_position)
        time.sleep(0.9)
        pyautogui.click(image_center)

    def action_3(self):
        image_position = pyscreeze.locateOnScreen('Bilder/3.png', confidence=0.5, grayscale=True)
        image_center = pyscreeze.center(image_position)
        time.sleep(0.4)
        pyautogui.doubleClick(image_center)
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.1)
        text = self.ctrl_v_field.value + '_A'
        pyautogui.typewrite(text)
        time.sleep(0.1)

    def action_4(self):
        pyautogui.press('tab')
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
        text = self.ctrl_v_field.value
        pyautogui.typewrite(text)
        time.sleep(0.1)

    def action_5(self):
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        time.sleep(0.1)
        text = self.selection_dropdown.value
        pyautogui.typewrite(text)
        time.sleep(0.1)

    def action_6(self):
        pyautogui.press('enter')
        time.sleep(0.1)

    def action_7(self):
        wegzeit1 = 0.4
        pfad_rohteil = os.path.join(self.destination_field.value, "!rohteil.dxf")
        pfad_schraubstock = os.path.join(self.destination_field.value, "!schraubstock.step")
        pyautogui.doubleClick(974, 1047, duration=wegzeit1)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(0.5)
        pyautogui.typewrite(pfad_rohteil)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(0.5)
        pyautogui.doubleClick(977, 1142, duration=wegzeit1)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(0.8)
        pyautogui.typewrite(pfad_schraubstock)
        time.sleep(0.8)
        pyautogui.press('enter')

    def move_files(self, e):
        at_prefix = self.at_prefix_field.value
        project_name = self.project_name_field.value
        if not at_prefix:
            self.status_label.value = "Fehler: Gebe AT- .. ein!"
            self.status_label.color = ft.Colors.RED
            self.page.update()
            return
        if not project_name:
            self.status_label.value = "Fehler: Projektnamen fehlt!"
            self.status_label.color = ft.Colors.RED
            self.page.update()
            return

        machines = ["HERMLE-C40", "HERMLE-C400", "DMU-EVO60", "DMU-100EVO", "DMC650V", "DMC1035V"]
        files_to_move = []
        for machine in machines:
            source_path = f"{base_path2}/{machine}/{base_path3}/*.h"
            machine_files = glob.glob(source_path)
            if not machine_files:
                self.status_label.value = f"Warnung: Keine Dateien zum Verschieben gefunden in {machine}!"
                self.status_label.color = ft.Colors.ORANGE
            else:
                files_to_move += machine_files

        if not files_to_move:
            self.status_label.value = "Fehler: Nichts gefunden und verschoben!"
            self.status_label.color = ft.Colors.RED
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
        self.status_label.color = ft.Colors.GREEN
        self.page.update()

    def check_dxf_files(self):
        ordner = ["HERMLE-C40", "HERMLE-C400", "DMU-EVO60", "DMU-100EVO", "DMC650V", "DMC1035V"]
        dxf_files = []
        for maschine in ordner:
            verzeichnis = f"{base_path2}/{maschine}/{base_path3}/*.H"
            dxf_files += glob.glob(verzeichnis)

        if dxf_files:
            status_text = f"Status: {len(dxf_files)} Programm(e) gefunden ;-)"
            self.status_label1.color = ft.Colors.GREEN
        else:
            status_text = "Status: Kein Programm gefunden!"
            self.status_label1.color = ft.Colors.RED

        self.status_label1.value = status_text
        self.page.update()

        # Timer für nächste Überprüfung
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
            self.script_process = subprocess.Popen(["python", script_path],
                                                   stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE,
                                                   stdin=subprocess.PIPE,
                                                   creationflags=subprocess.CREATE_NO_WINDOW)
            self.update()
        except Exception as e:
            self.show_dialog("Fehler", f"Fehler beim Starten des Skripts: {e}")

    def kill_python_script(self, e):
        if self.script_process is not None:
            self.script_process.kill()
            self.script_process = None
            self.update()

    def start_bseite(self, e):
        try:
            partheight_str = self.blength_field.value.replace(',', '.')
            if not partheight_str:
                self.show_dialog("Fehler", "Bitte Fertigteilhöhe für B-Seite eingeben.")
                return
            partheight = float(partheight_str)

            # Übergebe self.page an start_mausbewegungen
            start_mausbewegungen(self.page, partheight) # NEU: self.page übergeben

            # Optional: Eine kleine Bestätigung im Hauptfenster, dass der Prozess gestartet wurde,
            # da der eigentliche Dialog erst am Ende von start_mausbewegungen erscheint.
            # self.show_dialog("Info", "B-Seiten Automatisierung gestartet...")

        except ValueError:
            self.show_dialog("Fehler", "Ungültige Eingabe für Fertigteilhöhe. Bitte eine Zahl eingeben.")
        except Exception as ex: # Fange auch andere Fehler ab, die von start_mausbewegungen kommen könnten
            self.show_dialog("Fehler", f"Fehler beim Starten der B-Seite: {ex}")
            #traceback.print_exc() # Gibt den vollen Traceback in der Konsole aus

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

            # Füllen der Eingabefelder mit Ganzzahlen
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

    # KORREKTUR: Verwende page.window statt direkter Attribute
    page.window.width = 600
    page.window.height = 1400
    page.window.resizable = True
    page.window.maximizable = True
    page.window.left = 0
    page.window.top = 0

    # Zentrierung
    #page.window.center()

    page.theme_mode = ft.ThemeMode.LIGHT
    app = BlankMakerApp(page)


if __name__ == '__main__':
    ft.app(target=main)
