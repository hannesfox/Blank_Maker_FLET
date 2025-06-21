#autoesprit.py
import pyautogui
import time
import tkinter as tk
from tkinter import messagebox


def run_program(length, width, height):
    wegzeit = 1
    pyautogui.doubleClick(983, 1014, duration=wegzeit)  # Doppelklick auf Standad
    positions = [(951, 1031), (950, 1064), (951, 1079), (951, 1095), (951, 1110), (952, 1127), (950, 1143), (951, 1160),
                 (951, 1176), (1265, 142), (1489, 500), (1640, 597)]
    verweilzeit = 0.05

    for position in positions:
        pyautogui.moveTo(position[0], position[1])
        time.sleep(verweilzeit)
        pyautogui.click()

    def enter_values(length, width, height):
        pyautogui.typewrite(str(length))
        pyautogui.press('tab')
        pyautogui.typewrite(str(width))
        pyautogui.press('tab')
        pyautogui.typewrite(str(height))
        pyautogui.press('tab')
        pyautogui.typewrite(str(-length / 2))
        pyautogui.press('tab')
        pyautogui.typewrite(str(-width / 2))
        pyautogui.press('tab')
        pyautogui.typewrite('-4')
        pyautogui.press('tab')

    pyautogui.moveTo(1650, 597, duration=0.2)  # Doppelklick in Länge
    pyautogui.doubleClick()

    enter_values(length, width, height)

    positions1 = [(1854, 878), (1478, 553), (951, 1031), (1593, 602)]
    verweilzeit = 0.05

    for position1 in positions1:
        pyautogui.moveTo(position1[0], position1[1])
        time.sleep(verweilzeit)
        pyautogui.click()


    #Fertigteil in reihe versuchen zu treffen 
    #grid_size = 8
    #point_distance = 100
    

    # Startposition zum starten der reihe
    #start_x, start_y = 2090, 380

    # Schleife durch das Raster und führe Klicks aus
    #for row in range(grid_size):
        #for col in range(grid_size):
            #x = start_x + col * point_distance
            #y = start_y + row * point_distance
            #pyautogui.click(x, y)

    #in Kreis Klicken
    pyautogui.doubleClick(2200, 812)
    time.sleep(0.5)
            

    
    wegzeit1 = 0.2
    positions2 = [(1850, 883), (1761, 925, {"duration": wegzeit1})]
    verweilzeit = 0.05
    

    for position2 in positions2:
        pyautogui.moveTo(position2[0], position2[1], duration=wegzeit1)
        time.sleep(verweilzeit)
        pyautogui.click()

    pyautogui.click(951, 1031, duration=wegzeit1)  # Solid ausblenden
    pyautogui.click(949, 1048, duration=wegzeit1)  # roh ausblenden
    pyautogui.doubleClick(982, 1143, duration=wegzeit1)  # Müll doppelklick
    time.sleep(verweilzeit)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.click(1394, 110, duration=wegzeit1)  # Simulationsbauteil erstellen
    pyautogui.click(1604, 853, duration=wegzeit1)  # Übernehmen
    time.sleep(0.5)

    pyautogui.doubleClick(981, 1142, duration=wegzeit1) #Müll layer
    time.sleep(0.5)
    pyautogui.click(1151, 1102, duration=wegzeit1)       #Layer Löschen
    time.sleep(0.5)

    pyautogui.press('left')  # Drückt die Pfeil-nach-links-Taste
    time.sleep(0.5)
    pyautogui.press('enter')  # Drückt die Enter-Taste
    time.sleep(0.5)

    pyautogui.click(1020, 173, duration=wegzeit1) #Freiklicken

    pyautogui.click(950, 1176, duration=wegzeit1)   #Spannelemente ausblenden
    pyautogui.click(950, 1031, duration=wegzeit1)  # Solid einblenden

    pyautogui.doubleClick(986, 1127, duration=wegzeit1)  # auf schatten klicken
    pyautogui.click(1756, 109, duration=wegzeit1)       #Profilkurfe erzeugen
    time.sleep(0.5)

    # Bauteil treffen - statt time.sleep(5)
    #def show_message_box():
        #root = tk.Tk()
        #root.withdraw()  # Hauptfenster ausblenden
        #root.attributes("-topmost", True)
        #root.update()  # Fenster sofort anzeigen
        #root.focus_force()  # Fenster erhält den Fokus
        #messagebox.showinfo("Bauteil getroffen?", "Bitte klicken Sie auf OK, um fortzufahren.")
        #root.destroy()  # Fenster nach Bestätigung schließen

    pyautogui.doubleClick(2205, 814, duration=wegzeit1)   #mittig auf bauteil
    time.sleep(0.5)


    # Messagebox anzeigen und auf Benutzerklick warten
    #show_message_box()

    pyautogui.click(1010, 329, duration=wegzeit1)  # OK Klicken

    pyautogui.click(1075, 140, duration=wegzeit1)  # Simulation starten

