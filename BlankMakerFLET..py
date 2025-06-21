#BlankMakerFLET.py
import flet as ft
import config
from ui_elements import create_all_ui_elements
from ui_layout import build_main_ui
from event_handlers import EventHandlersBase



class BlankMakerApp(EventHandlersBase): # Erbt von EventHandlersBase
    """
    Die Hauptanwendungsklasse für den Blank Maker.
    Sie kapselt die gesamte UI-Logik und die Anwendungsfunktionalität.
    """

    def __init__(self, page: ft.Page):
        self.page = page

        # --- Initialisierung der Anwendungszustände ---
        self.history = []
        self.updating = False
        self.current_value = ""
        self.script_process = None
        self.external_flet_process = None

        # --- Datumsabhängige Pfade dynamisch erstellen ---
        # BASE_PATH4 wird jetzt direkt von config geladen
        self.base_path4 = config.BASE_PATH4 # Wird in create_all_ui_elements für destination_field verwendet

        # --- UI-Erstellung (Widgets werden an self gebunden) ---
        create_all_ui_elements(self) # Übergibt die aktuelle Instanz

        # --- Ordneroptionen laden (nachdem UI-Elemente erstellt wurden) ---
        self.folder_options = self.get_folder_options() # Methode aus EventHandlersBase
        if self.folder_options: # Nur wenn Optionen vorhanden sind
             self.folder_dropdown.options = [ft.dropdown.Option(folder) for folder in self.folder_options]
        else:
            self.folder_dropdown.options = [ft.dropdown.Option(key="no_options", text="Keine Ordner gefunden")]
            self.folder_dropdown.hint_text = "Keine Ordneroptionen geladen"


        # --- UI-Layout aufbauen ---
        build_main_ui(self) # Übergibt die aktuelle Instanz

        # --- Asynchrone Aufgabe starten ---
        self.page.run_task(self.continuously_check_dxf_files) # Methode aus EventHandlersBase


def main(page: ft.Page):
    # --- Fensterkonfiguration ---
    page.title = "BMM 9.FLET by Gschwendtner Johannes"
    page.window.width = 600
    page.window.height = 950 # Angepasst, um Scrollen zu reduzieren, je nach Inhalt anpassen
    page.window.resizable = True
    page.window.maximizable = True
    page.window.left = -5 # Kann zu Problemen auf manchen Systemen führen, ggf. anpassen oder entfernen
    page.window.top = 0

    # --- Definition der Farbthemen (Light & Dark) ---
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
            on_surface=ft.Colors.WHITE,
        ),
        use_material3=True,
    )
    page.theme_mode = ft.ThemeMode.LIGHT # Oder ft.ThemeMode.SYSTEM

    # --- App-Instanz erstellen und ausführen ---
    app = BlankMakerApp(page)
    # Die Page wird durch das `app` Objekt bereits initialisiert und aufgebaut.
    # page.add() ist nicht mehr nötig, da build_main_ui dies bereits tut.

if __name__ == '__main__':
    ft.app(target=main)