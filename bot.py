from pyautogui import *
import pyautogui as ag
import pygetwindow as gw
import time
import keyboard
import random
import win32api, win32con
from PIL import ImageGrab
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

region_window = gw.getWindowsWithTitle('BlueStack')[0]
REGION = (region_window.left, region_window.top, region_window.width, region_window.height)

achiev = None
while achiev is None:
    achiev = ag.locateCenterOnScreen('pic/achievements_on.png', region=REGION, confidence=0.9)
    time.sleep(1)
print("achev found")

exit = None
while exit is None:
    ag.click(achiev[0], achiev[1])
    time.sleep(0.1)
    exit = ag.locateCenterOnScreen('pic/exit_achiev.png', region=REGION, confidence=0.9)
print('achiev entered')

collect = None
while collect is None:
    collect = ag.locateAllOnScreen('pic/achievement_collectable.png', region=REGION, confidence=0.9)
print('collectibles found')

centers = list(map(lambda x: ag.center(x), collect))
for c in centers:
    ag.click(c[0], c[1])
    time.sleep(0.05)

ag.click(exit[0], exit[1])
