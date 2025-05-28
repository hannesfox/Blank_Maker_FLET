import pyautogui
import time
import tkinter as tk
from tkinter import messagebox
import time

verweilzeit = 0.5    

def start_mausbewegungen(partheight):
    #  Masken - feature u werkzeugweg abwählen
    time.sleep(verweilzeit)
    pyautogui.click(x=3111, y=1289, duration= 1)
    time.sleep(verweilzeit)
    pyautogui.click(x=3111, y=1306)
    time.sleep(verweilzeit)

    # Mit pyautogui Strg + A drücken - alles markieren
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(verweilzeit)

    # Arbeitsebene vorne auswählen
    pyautogui.click(x=1685, y=81)
    time.sleep(verweilzeit)
    pyautogui.click(x=1685, y=191)
    time.sleep(verweilzeit)

    # Mit pyautogui Strg + C drücken
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.2)

    #-------------------------------------------------
    

    # Rotieren
    
    pyautogui.press('r')
    time.sleep(0.1)
    pyautogui.press('o')
    time.sleep(0.1)
    pyautogui.click(x=2119, y=660)#Originale
    time.sleep(0.1)
    for _ in range(1):
        pyautogui.press('tab')
        time.sleep(0.1)
    pyautogui.typewrite("180")
    time.sleep(0.2)

    #-------------------------------------------------

    

    # Zwei Bilder vergleichen

    def find_image(image_path, threshold=0.8):
        location = pyautogui.locateOnScreen(image_path, confidence=threshold)
        return location

    # Dateipfade Bilder
    suchbild_pfad_1 = 'b1.png'
    kontrollbild_pfad_1 = 'b2.png'
    

    # schleife für die Suche nach b1 und b2
    
    while True:
        b1_location = find_image(suchbild_pfad_1)

        if b1_location:
            pyautogui.click(b1_location.left + b1_location.width / 2, b1_location.top + b1_location.height / 2)
            #print("b1 gefunden")
            time.sleep(0.5)  
            pyautogui.click(x=2153, y=816)
            break  

        # Nur wenn b1 nicht gefunden wurde, nach b2 suchen
        b2_location = find_image(kontrollbild_pfad_1)

        if b2_location:
            pyautogui.click(x=2153, y=816)
            #print("b2 gefunden")
            time.sleep(0.5)  
            break
            
        time.sleep(1)


    time.sleep(verweilzeit)

    #arbeitsebene xyz auswäheln
    pyautogui.click(x=1685, y=80)
    time.sleep(verweilzeit)
    pyautogui.click(x=1685, y=116)   
    time.sleep(verweilzeit)

    # Mit pyautogui Strg + C drücken
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.2)

    #-------------------------------------------------
       
    # Verschieben suchen
    pyautogui.press('v')
    time.sleep(0.1)
    
    pyautogui.click(x=2119, y=660)#Originale
    time.sleep(0.1)
    #for _ in range(4):
        #pyautogui.press('tab')
        #time.sleep(0.1)
    #pyautogui.typewrite("180")
    #time.sleep(0.2)
           
    #-------------------------------------------------

    #  unter modifizieren, verschieben bauteil
    #pyautogui.click(x=1857, y=251)#auswahl
    #time.sleep(verweilzeit)
    #pyautogui.click(x=1859, y=450)#verschieben
    #time.sleep(verweilzeit)
     
    #pyautogui.click(x=1673, y=275)#originale
    #time.sleep(verweilzeit)

    # Vier Mal Tab drücken
    for _ in range(2):
        pyautogui.press('tab')

    pyautogui.typewrite("0") # X 0 eintragen
    pyautogui.press('tab')
    pyautogui.typewrite("0") # Y 0 eintragen
    pyautogui.press('tab')

    # zu verschiebende höhe eintragen          
    
    pyautogui.typewrite(str(partheight))
    time.sleep(verweilzeit)

    # Enter drücken
    pyautogui.press('enter')

    # Einen Klick ausführen - freiklicken
    pyautogui.click(x=1021, y=177)
    time.sleep(verweilzeit)

    # Mit pyautogui F8 drücken - ISO Ansicht
    pyautogui.press('F8')
    time.sleep(verweilzeit)

    # Masken einblenden
    pyautogui.click(x=3103, y=1290)
    time.sleep(verweilzeit)
    pyautogui.click(x=3118 , y=1307)
    time.sleep(verweilzeit)

    #  Feature auswählen
    pyautogui.click(x=1477, y=80)
    time.sleep(verweilzeit)
    pyautogui.click(x=1477, y=132)
    time.sleep(verweilzeit)

    # Mit pyautogui Strg + A drücken
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(verweilzeit)

    # Mit pyautogui Strg + C drücken
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(2)

    #-------------------------------------------------
    pyautogui.press('s')
    time.sleep(0.1)
    pyautogui.press('y')
    time.sleep(0.1)
    pyautogui.click(x=2119, y=660)#Originale
    time.sleep(0.1)
    pyautogui.click(x=2088, y=751)#Y Achse
    time.sleep(0.1)
    
    
    #-------------------------------------------------
    

    # Einen Klick ausführen - freiklicken
    pyautogui.click(x=1021, y=177)
    time.sleep(verweilzeit)

    
    # Zwei Bilder vergleichen    
    

    # schleife für die Suche nach b3 und b4
    def find_image1(image_path, threshold=0.8):
        location = pyautogui.locateOnScreen(image_path, confidence=threshold)
        return location

    # pfade Bilder
    suchbild_pfad_3 = 'b3.png'
    kontrollbild_pfad_4 = 'b4.png'
    

    # schleife für die Suche nach b1 und b2
    
    while True:
        b3_location = find_image1(suchbild_pfad_3)

        if b3_location:
            pyautogui.click(b3_location.left + b3_location.width / 2, b3_location.top + b3_location.height / 2)
            #print("b3 gefunden")
            time.sleep(0.5)  
            pyautogui.click(x=2153, y=816)
            break  

        # Nur wenn b1 nicht gefunden wurde, nach b2 suchen
        b4_location = find_image(kontrollbild_pfad_4)

        if b4_location:
            pyautogui.click(x=2153, y=816)
            #print("b4 gefunden")
            time.sleep(0.5)  
            break
            
        time.sleep(1)



    # Eine Position mit pyautogui anklicken und Enter drücken
    pyautogui.click(x=2152, y=815)
    time.sleep(verweilzeit)
    pyautogui.press('enter')
    time.sleep(verweilzeit)
 
    # Zwei Positionen mit pyautogui anklicken - Konturzug
    pyautogui.click(x=1477, y=82)#alles
    time.sleep(verweilzeit)
    pyautogui.click(x=1477, y=251)#korturzug
    time.sleep(verweilzeit)

    # Mit pyautogui Strg + A drücken
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(verweilzeit)

    # Eine Position mit pyautogui anklicken - Bearbeitungsseite
    pyautogui.click(x=239, y=701)
    time.sleep(verweilzeit)

    # Mit pyautogui zweimal Pfeiltaste nach oben drücken
    pyautogui.press('up')
    time.sleep(0.2)
    pyautogui.press('up')
    time.sleep(verweilzeit)

    # Eine Position mit pyautogui anklicken - Freiklick
    pyautogui.click(x=1020, y=175)
    time.sleep(verweilzeit)

    # Zwei Positionen mit pyautogui anklicken - Alles
    pyautogui.click(x=1477, y=80, duration= 1)#alles
    time.sleep(verweilzeit)
    pyautogui.click(x=1477 , y=101)#alles eins unterhalb
    
    # Neuberechnen
    pyautogui.click(x=1514, y=137, duration= 1)
    
    


    def show_message_box1():
        root = tk.Tk()
        root.withdraw()  # Hauptfenster ausblenden
        root.attributes("-topmost", True)  # Messagebox bleibt im Vordergrund
        root.update()  # Fenster sofort anzeigen
        root.focus_force()  # Fenster erhält den Fokus
        messagebox.showinfo("B-Seiten Automatisierung abgeschlossen", "Klicke auf OK um weiter Programmieren zu können.")
        root.destroy()  # Fenster nach Bestätigung schließen
    show_message_box1()    
    pass
