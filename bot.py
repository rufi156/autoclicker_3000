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
CONFIDENCE = 0.9

def collect_achiev():
    """
    checks whether achievements are available, if true then collects them and exits achievements window
    """
    run = ag.locateOnScreen('pic/run_is_on.png', region=REGION, confidence=CONFIDENCE)
    while run is not None:
        achiev = None
        while achiev is None:
            achiev = ag.locateCenterOnScreen('pic/achievements_on.png', region=REGION, confidence=CONFIDENCE)
            time.sleep(1)
        print('achiev found')

        exit = None
        while exit is None:
            ag.click(achiev[0], achiev[1])
            time.sleep(0.1)
            exit = ag.locateCenterOnScreen('pic/exit.png', region=REGION, confidence=CONFIDENCE)
        print('achiev entered')

        collect = None
        while collect is None:
            collect = ag.locateAllOnScreen('pic/achievement_collectable.png', region=REGION, confidence=CONFIDENCE)

        centers = list(map(lambda x: ag.center(x), collect))
        for c in centers:
            ag.click(c[0], c[1])
            time.sleep(0.05)
        print('achiev collected')

        ag.click(exit[0], exit[1])
        print('exit')

def reset_run(level):
    settings = None
    while settings is None:
        settings = ag.locateCenterOnScreen('pic/settings.png', region=REGION, confidence=CONFIDENCE)
        time.sleep(1)
    print('settings found')

    map = None
    while map is None:
        ag.click(settings[0], settings[1])
        time.sleep(0.1)
        map = ag.locateCenterOnScreen('pic/map_select.png', region=REGION, confidence=CONFIDENCE)
    print('settings entered')

    mode = None
    while mode is None:
        ag.click(map[0], map[1])
        time.sleep(0.1)
        mode = ag.locateAllOnScreen('pic/normal.png', region=REGION, confidence=CONFIDENCE)
    print('mode entered')

    centers = list(map(lambda x: ag.center(x), mode))
    selected_mode = centers[level]

    confirm = None
    while confirm is None:
        ag.click(selected_mode[0], selected_mode[1])
        time.sleep(0.1)
        confirm = ag.locateCenterOnScreen('pic/confirm.png', region=REGION, confidence=CONFIDENCE)
    print('pick_monster entered')

    in_game = None
    while in_game is None:
        ag.click(confirm[0], confirm[1])
        time.sleep(0.1)
        confirm = ag.locateCenterOnScreen('pic/run_is_on.png', region=REGION, confidence=CONFIDENCE)
    print('run started')

#reset_run(0)
collect_achiev()
print('done')
