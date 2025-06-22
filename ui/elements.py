import flet as ft


def create_all_ui_elements(app_instance):
    """
    Erstellt verbesserte UI-Elemente mit modernem Design.
    """
    # --- Design System ---
    textfield_style = {
        "filled": True,
        "bgcolor": ft.Colors.with_opacity(0.08, ft.Colors.ON_SURFACE),
        "border": ft.InputBorder.OUTLINE,
        "border_radius": 8,
        "border_color": ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE),
        "focused_border_color": ft.Colors.PRIMARY,
        "dense": True,
        "content_padding": ft.padding.symmetric(horizontal=12, vertical=8),
    }

    dropdown_style = {
        "filled": True,
        "bgcolor": ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
        "border": ft.InputBorder.OUTLINE,
        "border_radius": 8,
        "border_color": ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY),
        "focused_border_color": ft.Colors.PRIMARY,
        "dense": True,
        "content_padding": ft.padding.symmetric(horizontal=12, vertical=8),
    }

    primary_button_style = ft.ButtonStyle(
        bgcolor=ft.Colors.PRIMARY,
        color=ft.Colors.ON_PRIMARY,
        elevation=2,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        shape=ft.RoundedRectangleBorder(radius=6),
        text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_500)
    )

    secondary_button_style = ft.ButtonStyle(
        bgcolor=ft.Colors.SECONDARY,
        color=ft.Colors.ON_SECONDARY,
        elevation=1,
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        shape=ft.RoundedRectangleBorder(radius=6),
        text_style=ft.TextStyle(size=11, weight=ft.FontWeight.W_500)
    )

    # --- Eingabefelder ---
    # Rohteil Felder
    app_instance.length_field = ft.TextField(
        label="X Länge",
        width=120,
        on_change=app_instance.update_folder_selection,
        **textfield_style
    )
    app_instance.width_field = ft.TextField(
        label="Y Breite",
        width=120,
        on_change=app_instance.on_width_change,
        **textfield_style
    )
    app_instance.height_field = ft.TextField(
        label="Z Höhe",
        width=120,
        **textfield_style
    )

    # Kreis Felder
    app_instance.diameter_field = ft.TextField(
        label="Durchmesser",
        width=140,
        **textfield_style
    )
    app_instance.height2_field = ft.TextField(
        label="Höhe",
        width=140,
        **textfield_style
    )

    # Spannmittel Felder
    app_instance.value_field = ft.TextField(
        label="Y Spannweite",
        width=300,
        **textfield_style
    )

    # Projekt Felder
    app_instance.ctrl_v_field = ft.TextField(
        label="Zeichnungsnummer",
        width=300,
        **textfield_style
    )
    app_instance.at_prefix_field = ft.TextField(
        label="AT",
        value="25",
        width=80,
        **textfield_style
    )
    app_instance.project_name_field = ft.TextField(
        label="Projekt-Nr",
        width=140,
        max_length=4,
        on_change=app_instance.on_entry_change,
        **textfield_style
    )

    # Ziel- und B-Seite Felder
    app_instance.destination_field = ft.TextField(
        label="Zielordner Pfad",
        width=600,
        value=str(app_instance.base_path4),
        **textfield_style
    )
    app_instance.blength_field = ft.TextField(
        label="Fertigteilhöhe B-Seite",
        width=200,
        **textfield_style
    )

    # --- Dropdown-Menüs ---
    app_instance.folder_dropdown = ft.Dropdown(
        label="Spannmittel Ordner",
        width=300,
        options=[],
        **dropdown_style
    )
    app_instance.selection_dropdown = ft.Dropdown(
        label="Maschinenart",
        width=300,
        value="Option",
        options=[
            ft.dropdown.Option('5 Achs  3 Achs'),
            ft.dropdown.Option('5 Achs  5 Achs'),
            ft.dropdown.Option('3 Achs  3 Achs'),
            ft.dropdown.Option('5 Achs'),
            ft.dropdown.Option('3 Achs')
        ],
        on_change=app_instance.update_folder_selection,
        **dropdown_style
    )

    # --- MAKE Buttons ---
    app_instance.rect_make_button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.ADD_BOX, size=16),
            ft.Text("MAKE Rechteck")
        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        on_click=app_instance.handle_rect_creation,
        style=primary_button_style,
        tooltip="Rechteckiges Rohteil erstellen"
    )

    app_instance.circle_make_button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.ADD_CIRCLE, size=16),
            ft.Text("MAKE Kreis")
        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        on_click=app_instance.handle_circle_creation,
        style=primary_button_style,
        tooltip="Rundes Rohteil erstellen"
    )

    app_instance.vice_create_button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.BUILD, size=16),
            ft.Text("MAKE Schraubstock")
        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        on_click=app_instance.handle_vice_creation,
        style=primary_button_style,
        tooltip="Schraubstock-Spannmittel erstellen"
    )

    # --- Navigations-Buttons ---
    app_instance.back_button = ft.ElevatedButton(
        "Zurück",
        on_click=app_instance.go_back,
        disabled=True,
        style=secondary_button_style
    )

    # --- Prozess-Control Buttons ---
    app_instance.start_button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.PLAY_ARROW, size=16),
            ft.Text("Start")
        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        on_click=app_instance.run_prozess_listener_script_ui_toggle,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
            elevation=3,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            shape=ft.RoundedRectangleBorder(radius=6)
        ),
        tooltip="F12-Listener Prozess starten"
    )

    app_instance.stop_button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.STOP, size=16),
            ft.Text("Stop")
        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        on_click=app_instance.kill_prozess_listener_script_ui_toggle,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.RED_700,
            color=ft.Colors.WHITE,
            elevation=3,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            shape=ft.RoundedRectangleBorder(radius=6)
        ),
        disabled=True,
        tooltip="F12-Listener Prozess stoppen"
    )

    app_instance.start_external_flet_button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.LAUNCH, size=16),
            ft.Text("Start OCR")
        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        on_click=app_instance.start_external_flet_app_ui_toggle,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN_800,
            color=ft.Colors.WHITE,
            elevation=3,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            shape=ft.RoundedRectangleBorder(radius=6)
        ),
        tooltip="Externe OCR App starten"
    )

    # --- Export Button (Haupt-Action) ---
    app_instance.export_button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.SAVE_ALT, size=20),
            ft.Text("PROGRAMM AUSGEBEN", size=16, weight=ft.FontWeight.BOLD)
        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
        on_click=app_instance.animate_and_move_files,
        width=320,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.RED_600,
            color=ft.Colors.WHITE,
            elevation=6,
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            shape=ft.RoundedRectangleBorder(radius=8),
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
        ),
        tooltip="Fertige Programme ausgeben und verschieben"
    )
    app_instance.export_button.animate_bgcolor = ft.Animation(
        duration=2500,
        curve=ft.AnimationCurve.EASE_IN_OUT
    )

    # --- Status-Anzeigen ---
    app_instance.status_label = ft.Text(
        "",
        size=12,
        color=ft.Colors.ON_SURFACE_VARIANT
    )
    app_instance.dxf_status_container = ft.Row(
        controls=[],
        wrap=True,
        spacing=4,
        run_spacing=4
    )
    app_instance.status_icon = ft.Icon(
        ft.Icons.CIRCLE,
        color=ft.Colors.RED_600,
        size=16
    )
    app_instance.status_text = ft.Text(
        "Gestoppt",
        size=11,
        color=ft.Colors.RED_600,
        weight=ft.FontWeight.W_500
    )
    app_instance.external_flet_status_text = ft.Text(
        "OCR App: Gestoppt",
        size=11,
        color=ft.Colors.ON_SURFACE_VARIANT,
        text_align=ft.TextAlign.CENTER
    )

    # --- Progress Bars ---
    progress_bar_style = {
        "width": 200,
        "height": 4,
        "visible": False,
        "border_radius": 2,
        "color": ft.Colors.PRIMARY,
        "bgcolor": ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY)
    }

    app_instance.rect_progress = ft.ProgressBar(**progress_bar_style)
    app_instance.circle_progress = ft.ProgressBar(**progress_bar_style)
    app_instance.vice_progress = ft.ProgressBar(**progress_bar_style)