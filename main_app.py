import flet as ft
import config
from ui.elements import create_all_ui_elements
from ui.layout import build_main_ui
from core.event_handlers import EventHandlersBase # Angepasster Import


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
        self.base_path4 = config.BASE_PATH4 # Wird in ui.elements für destination_field verwendet

        # --- UI-Erstellung (Widgets werden an self gebunden) ---
        create_all_ui_elements(self) # Übergibt die aktuelle Instanz

        # --- Event-Handler Initialisierung (ruft Methoden aus EventHandlersBase) ---
        super().__init__() # Wichtig: Initialisiert die Basisklasse korrekt, falls sie einen eigenen __init__ hätte
                           # In diesem Fall werden Methoden wie get_folder_options direkt aufgerufen.

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
    page.title = "BMM 10.FLET by Gschwendtner Johannes" # Versionsnummer angepasst
    page.window.width = 680
    page.window.height = 1200
    page.window.resizable = True
    page.window.maximizable = True
    page.window.left = -5
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
    page.theme_mode = ft.ThemeMode.DARK

    # --- App-Instanz erstellen und ausführen ---
    app = BlankMakerApp(page)
    # Die Page wird durch das `app` Objekt bereits initialisiert und aufgebaut.

if __name__ == '__main__':
    ft.app(target=main)