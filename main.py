import cv2
import math
from tkinter import *
import pyautogui
import time
import numpy as np
import matplotlib.pyplot as plt
import win32api, win32con
import keyboard
from collections import deque  

from utils import MultiScaleTemplateMatcher

CAPTURE_AREA = [None, None]

QUIT = False # We loop in-game until this is set to True.

CLICK_MEMORY_SIZE = 3 # This defines how many of the coordinates of the last clicked areas we keep in memory.

def terminate_program():
    global QUIT
    
    QUIT = True
    
    exit(0)

keyboard.add_hotkey('c', terminate_program)

# This defines when two locations are considered as equal.
def is_the_same_location(loc1, loc2):
    return math.fabs(loc1[0] - loc2[0]) < 50 and math.fabs(loc1[1] - loc2[1]) < 50

def was_position_already_clicked(loc):
    for p in last_click_positions:
        if is_the_same_location(loc, p):
            return True
    
    return False

# Select the area of the screen that we will use as inputs.
def callback(event):
    global CAPTURE_AREA

    if CAPTURE_AREA[0] is None:
        CAPTURE_AREA[0] = (event.x, event.y)

        print("Click on the bottom right corner of the area.")
    elif CAPTURE_AREA[1] is None:
        CAPTURE_AREA[1] = (event.x, event.y)
    
        root.quit()

        root.destroy()

root = Tk()

w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.overrideredirect(1)
root.geometry("%dx%d+0+0" % (w, h))

root.bind("<Button-1>", callback)

root.attributes('-alpha', 0.3)

print("Click on the top left corner of the area.")

root.mainloop()

time.sleep(2)

template_matcher = MultiScaleTemplateMatcher(template=cv2.Canny(cv2.imread("img/template.png", 0), 50, 200))
last_click_positions = deque([(0,0)] * CLICK_MEMORY_SIZE)

while not QUIT:
    img = np.array(pyautogui.screenshot())[CAPTURE_AREA[0][1]:CAPTURE_AREA[1][1], CAPTURE_AREA[0][0]:CAPTURE_AREA[1][0], :]

    img = np.where(np.logical_or(img[:, :, 0] < 180, img[:, :, 0] > 220), 0, 255).astype(np.uint8)

    rectangle = template_matcher.match_image(img)

    if rectangle:
        center = (rectangle[0][0] + (rectangle[1][0] - rectangle[0][0]) // 2, rectangle[0][1] + (rectangle[1][1] - rectangle[0][1]) // 2)
        
        x, y = CAPTURE_AREA[0][0] + center[0], CAPTURE_AREA[0][1] + center[1]

        if not was_position_already_clicked((x,y)):
            # Correct the mouse cursor to point to the target
            x = x - 18
            y = y - 25

            win32api.SetCursorPos((x, y))

            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
            time.sleep(0.5)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
            
            # Remove the first coordinate and append the new one
            last_click_positions.append((x,y))
            last_click_positions.popleft()