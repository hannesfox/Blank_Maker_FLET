import flet as ft  # Nur für ft.Colors, falls für Fehlermeldungen etc. benötigt, sonst nicht
import shutil
import os
import re
from pathlib import Path
import ezdxf  # Für DXF Erstellung

import config  # Für BASE_PATH1, BASE_PATH2, BASE_PATH3


# --- DXF Erstellungsfunktionen (ehemals program1.py, program2.py) ---

def create_rectangle_file(length: float, width: float, height: float, destination_folder: Path):
    """Erstellt eine DXF-Datei für ein Rechteck und speichert sie im Zielordner."""
    if not isinstance(destination_folder, Path):
        raise TypeError("destination_folder muss ein Path-Objekt sein.")
    destination_folder.mkdir(parents=True, exist_ok=True)
    file_path = destination_folder / "!rohteil.dxf"

    dwg = ezdxf.new('R2010')
    msp = dwg.modelspace()
    center_z_offset = -4  # Wie im Original

    points = [
        (-length / 2, -width / 2, center_z_offset),
        (length / 2, -width / 2, center_z_offset),
        (length / 2, width / 2, center_z_offset),
        (-length / 2, width / 2, center_z_offset),
        (-length / 2, -width / 2, center_z_offset),  # Schließt Polyline
    ]
    msp.add_polyline3d(points, dxfattribs={'layer': 'Roh', 'color': 198})

    copy_points = [(x, y, z + height) for x, y, z in points]
    msp.add_polyline3d(copy_points, dxfattribs={'layer': 'Roh', 'color': 198})

    text_content = f"X: {length} mm\nY: {width} mm\nZ: {height} mm"
    text_entity = msp.add_text(text_content, dxfattribs={'height': 5, 'layer': 'Roh', 'color': 206})
    text_entity.dxf.insert = (-length / 2, (width / 2) + 4,
                              height + center_z_offset)  # Position relativ zur oberen Fläche
    text_entity.dxf.rotation = 0

    try:
        dwg.saveas(file_path)
    except Exception as e:
        raise IOError(f"Fehler beim Speichern der Rechteck-DXF-Datei '{file_path}': {e}")


def create_circle_file(diameter: float, height: float, destination_folder: Path):
    """Erstellt eine DXF-Datei für einen Kreis/Zylinder und speichert sie im Zielordner."""
    if not isinstance(destination_folder, Path):
        raise TypeError("destination_folder muss ein Path-Objekt sein.")
    destination_folder.mkdir(parents=True, exist_ok=True)
    file_path = destination_folder / "!rohteil.dxf"

    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    radius = diameter / 2
    center_z_offset = -6  # Wie im Original

    msp.add_circle((0, 0, center_z_offset), radius, dxfattribs={'layer': 'Roh', 'color': 198})
    msp.add_circle((0, 0, height + center_z_offset), radius, dxfattribs={'layer': 'Roh', 'color': 198})

    mtext_diameter = msp.add_mtext(f"Diameter = {diameter}",
                                   dxfattribs={'layer': 'Roh', 'color': 198, 'char_height': 5})
    mtext_diameter.set_location(insert=(radius * 1.2, 4, height + center_z_offset), rotation=0, attachment_point=1)

    mtext_height = msp.add_mtext(f"Height = {height}", dxfattribs={'layer': 'Roh', 'color': 206, 'char_height': 5})
    mtext_height.set_location(insert=(radius * 1.2, -4, height + center_z_offset), rotation=0, attachment_point=1)

    try:
        doc.saveas(file_path)
    except Exception as e:
        raise IOError(f"Fehler beim Speichern der Kreis-DXF-Datei '{file_path}': {e}")


# --- Datei Kopier- und Verschiebefunktionen ---

def copy_vice_files(selected_folder_name: str, selected_value: str, destination_folder: Path, show_dialog_func):
    """Kopiert Schraubstock (.step) und zugehörige .dxf Dateien."""
    if not selected_folder_name or not selected_value:
        raise ValueError("Ordnername oder Wert für Schraubstockauswahl fehlt.")
    if not isinstance(destination_folder, Path):
        raise TypeError("destination_folder muss ein Path-Objekt sein.")

    source_folder = config.BASE_PATH1 / selected_folder_name
    destination_folder.mkdir(parents=True, exist_ok=True)

    found_step = False
    found_dxf = False
    copied_files_info = []

    for item in source_folder.iterdir():
        if item.is_file():
            # Suche nach .step Datei, die den Wert enthält
            if item.suffix.lower() == ".step" and re.search(r"\b{}\b".format(re.escape(selected_value)), item.name,
                                                            re.IGNORECASE):
                try:
                    dest_file_path = destination_folder / f"!schraubstock{item.suffix}"
                    shutil.copy2(item, dest_file_path)
                    copied_files_info.append(f"STEP: {item.name} -> {dest_file_path.name}")
                    found_step = True
                except Exception as e:
                    raise IOError(f"Fehler beim Kopieren von {item.name}: {e}")

            # Suche nach .dxf Dateien (alle im Ordner)
            # Originalcode hat alle DXF-Dateien kopiert, nicht nur die passende zum Wert.
            # Das wird hier beibehalten.
            elif item.suffix.lower() == ".dxf":
                try:
                    # DXF-Dateien behalten ihren Originalnamen im Zielordner
                    dest_file_path = destination_folder / item.name
                    shutil.copy2(item, dest_file_path)
                    copied_files_info.append(f"DXF: {item.name} -> {dest_file_path.name}")
                    found_dxf = True  # Zumindest eine DXF gefunden
                except Exception as e:
                    # Hier könnte man entscheiden, ob der Fehler fatal ist oder nur geloggt wird
                    print(f"Warnung: Fehler beim Kopieren der DXF-Datei {item.name}: {e}")

    if not found_step:
        # Verwende die show_dialog_func für Feedback an den User
        show_dialog_func("Info Schraubstock",
                         f"Keine passende .step Datei für Wert '{selected_value}' in '{source_folder.name}' gefunden.")
    elif not copied_files_info:  # Sollte nicht passieren, wenn found_step True ist, aber als Sicherheitsnetz
        show_dialog_func("Info Schraubstock",
                         f"Keine Dateien für Wert '{selected_value}' in '{source_folder.name}' gefunden oder kopiert.")

    # Optional: Eine Erfolgsmeldung, wenn Dateien kopiert wurden
    # if copied_files_info:
    #     show_dialog_func("Erfolg", "Schraubstockdateien kopiert:\n" + "\n".join(copied_files_info))


def move_program_files(at_prefix: str, project_name: str, show_dialog_func) -> int:
    """Verschiebt .H Programmdateien in einen projektspezifischen Ordner."""
    if not at_prefix or not project_name:
        # Dieser Fall sollte bereits im Event-Handler abgefangen werden, aber zur Sicherheit hier.
        raise ValueError("AT-Präfix oder Projektname fehlt.")

    machines = ["HERMLE-C40", "HERMLE-C400", "DMU-EVO60", "DMU-100EVO", "DMC650V", "DMC1035V"]
    moved_count = 0
    errors = []

    for machine in machines:
        source_dir = config.BASE_PATH2 / machine / config.BASE_PATH3  # config.BASE_PATH3 ist "WKS05"
        if not source_dir.is_dir():
            # print(f"Info: Quellordner {source_dir} für Maschine {machine} nicht gefunden. Überspringe.")
            continue

        destination_dir_name = f"AT{at_prefix}-{project_name}"
        destination_dir = config.BASE_PATH2 / machine / destination_dir_name
        destination_dir.mkdir(parents=True, exist_ok=True)

        for file_path in source_dir.glob("*.H"):
            try:
                shutil.move(str(file_path), str(destination_dir / file_path.name))
                moved_count += 1
            except Exception as ex_move:
                errors.append(f"Konnte {file_path.name} nicht verschieben: {ex_move}")

    if errors:
        # Zeige Fehler gesammelt an
        show_dialog_func("Fehler beim Verschieben", "\n".join(errors))

    return moved_count