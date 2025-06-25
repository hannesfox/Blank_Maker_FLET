import flet as ft
import subprocess
import asyncio
from pathlib import Path


async def monitor_process_async(process, on_stop_callback):
    """Überwacht einen Prozess asynchron und ruft bei Beendigung einen Callback auf."""
    if process is None:
        return
    while True:
        if process.poll() is not None:  # Prozess beendet
            if callable(on_stop_callback):
                on_stop_callback()
            break
        await asyncio.sleep(1)  # Prüfintervall


def run_script_async(
        page: ft.Page,
        script_path: Path,
        current_process_ref,  # Referenz auf das Prozessattribut in der App-Instanz (z.B. self.script_process)
        start_button: ft.ElevatedButton,
        stop_button: ft.ElevatedButton = None,
        status_icon: ft.Icon = None,  # Optional
        status_text: ft.Text = None,  # Optional
        process_name: str = "Skript",
        on_stop_callback=None,
        status_running_text: str = "Läuft",
        status_stopped_text: str = "Gestoppt",
        running_color=ft.Colors.GREEN_600,
        stopped_color=ft.Colors.RED_600
):
    """
    Startet ein Python-Skript als Subprozess und aktualisiert die UI.
    Start Stop Button für Prozess Öffnen funktion.
    """
    if current_process_ref and current_process_ref.poll() is None:
        # show_dialog_func("Info", f"{process_name} läuft bereits!") # Dialog sollte vom Haupt-Handler kommen
        print(f"Info: {process_name} läuft bereits!")
        return current_process_ref  # Prozess läuft schon, gib aktuelle Referenz zurück

    try:
        # CREATE_NO_WINDOW nur für Windows, um Konsolenfenster zu vermeiden
        creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') and Path(
            script_path).suffix.lower() == '.pyw' else 0

        # Stelle sicher, dass script_path ein String ist für subprocess.Popen
        script_path_str = str(script_path)
        if not script_path.exists():
            # show_dialog_func("Fehler", f"{process_name} Skriptpfad nicht gefunden: {script_path_str}")
            print(f"Fehler: {process_name} Skriptpfad nicht gefunden: {script_path_str}")
            if callable(on_stop_callback): on_stop_callback()  # UI zurücksetzen
            return None

        new_process = subprocess.Popen(["python", script_path_str], creationflags=creationflags)

        start_button.disabled = True
        if stop_button:
            stop_button.disabled = False
        if status_icon:
            status_icon.color = running_color

        if status_text:
            status_text.value = status_running_text
            status_text.color = running_color

        page.update()

        if callable(on_stop_callback):
            page.run_task(monitor_process_async, new_process, on_stop_callback)
        return new_process

    except Exception as ex:
        # show_dialog_func("Fehler", f"Fehler beim Starten von {process_name}: {ex}")
        print(f"Fehler beim Starten von {process_name}: {ex}")
        if callable(on_stop_callback):
            on_stop_callback()  # UI zurücksetzen
        return None


def kill_script_async(process_ref, process_name: str = "Skript"):
    """Beendet einen laufenden Prozess."""
    if process_ref and process_ref.poll() is None:
        try:
            process_ref.terminate()  # Zuerst freundlich versuchen
            process_ref.wait(timeout=2)  # Gib ihm Zeit zu terminieren
        except subprocess.TimeoutExpired:
            process_ref.kill()  # Wenn nicht, dann hart
            print(f"{process_name} wurde hart beendet (kill).")
        except Exception as e:
            print(f"Fehler beim Beenden von {process_name}: {e}")
        # Der on_stop_callback wird durch den monitor_process_async ausgelöst
    else:
        print(f"{process_name} lief nicht oder war bereits beendet.")