import flet as ft


def build_main_ui(app_instance):
    """
    Verbessertes UI-Layout mit optimierter Struktur und schönerem Design.
    """
    # --- Design System ---
    card_style = {
        "padding": ft.padding.all(12),
        "border_radius": 8,
        "border": ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE)),
        "bgcolor": ft.Colors.with_opacity(0.02, ft.Colors.ON_SURFACE)
    }

    primary_card_style = {
        "padding": ft.padding.all(12),
        "border_radius": 8,
        "bgcolor": ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
        "border": ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY))
    }

    # --- Header: Zielordner (ganz oben) ---
    header_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.FOLDER_OUTLINED, size=20, color=ft.Colors.PRIMARY),
                ft.Text("Zielordner:", weight=ft.FontWeight.W_600, size=13, color=ft.Colors.PRIMARY),
            ], spacing=8),
            app_instance.destination_field,
        ], spacing=6),
        **primary_card_style
    )

    # --- Sektion 1: Projektdaten ---
    project_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ENGINEERING_OUTLINED, size=18),
                ft.Text("Projektdaten", weight=ft.FontWeight.W_600, size=14),
            ], spacing=8),
            ft.Row([
                app_instance.ctrl_v_field,
                app_instance.selection_dropdown,
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=8),
        **card_style
    )

    # --- Sektion 2: Rohteil Erstellung ---
    rect_tab_content = ft.Container(
        content=ft.Column([
            ft.Row([
                app_instance.length_field,
                app_instance.width_field,
                app_instance.height_field
            ], spacing=8),
            ft.Row([
                app_instance.rect_make_button,
                app_instance.rect_progress
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=10),
        padding=8
    )

    circle_tab_content = ft.Container(
        content=ft.Column([
            ft.Row([
                app_instance.diameter_field,
                app_instance.height2_field
            ], spacing=8),
            ft.Row([
                app_instance.circle_make_button,
                app_instance.circle_progress
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=10),
        padding=8
    )

    rohteil_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CATEGORY_OUTLINED, size=18),
                ft.Text("Rohteil Erstellung", weight=ft.FontWeight.W_600, size=14),
            ], spacing=8),
            ft.Tabs(
                selected_index=0,
                animation_duration=200,
                height=160,
                indicator_color=ft.Colors.PRIMARY,
                label_color=ft.Colors.PRIMARY,
                unselected_label_color=ft.Colors.ON_SURFACE_VARIANT,
                tabs=[
                    ft.Tab(
                        text="Rechteck",
                        icon=ft.Icons.RECTANGLE_OUTLINED,
                        content=rect_tab_content
                    ),
                    ft.Tab(
                        text="Kreis",
                        icon=ft.Icons.CIRCLE_OUTLINED,
                        content=circle_tab_content
                    ),
                ],
            ),
        ], spacing=5),
        **card_style
    )

    # --- Sektion 3: Spannmittel (optimiert nach Ihren Wünschen) ---
    spannmittel_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PRECISION_MANUFACTURING_OUTLINED, size=18),
                ft.Text("Spannmittel", weight=ft.FontWeight.W_600, size=14),
            ], spacing=8),
            # Erste Zeile: Y mm Eingabe mit Dropdown daneben
            ft.Row([
                app_instance.value_field,
                app_instance.folder_dropdown,
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            # Zweite Zeile: MAKE Schraubstock Button
            ft.Container(
                content=ft.Column([
                    app_instance.vice_create_button,
                    app_instance.vice_progress
                ], spacing=4),
                expand=False
            )
        ], spacing=10),
        **card_style
    )

    # --- Sektion 4: Hauptaktionen ---
    actions_section = ft.Container(
        content=ft.Column([
            # Kombiablauf (prominent)
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PLAY_CIRCLE_FILLED, size=20),
                        ft.Text("Kombiablauf starten", size=14, weight=ft.FontWeight.W_600)
                    ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                    on_click=app_instance.start_kombiablauf_workflow,
                    height=48,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY,
                        elevation=4,
                        padding=ft.padding.symmetric(horizontal=24, vertical=12),
                        shape=ft.RoundedRectangleBorder(radius=8)
                    )
                ),
                alignment=ft.alignment.center
            ),
            # B-Seite Bearbeitung
            ft.Row([
                app_instance.blength_field,
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.FLIP_CAMERA_ANDROID, size=16),
                        ft.Text("B-Start", size=12)
                    ], spacing=4),
                    on_click=app_instance.start_bseite_automation_ui_toggle,
                    height=36,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.SECONDARY,
                        color=ft.Colors.ON_SECONDARY,
                        padding=ft.padding.symmetric(horizontal=16, vertical=8),
                        shape=ft.RoundedRectangleBorder(radius=6)
                    )
                ),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=16),
        **primary_card_style
    )

    # --- Sektion 5: NC-Ausgabe & Status ---
    nc_status_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CODE_OUTLINED, size=18),
                ft.Text("NC-Ausgabe & Status", weight=ft.FontWeight.W_600, size=14),
            ], spacing=8),
            ft.Row([
                # Linke Spalte: NC-Ausgabe
                ft.Column([
                    ft.Row([app_instance.at_prefix_field, app_instance.project_name_field], spacing=8),
                    ft.Row([
                        ft.ElevatedButton(
                            "Switch AT",
                            on_click=app_instance.toggle_value,
                            height=32,
                            style=ft.ButtonStyle(
                                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                text_style=ft.TextStyle(size=11)
                            )
                        ),
                        app_instance.back_button
                    ], spacing=8),
                ], spacing=8, expand=True),

                # Rechte Spalte: Status
                ft.Column([
                    app_instance.status_label,
                    app_instance.dxf_status_container,
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.END, expand=True)
            ], vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=10),
        **card_style
    )

    # --- Export Button (prominent) ---
    export_section = ft.Container(
        content=app_instance.export_button,
        alignment=ft.alignment.center,
        padding=ft.padding.symmetric(vertical=12)
    )

    # --- Sektion 6: Externe Prozesse ---
    processes_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SETTINGS_APPLICATIONS_OUTLINED, size=18),
                ft.Text("Externe Prozesse", weight=ft.FontWeight.W_600, size=14),
            ], spacing=8),
            ft.Row([
                # F12-Listener
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.KEYBOARD, size=16),
                            ft.Text("F12-Listener", size=12, weight=ft.FontWeight.W_500)
                        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            app_instance.start_button,
                            app_instance.stop_button
                        ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            app_instance.status_icon,
                            app_instance.status_text
                        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=12,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE)),
                    border_radius=6,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
                    expand=True
                ),

                # OCR App
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("📄", size=16),
                            ft.Text("OCR App", size=12, weight=ft.FontWeight.W_500)
                        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                        app_instance.start_external_flet_button,
                        app_instance.external_flet_status_text,
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=12,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE)),
                    border_radius=6,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
                    expand=True
                ),
            ], spacing=12),
        ], spacing=10),
        **card_style
    )

    # --- Hauptlayout ---
    main_content = ft.Column([
        header_section,
        project_section,
        rohteil_section,
        spannmittel_section,
        actions_section,
        nc_status_section,
        export_section,
        processes_section,
    ], spacing=12)

    # Container mit Padding und Scroll
    app_instance.page.add(
        ft.Container(
            content=main_content,
            padding=ft.padding.all(16),
            expand=True,
        )
    )

    app_instance.page.scroll = ft.ScrollMode.ADAPTIVE
    app_instance.page.update()