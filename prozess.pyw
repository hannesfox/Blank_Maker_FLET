import pyautogui
import keyboard
import time
from threading import Thread

def process_images():
    try:
        image_pos = pyautogui.locateOnScreen('Bilder/image1.png', confidence=0.7, grayscale=True)
        x, y = pyautogui.center(image_pos)
        time.sleep(0.05)
        pyautogui.click(x, y)
        time.sleep(0.05)
        image_pos = pyautogui.locateOnScreen('Bilder/image2.png', confidence=0.7, grayscale=True)
        x, y = pyautogui.center(image_pos)
        time.sleep(0.05)
        pyautogui.click(x, y)
        time.sleep(0.05)
    except pyautogui.ImageNotFoundException:
        pass

def on_f12_pressed(event):
    pyautogui.rightClick()
    time.sleep(0.05)
    Thread(target=process_images).start()
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')


keyboard.on_press_key('F12', on_f12_pressed)

while True:
    time.sleep(0.05)
