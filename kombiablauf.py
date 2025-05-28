import pyautogui
import pyscreeze
import os
import time
import tkinter as tk
from tkinter import messagebox
import threading
from autoesprit import run_program

class TransparentRing(tk.Toplevel):
    def __init__(self, parent, x, y, radius=100, ring_width=5):
        super().__init__(parent)
        
        # Fenster-Eigenschaften setzen
        self.overrideredirect(True)  # Rahmen entfernen
        self.attributes("-topmost", True)  # Immer im Vordergrund
        self.attributes("-transparentcolor", "white")  # Weiß wird transparent
        self.attributes("-alpha", 0.7)  # Leichte Transparenz für den Ring
        
        # Fenster-Größe etwas größer als der Ring
        window_size = (radius + ring_width) * 2
        self.geometry(f"{window_size}x{window_size}+{x-radius-ring_width}+{y-radius-ring_width}")
        
        # Canvas für das Zeichnen erstellen
        self.canvas = tk.Canvas(self, width=window_size, height=window_size, 
                               bg="white", highlightthickness=0)
        self.canvas.pack()
        
        # Kreismitte berechnen
        center = window_size / 2
        
        # Äußeren Kreis zeichnen
        self.canvas.create_oval(
            ring_width, ring_width, 
            window_size - ring_width, window_size - ring_width, 
            fill="red", outline="")
        
        # Inneren Kreis ausschneiden (transparent)
        self.canvas.create_oval(
            ring_width + ring_width, ring_width + ring_width,
            window_size - ring_width - ring_width, window_size - ring_width - ring_width,
            fill="white", outline="")
        
        # Horizontale Linie des Fadenkreuzes
        self.canvas.create_line(
            center - radius + ring_width*2, center,
            center + radius - ring_width*2, center,
            fill="red", width=2)
        
        # Vertikale Linie des Fadenkreuzes
        self.canvas.create_line(
            center, center - radius + ring_width*2,
            center, center + radius - ring_width*2,
            fill="red", width=2)
        
        # Optional: Kleine Markierungen/Skala am Fadenkreuz
        tick_length = 5
        for i in range(1, 5):
            # Horizontale Ticks
            offset = i * (radius / 5)
            # Rechts
            self.canvas.create_line(
                center + offset, center - tick_length,
                center + offset, center + tick_length,
                fill="red", width=1)
            # Links
            self.canvas.create_line(
                center - offset, center - tick_length,
                center - offset, center + tick_length,
                fill="red", width=1)
            # Vertikale Ticks
            # Oben
            self.canvas.create_line(
                center - tick_length, center - offset,
                center + tick_length, center - offset,
                fill="red", width=1)
            # Unten
            self.canvas.create_line(
                center - tick_length, center + offset,
                center + tick_length, center + offset,
                fill="red", width=1)

class Kombiablauf:
    def __init__(self, ctrl_v_entry, selection_var, destination_entry, length_var, width_var, height_var):
        self.ctrl_v_entry = ctrl_v_entry
        self.selection_var = selection_var
        self.destination_entry = destination_entry
        self.length_var = length_var
        self.width_var = width_var
        self.height_var = height_var
        self.ring = None
        
    def kombiablauf(self):
        self.action_1()
        self.action_2()
        self.action_3()
        self.action_4()
        self.action_5()
        self.action_6()
        self.action_7()
        
        # Entscheidungsmeldung am Ende des Ablaufs mit rotem Ring
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        root.update()  # Fenster sofort anzeigen
        root.focus_force()  # Fenster erhält den Fokus
        
        # Hier den roten Ring an einer spezifischen Position anzeigen
        ring_x = 2200  # Exakte X-Position in Pixeln
        ring_y = 812  # Exakte Y-Position in Pixeln
        
        # Ring erstellen an der angegebenen Position
        self.ring = TransparentRing(root, ring_x, ring_y, radius=100, ring_width=5)
        
        # MessageBox anzeigen
        decision = messagebox.askyesno("Pause!", "Hallo Hannes, hab ich gute Arbeit geleistet? Soll ich noch weitere Aufgaben für dich übernehmen?")
        
        # Ring entfernen
        if self.ring:
            self.ring.destroy()
            self.ring = None
        
        root.destroy()
        
        if decision:
            # Weitere Aktionen bei Fortsetzen
            print("Prozess wird fortgesetzt.")
            length = float(self.length_var.get())
            width = float(self.width_var.get())
            height = float(self.height_var.get())
            
            run_program(length, width, height)  # autoesprit läuft weiter
        else:
            print("Prozess abgebrochen.")
            
    def action_1(self):
        image_position = pyscreeze.locateOnScreen('1.png', confidence=0.5)
        image_center = pyscreeze.center(image_position)
        time.sleep(0.5)
        pyautogui.click(image_center)
        time.sleep(0.5)
        
    def action_2(self):
        image_position = pyscreeze.locateOnScreen('2.png', confidence=0.4)
        image_center = pyscreeze.center(image_position)
        time.sleep(0.9)
        pyautogui.click(image_center)
        
    def action_3(self):
        image_position = pyscreeze.locateOnScreen('3.png', confidence=0.5, grayscale=True)
        image_center = pyscreeze.center(image_position)
        time.sleep(0.4)
        pyautogui.doubleClick(image_center)
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.1)
        text = self.ctrl_v_entry.get() + '_A'
        pyautogui.typewrite(text)
        time.sleep(0.1)
        
    def action_4(self):
        pyautogui.press('tab')
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
        text = self.ctrl_v_entry.get()
        pyautogui.typewrite(text)
        time.sleep(0.1)
        
    def action_5(self):
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        time.sleep(0.1)
        text = self.selection_var.get()
        pyautogui.typewrite(text)
        time.sleep(0.1)
        
    def action_6(self):
        pyautogui.press('enter')
        time.sleep(0.1)
        
    def action_7(self):
        wegzeit1 = 0.4
        pfad_rohteil = os.path.join(self.destination_entry.get(), "!rohteil.dxf")
        pfad_schraubstock = os.path.join(self.destination_entry.get(), "!schraubstock.step")
        pyautogui.doubleClick(974, 1047, duration=wegzeit1)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(0.5)
        pyautogui.typewrite(pfad_rohteil)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(0.5)
        pyautogui.doubleClick(977, 1142, duration=wegzeit1)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(0.8)
        pyautogui.typewrite(pfad_schraubstock)
        time.sleep(0.8)
        pyautogui.press('enter')
