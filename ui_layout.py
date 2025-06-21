#ui_layout.py
import flet as ft

def build_main_ui(app_instance):
    """
    Stellt die erstellten UI-Elemente in einem strukturierten Layout zusammen.
    Greift auf die Widgets zu, die in app_instance gespeichert sind.
    """
    app_instance.page.add(
        ft.Column([
            ft.Text("Programmname:", size=16, weight=ft.FontWeight.BOLD),
            app_instance.ctrl_v_field,
            app_instance.selection_dropdown,
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
                                    ft.Row([app_instance.length_field, app_instance.width_field, app_instance.height_field]),
                                    ft.Row([app_instance.rect_make_button, app_instance.rect_progress],
                                           vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                    app_instance.original_size_label,
                                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                                padding=ft.padding.symmetric(horizontal=5),
                            )
                        ),
                        ft.Tab(
                            text="Kreis", icon=ft.Icons.CIRCLE_OUTLINED,
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Row([app_instance.diameter_field, app_instance.height2_field]),
                                    ft.Row([app_instance.circle_make_button, app_instance.circle_progress],
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
            app_instance.value_field,
            app_instance.folder_dropdown,
            ft.Text("Zielordner:"),
            app_instance.destination_field,
            ft.Row([app_instance.vice_create_button, app_instance.vice_progress], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=20),
            ft.Container(
                content=ft.ElevatedButton(
                    text="Kombiablauf Starten", icon=ft.Icons.AUTO_FIX_HIGH_OUTLINED,
                    on_click=app_instance.start_kombiablauf, # Event handler from app_instance
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
            ft.Row([app_instance.blength_field, ft.ElevatedButton("   B-Start   ", on_click=app_instance.start_bseite)]), # Event handler
            ft.Divider(height=10),
            ft.Row(controls=[
                ft.Column(controls=[
                    ft.Text("PythonCommander:", size=12, weight=ft.FontWeight.BOLD),
                    ft.Row([app_instance.at_prefix_field, ft.ElevatedButton("     Switch    ", on_click=app_instance.toggle_value)]), # Event handler
                    ft.Row([app_instance.project_name_field, app_instance.back_button]),
                ], alignment=ft.MainAxisAlignment.START, expand=True),
                ft.Column(controls=[app_instance.status_label, app_instance.dxf_status_container],
                          alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.END,
                          expand=True)
            ]),
            ft.Container(content=app_instance.export_button, alignment=ft.alignment.center,
                         padding=ft.padding.symmetric(vertical=20)),
            ft.Divider(height=10),
            ft.Row(controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text("Prozess Öffnen:", size=12, weight=ft.FontWeight.BOLD),
                        ft.Row([app_instance.start_button, app_instance.stop_button], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([app_instance.status_icon, app_instance.status_text], alignment=ft.MainAxisAlignment.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True, padding=10, border=ft.border.all(1, "outlinevariant"),
                    border_radius=ft.border_radius.all(8),
                ),
                ft.VerticalDivider(width=10, thickness=1),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Externe Flet Anwendung (ProzessOCR):", size=12, weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER),
                        ft.Row([app_instance.start_external_flet_button, app_instance.stop_external_flet_button], alignment=ft.MainAxisAlignment.CENTER), # stop button hinzugefügt
                        ft.Row([app_instance.external_flet_status_text], alignment=ft.MainAxisAlignment.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True, padding=10, border=ft.border.all(1, "outlinevariant"),
                    border_radius=ft.border_radius.all(8),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.START),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    )