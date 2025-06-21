# config.py

from pathlib import Path
import datetime
import os

IS_WINDOWS = os.name == 'nt'

# Definiere die Pfade basierend auf dem Betriebssystem
if IS_WINDOWS:
    user_profile = Path.home()
    # Versuche, das Laufwerk K: zu verwenden, wenn es existiert, sonst Fallback
    try:
        net_drive_k_resolved = Path(r"K:").resolve(strict=True) # Prüft Existenz
        net_drive_k = net_drive_k_resolved
        print(f"Windows: Laufwerk K: gefunden unter {net_drive_k}")
    except FileNotFoundError:
        print("Windows: Laufwerk K: nicht gefunden. Verwende Fallback-Pfade auf dem Desktop.")
        net_drive_k = user_profile / "Desktop" / "K_DRIVE_FALLBACK" # Fallback, falls K: nicht existiert
        (net_drive_k / "NC-PGM").mkdir(parents=True, exist_ok=True)
        (net_drive_k / "Esprit").mkdir(parents=True, exist_ok=True)


    BASE_PATH1 = user_profile / "Desktop" / "Spannmittel"
    BASE_PATH2 = net_drive_k / "NC-PGM"
    ESPPRIT_BASE_PATH = net_drive_k / "Esprit"
    BASE_PATH5 = user_profile / "PycharmProjects" / "Blank_Maker_FLET" / "prozess.pyw"
    PATH_TO_EXTERNAL_FLET_APP = user_profile / "PycharmProjects" / "ProzessORC" / "Flet-ProzessOCR-1.0.py"
    BASE_PATH3 = Path("WKS05") # Relativer Pfad, bleibt gleich
else:
    # macOS/Linux Pfade (Passe diese an deine Struktur an!)
    # Annahme: Das Projekt Blank_Maker_FLET liegt auf deinem Desktop
    project_root = Path.home() / "Desktop" / "Blank_Maker_FLET"

    BASE_PATH1 = project_root / "Pfade-Mac" / "Spannmittel"
    BASE_PATH2 = project_root / "Pfade-Mac" / "NC-PGM"
    ESPPRIT_BASE_PATH = project_root / "Pfade-Mac" / "Esprit"
    BASE_PATH5 = project_root / "prozess.pyw" # Direkt im Projekt-Root
    # PATH_TO_EXTERNAL_FLET_APP sollte der tatsächliche Pfad zur anderen App sein
    PATH_TO_EXTERNAL_FLET_APP = Path.home() / "Desktop" / "ProzessORC" / "Flet-ProzessOCR-1.0.py"
    BASE_PATH3 = Path("WKS05") # Relativer Pfad, bleibt gleich

    # Erstelle die macOS Test-Pfade, falls sie nicht existieren
    BASE_PATH1.mkdir(parents=True, exist_ok=True)
    BASE_PATH2.mkdir(parents=True, exist_ok=True)
    ESPPRIT_BASE_PATH.mkdir(parents=True, exist_ok=True)
    (ESPPRIT_BASE_PATH / "NC-Files").mkdir(parents=True, exist_ok=True) # Für get_daily_folder_path_config


def get_daily_folder_path_config() -> Path:
    """Ermittelt den Pfad für den aktuellen Wochentag."""
    current_date = datetime.datetime.now()
    kalenderwoche = int(current_date.strftime("%V"))
    wochentag_num_python = current_date.weekday()
    wochentag_ordner_num = wochentag_num_python + 1

    deutsche_wochentage_kurz = {0: "MO", 1: "DI", 2: "MI", 3: "DO", 4: "FR", 5: "SA", 6: "SO"}
    wochentag_kuerzel = deutsche_wochentage_kurz[wochentag_num_python] # Korrekt mit "ue"

    # Pfad an Betriebssystem anpassen
    # ESPPRIT_BASE_PATH wird hier verwendet
    # Stelle sicher, dass ESPPRIT_BASE_PATH oben korrekt definiert wurde
    base_folder_for_daily = ESPPRIT_BASE_PATH / "NC-Files" # Unterordner für tägliche Dateien

    daily_folder_name_part = f"AT-25-KW{kalenderwoche}/Gschwendtner/{wochentag_ordner_num}.{wochentag_kuerzel}" # Korrekt mit "ue"
    daily_folder = base_folder_for_daily / daily_folder_name_part

    # Für Testzwecke Ordner erstellen, wenn er nicht existiert
    daily_folder.mkdir(parents=True, exist_ok=True)

    return daily_folder

BASE_PATH4 = get_daily_folder_path_config()

print(f"Konfigurierte Pfade:")
print(f"BASE_PATH1 (Spannmittel): {BASE_PATH1}")
print(f"BASE_PATH2 (NC-PGM): {BASE_PATH2}")
print(f"BASE_PATH3 (WKS05): {BASE_PATH3}")
print(f"BASE_PATH4 (Täglicher Ordner): {BASE_PATH4}")
print(f"BASE_PATH5 (Prozess-Skript): {BASE_PATH5}")
print(f"ESPPRIT_BASE_PATH: {ESPPRIT_BASE_PATH}")
print(f"PATH_TO_EXTERNAL_FLET_APP: {PATH_TO_EXTERNAL_FLET_APP}")