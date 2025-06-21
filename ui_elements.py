#ui_elements.py
import flet as ft
import config # Importiere die Konfigurationsdatei

def create_all_ui_elements(app_instance):
    """
    Erstellt und konfiguriert alle UI-Widgets und weist sie der app_instance zu.
    Das Design wird hier zentral definiert.
    """
    # app_instance ist die Instanz von BlankMakerApp

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
    app_instance.length_field = ft.TextField(label="X Länge:", width=150, on_change=app_instance.update_folder_selection, **textfield_style)
    app_instance.width_field = ft.TextField(label="Y Breite:", width=150, on_change=app_instance.on_width_change, **textfield_style)
    app_instance.height_field = ft.TextField(label="Z Höhe:", width=150, **textfield_style)
    app_instance.diameter_field = ft.TextField(label="Durchmesser:", width=150, **textfield_style)
    app_instance.height2_field = ft.TextField(label="Höhe:", width=150, **textfield_style)
    app_instance.value_field = ft.TextField(label="Wert in mm:", width=300, **textfield_style)
    app_instance.ctrl_v_field = ft.TextField(label="Text für CTRL+V eingeben:", width=300, **textfield_style)
    app_instance.at_prefix_field = ft.TextField(label="AT-..", value="25", width=100, **textfield_style)
    app_instance.project_name_field = ft.TextField(label="Projektname: zB.0815", width=200, max_length=4, on_change=app_instance.on_entry_change, **textfield_style)
    # Verwende BASE_PATH4 von der app_instance, die es aus config initialisiert hat
    app_instance.destination_field = ft.TextField(label="Zielordner:", width=500, value=str(app_instance.base_path4), **textfield_style)
    app_instance.blength_field = ft.TextField(label="Fertigteilhöhe:", width=150, **textfield_style)
    app_instance.maße_field = ft.TextField(label="Rohteil Maße (L*B*H):", width=300, on_change=app_instance.update_dimensions_from_input, **textfield_style)

    # --- Dropdown-Menüs ---
    app_instance.folder_dropdown = ft.Dropdown(label="Ordner auswählen:", width=300, options=[], **dropdown_style)
    app_instance.selection_dropdown = ft.Dropdown(
        label="Maschinenart:", width=300, value="Option",
        options=[
            ft.dropdown.Option('5 Achs  3 Achs'), ft.dropdown.Option('5 Achs  5 Achs'),
            ft.dropdown.Option('3 Achs  3 Achs'), ft.dropdown.Option('5 Achs'), ft.dropdown.Option('3 Achs')
        ],
        on_change=app_instance.update_folder_selection, **dropdown_style
    )

    # --- Buttons ---
    app_instance.back_button = ft.ElevatedButton("Zurück", on_click=app_instance.go_back, disabled=True)
    app_instance.rect_make_button = ft.ElevatedButton("MAKE ..", on_click=app_instance.handle_rect_creation)
    app_instance.circle_make_button = ft.ElevatedButton("MAKE ..", on_click=app_instance.handle_circle_creation)
    app_instance.vice_create_button = ft.ElevatedButton("Schraubstock erstellen", on_click=app_instance.handle_vice_creation)
    app_instance.start_button = ft.ElevatedButton("Prozess Start", on_click=app_instance.run_python_script, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
    app_instance.stop_button = ft.ElevatedButton("Prozess Stop", on_click=app_instance.kill_python_script, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, disabled=True)
    app_instance.start_external_flet_button = ft.ElevatedButton("Externe Flet App STARTEN", on_click=app_instance.start_external_flet_app, bgcolor=ft.Colors.GREEN_800, color=ft.Colors.WHITE)
    app_instance.stop_external_flet_button = ft.ElevatedButton("Externe Flet App STOPPEN", on_click=app_instance.stop_external_flet_app, bgcolor=ft.Colors.RED_800, color=ft.Colors.WHITE, disabled=True)

    app_instance.export_button = ft.ElevatedButton(
        text="PROGRAMM AUSGEBEN", icon=ft.Icons.SAVE, on_click=app_instance.animate_and_move_files, width=300, height=40,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=5),
            padding=10, elevation=5, text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
        ),
        tooltip="Gibt die fertigen Programme aus."
    )
    app_instance.export_button.animate_bgcolor = ft.Animation(duration=2500, curve=ft.AnimationCurve.EASE_IN_OUT)

    # --- Status-Anzeigen und Prozessleisten ---
    app_instance.status_label = ft.Text("", size=15)
    app_instance.dxf_status_container = ft.Row(controls=[], wrap=True, spacing=2)
    app_instance.original_size_label = ft.Text("", size=8)
    app_instance.status_icon = ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.RED_600, size=25)
    app_instance.status_text = ft.Text("Gestoppt", size=12, color=ft.Colors.RED_600)
    app_instance.external_flet_status_text = ft.Text("Externe Flet App: Gestoppt", size=12, color="onsurfacevariant")

    progress_bar_style = {"width": 200, "height": 10, "visible": False, "border_radius": 5}
    app_instance.rect_progress = ft.ProgressBar(**progress_bar_style)
    app_instance.circle_progress = ft.ProgressBar(**progress_bar_style)
    app_instance.vice_progress = ft.ProgressBar(**progress_bar_style)