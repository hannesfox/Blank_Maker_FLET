from pathlib import Path
import datetime
import os

IS_WINDOWS = os.name == 'nt'

# Definiere die Pfade basierend auf dem Betriebssystem
if IS_WINDOWS:
    user_profile = Path.home()
    try:
        # Nur prüfen, ob K: existiert und zugreifbar ist
        Path(r"K:").resolve(strict=True)
        # Wenn wir hier ankommen, existiert K:
        # Hier die Änderung: Stelle sicher, dass der Pfad mit einem Backslash endet, wenn es nur ein Laufwerksbuchstabe ist.
        net_drive_base_for_paths = Path("K:\\") # Explizit den Laufwerksbuchstaben MIT Backslash verwenden
        print(f"Windows: Laufwerk K: ist verfügbar und wird als Basis verwendet: {net_drive_base_for_paths}")
    except FileNotFoundError:
        print("Windows: Laufwerk K: nicht gefunden. Verwende Fallback-Pfade auf dem Desktop.")
        net_drive_base_for_paths = user_profile / "Desktop" / "K_DRIVE_FALLBACK"
        (net_drive_base_for_paths / "NC-PGM").mkdir(parents=True, exist_ok=True)
        (net_drive_base_for_paths / "Esprit").mkdir(parents=True, exist_ok=True)

    BASE_PATH1 = user_profile / "Desktop" / "Spannmittel"
    BASE_PATH2 = net_drive_base_for_paths / "NC-PGM"
    ESPPRIT_BASE_PATH = net_drive_base_for_paths / "Esprit" # Wird jetzt K:\Esprit sein

    # Pfad zum prozess_listener.py
    pycharm_projects_base = user_profile / "PycharmProjects"
    project_folder_name_actual = "Blank_Maker_FLET" # Stelle sicher, dass dies korrekt ist

    PATH_TO_PROZESS_LISTENER = pycharm_projects_base / project_folder_name_actual / "external_scripts" / "prozess_listener.py"
    PATH_TO_EXTERNAL_FLET_APP = pycharm_projects_base / "ProzessORC" / "Flet-ProzessOCR-1.0.py"
    BASE_PATH3 = Path("WKS05")
else:
    # macOS/Linux Pfade (Passe diese an deine Struktur an!)
    project_root_name = "Blank_Maker_FLET" # Annahme des neuen Projektnamens
    project_root = Path.home() / "Desktop" / project_root_name

    BASE_PATH1 = project_root / "Pfade-Mac" / "Spannmittel"
    BASE_PATH2 = project_root / "Pfade-Mac" / "NC-PGM"
    ESPPRIT_BASE_PATH = project_root / "Pfade-Mac" / "Esprit"
    PATH_TO_PROZESS_LISTENER = project_root / "external_scripts" / "prozess_listener.py"
    PATH_TO_EXTERNAL_FLET_APP = Path.home() / "Desktop" / "ProzessORC" / "Flet-ProzessOCR-1.0.py" # Anpassen falls nötig
    BASE_PATH3 = Path("WKS05")

    # Erstelle die macOS Test-Pfade, falls sie nicht existieren
    BASE_PATH1.mkdir(parents=True, exist_ok=True)
    BASE_PATH2.mkdir(parents=True, exist_ok=True)
    ESPPRIT_BASE_PATH.mkdir(parents=True, exist_ok=True)
    (ESPPRIT_BASE_PATH / "NC-Files").mkdir(parents=True, exist_ok=True)


def get_daily_folder_path_config() -> Path:
    """Ermittelt den Pfad für den aktuellen Wochentag."""
    current_date = datetime.datetime.now()
    kalenderwoche = int(current_date.strftime("%V"))
    wochentag_num_python = current_date.weekday()
    wochentag_ordner_num = wochentag_num_python + 1
    deutsche_wochentage_kurz = {0: "MO", 1: "DI", 2: "MI", 3: "DO", 4: "FR", 5: "SA", 6: "SO"}
    wochentag_kuerzel = deutsche_wochentage_kurz[wochentag_num_python]

    base_folder_for_daily = ESPPRIT_BASE_PATH / "NC-Files"
    daily_folder_name_part = f"AT-25-KW{kalenderwoche}/Gschwendtner/{wochentag_ordner_num}.{wochentag_kuerzel}"
    daily_folder = base_folder_for_daily / daily_folder_name_part
    daily_folder.mkdir(parents=True, exist_ok=True)
    return daily_folder

BASE_PATH4 = get_daily_folder_path_config()

# Pfad zum Bilder-Ordner (relativ zum Projektstammverzeichnis)
# Dies ist eine Annahme. Wenn dein Bilder-Ordner woanders liegt, passe dies an.
# Oder übergebe diesen Pfad explizit an die Automationsfunktionen.
PROJECT_ROOT_DIR = Path(__file__).resolve().parent # Holt das Verzeichnis, in dem config.py liegt
PATH_TO_IMAGES_FOLDER = PROJECT_ROOT_DIR / "Bilder"


print(f"Konfigurierte Pfade:")
print(f"BASE_PATH1 (Spannmittel): {BASE_PATH1}")
print(f"BASE_PATH2 (NC-PGM): {BASE_PATH2}")
print(f"BASE_PATH3 (WKS05): {BASE_PATH3}")
print(f"BASE_PATH4 (Täglicher Ordner): {BASE_PATH4}")
print(f"PATH_TO_PROZESS_LISTENER: {PATH_TO_PROZESS_LISTENER}")
print(f"ESPPRIT_BASE_PATH: {ESPPRIT_BASE_PATH}")
print(f"PATH_TO_EXTERNAL_FLET_APP: {PATH_TO_EXTERNAL_FLET_APP}")
print(f"PATH_TO_IMAGES_FOLDER: {PATH_TO_IMAGES_FOLDER}")