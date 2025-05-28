# kombiablauf.py

import pyautogui
import pyscreeze
import os
import time
import flet as ft # Importiere Flet
from autoesprit import run_program

class Kombiablauf:
    def __init__(self, page: ft.Page, ctrl_v_field: ft.TextField, selection_dropdown: ft.Dropdown,
                 destination_field: ft.TextField, length_field: ft.TextField,
                 width_field: ft.TextField, height_field: ft.TextField):
        """
        Initialisiert den Kombiablauf mit Flet-Steuerelementen.
        page: Die Flet Page-Instanz, um Dialoge anzuzeigen.
        """
        self.page = page  # Flet Page-Instanz für Dialoge
        self.ctrl_v_field = ctrl_v_field
        self.selection_dropdown = selection_dropdown
        self.destination_field = destination_field
        self.length_field = length_field
        self.width_field = width_field
        self.height_field = height_field
        # self.ring = None # Nicht mehr benötigt

    def _show_decision_dialog(self):
        """Zeigt den Flet AlertDialog am Ende des Ablaufs."""

        def on_dialog_result(e):
            self.page.dialog.open = False
            self.page.update() # Schließe den Dialog
            if e.control.data == "yes":
                print("Prozess wird fortgesetzt (Flet Dialog).")
                try:
                    # Konvertiere Komma zu Punkt für Fließkommazahlen
                    length_str = self.length_field.value.replace(',', '.')
                    width_str = self.width_field.value.replace(',', '.')
                    height_str = self.height_field.value.replace(',', '.')

                    length = float(length_str)
                    width = float(width_str)
                    height = float(height_str)

                    run_program(length, width, height)  # autoesprit läuft weiter
                except ValueError:
                    # Fehlerbehandlung, falls Konvertierung fehlschlägt
                    error_dialog = ft.AlertDialog(
                        title=ft.Text("Eingabefehler"),
                        content=ft.Text("Ungültige Zahlenwerte in den Längen-, Breiten- oder Höhenfeldern."),
                        actions=[ft.TextButton("OK", on_click=lambda _: self.page.close_dialog())]
                    )
                    self.page.dialog = error_dialog
                    self.page.dialog.open = True
                    self.page.update()
                    print("Fehler: Ungültige Zahlenwerte für run_program.")
                except Exception as ex_run:
                    error_dialog = ft.AlertDialog(
                        title=ft.Text("Fehler bei Fortsetzung"),
                        content=ft.Text(f"Ein Fehler ist aufgetreten: {ex_run}"),
                        actions=[ft.TextButton("OK", on_click=lambda _: self.page.close_dialog())]
                    )
                    self.page.dialog = error_dialog
                    self.page.dialog.open = True
                    self.page.update()
                    print(f"Fehler beim Ausführen von run_program: {ex_run}")

            else:
                print("Prozess abgebrochen (Flet Dialog).")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Pause!"),
            content=ft.Text("Hallo Hannes, hab ich gute Arbeit geleistet? Soll ich noch weitere Aufgaben für dich übernehmen?"),
            actions=[
                ft.TextButton("Ja", on_click=on_dialog_result, data="yes"),
                ft.TextButton("Nein", on_click=on_dialog_result, data="no"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def kombiablauf(self):
        try:
            self.action_1()
            self.action_2()
            self.action_3()
            self.action_4()
            self.action_5()
            self.action_6()
            self.action_7()
        except pyautogui.FailSafeException:
            # FailSafe durch PyAutoGUI (Maus in Ecke)
            dialog = ft.AlertDialog(title=ft.Text("Abbruch"), content=ft.Text("Maus wurde in eine Ecke bewegt (Fail-Safe). Aktionen abgebrochen."), actions=[ft.TextButton("OK", on_click=lambda e: self.page.close_dialog())])
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            print("PyAutoGUI FailSafe ausgelöst.")
            return # Beende den Ablauf hier
        except FileNotFoundError as fnf_err:
             dialog = ft.AlertDialog(title=ft.Text("Bild nicht gefunden"), content=ft.Text(f"Ein benötigtes Bild konnte nicht gefunden werden:\n{fnf_err}\nDer Ablauf wurde abgebrochen."), actions=[ft.TextButton("OK", on_click=lambda e: self.page.close_dialog())])
             self.page.dialog = dialog
             dialog.open = True
             self.page.update()
             print(f"Bild nicht gefunden: {fnf_err}")
             return
        except Exception as e:
            # Allgemeiner Fehler während der Aktionen
            dialog = ft.AlertDialog(title=ft.Text("Fehler im Ablauf"), content=ft.Text(f"Ein Fehler ist aufgetreten:\n{e}\nDer Ablauf wurde abgebrochen."), actions=[ft.TextButton("OK", on_click=lambda e: self.page.close_dialog())])
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            print(f"Fehler im Kombiablauf: {e}")
            return # Beende den Ablauf hier

        # Entscheidungsmeldung am Ende des Ablaufs
        self._show_decision_dialog()

    def _locate_and_click(self, image_name, confidence, action_name, click_type="click", grayscale=False, wait_before_click=0.1, wait_after_click=0.5):
        """Hilfsfunktion, um Bild zu finden und zu klicken. Wirft FileNotFoundError, wenn Bilddatei fehlt, oder Exception, wenn nicht auf Screen."""
        # Prüfe, ob die Bilddatei existiert
        if not os.path.exists(image_name):
            # Versuche, im Verzeichnis des aktuellen Skripts zu suchen (falls relativer Pfad)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path_in_script_dir = os.path.join(script_dir, image_name)
            if os.path.exists(image_path_in_script_dir):
                image_to_find = image_path_in_script_dir
            else:
                raise FileNotFoundError(f"Bilddatei '{image_name}' für {action_name} nicht gefunden.")
        else:
            image_to_find = image_name

        image_position = pyscreeze.locateOnScreen(image_to_find, confidence=confidence, grayscale=grayscale)
        if image_position is None:
            raise Exception(f"Bild '{os.path.basename(image_to_find)}' für {action_name} nicht auf dem Bildschirm gefunden.")

        image_center = pyscreeze.center(image_position)
        time.sleep(wait_before_click) # Kurze Pause vor der Aktion
        if click_type == "click":
            pyautogui.click(image_center)
        elif click_type == "doubleclick":
            pyautogui.doubleClick(image_center)
        time.sleep(wait_after_click)


    def action_1(self):
        self._locate_and_click('1.png', confidence=0.5, action_name="Aktion 1", wait_after_click=0.5)

    def action_2(self):
        self._locate_and_click('2.png', confidence=0.4, action_name="Aktion 2", wait_after_click=0.9)

    def action_3(self):
        self._locate_and_click('3.png', confidence=0.5, action_name="Aktion 3 (Bild)", click_type="doubleclick", grayscale=True, wait_after_click=0.4)
        time.sleep(0.2) # Zusätzliche Pause nach Doppelklick
        pyautogui.press('delete')
        time.sleep(0.1)
        text = self.ctrl_v_field.value + '_A' # KORREKTUR: .value verwenden
        pyautogui.typewrite(text)
        time.sleep(0.1)

    def action_4(self):
        pyautogui.press('tab')
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
        text = self.ctrl_v_field.value # KORREKTUR: .value verwenden
        pyautogui.typewrite(text)
        time.sleep(0.1)

    def action_5(self):
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        time.sleep(0.1)
        text = self.selection_dropdown.value
        if not text or text == "Option":
            raise Exception("Bitte einen gültigen Programmtyp im Dropdown auswählen für Aktion 5.")
        pyautogui.typewrite(text)
        time.sleep(0.1)

    def action_6(self):
        pyautogui.press('enter')
        time.sleep(0.1)

    def action_7(self):
        wegzeit1 = 0.4
        destination_folder = self.destination_field.value
        if not destination_folder or not os.path.isdir(destination_folder):
            raise Exception(f"Zielordner '{destination_folder}' ist ungültig oder existiert nicht für Aktion 7.")

        pfad_rohteil = os.path.join(destination_folder, "!rohteil.dxf")
        pfad_schraubstock = os.path.join(destination_folder, "!schraubstock.step")

        # Überprüfe, ob die Dateien existieren, bevor PyAutoGUI Aktionen startet
        if not os.path.isfile(pfad_rohteil):
            raise FileNotFoundError(f"Rohteil-Datei '{pfad_rohteil}' nicht gefunden für Aktion 7.")
        if not os.path.isfile(pfad_schraubstock):
            raise FileNotFoundError(f"Schraubstock-Datei '{pfad_schraubstock}' nicht gefunden für Aktion 7.")


        pyautogui.doubleClick(974, 1047, duration=wegzeit1)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(0.5)
        pyautogui.typewrite(pfad_rohteil)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1.0)

        pyautogui.doubleClick(977, 1142, duration=wegzeit1)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(0.8)
        pyautogui.typewrite(pfad_schraubstock)
        time.sleep(0.8)
        pyautogui.press('enter')
        time.sleep(1.0)