from pyautogui import *
import threading
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
    while True:
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
        time.sleep(0.2)
        map = ag.locateCenterOnScreen('pic/map_select.png', region=REGION, confidence=CONFIDENCE)
    print('settings entered')

    mode = None
    while mode is None:
        ag.click(map[0], map[1])
        time.sleep(0.2)
        mode = ag.locateCenterOnScreen('pic/'+level+'_normal.png', region=REGION, confidence=CONFIDENCE)
    print('mode entered')

    confirm = None
    while confirm is None:
        ag.click(mode[0], mode[1]+25)
        time.sleep(0.2)
        confirm = ag.locateCenterOnScreen('pic/confirm.png', region=REGION, confidence=CONFIDENCE)
    print('pick_monster entered')

    x = confirm[0]
    y = confirm[1]
    while confirm is not None:
        ag.click(x, y)
        time.sleep(0.2)
        confirm = ag.locateCenterOnScreen('pic/confirm.png', region=REGION, confidence=CONFIDENCE)
    print('run started')

def enter_ad():
    ad = None
    stone = None
    timer = 0
    while timer<30 and ad is None:
            ad = ag.locateCenterOnScreen('pic/ad.png', region=REGION, confidence=CONFIDENCE)
            time.sleep(1)
            timer += 1
    if timer = 30:
        return 0
    stone = ag.locateCenterOnScreen('pic/stone.png', region=REGION, confidence=CONFIDENCE)
    gem = ag.locateCenterOnScreen('pic/gem.png', region=REGION, confidence=CONFIDENCE)
    if ad is not None and (stone is not None or gem is not None):
        print('ad found')
        ag.click(ad[0], ad[1])
        return 1
    else:
        offer = ag.locateCenterOnScreen('pic/decline_offer.png', region=REGION, confidence=CONFIDENCE)
        ag.click(offer[0], offer[1])
        return 0


def skip_ad():
    arrow = None
    arrow2 = None
    arrow3 = None
    arrow4 = None
    exit = None
    exit2 = None
    exit3 = None
    exit4 = None
    timer = 0
    while timer<5 and arrow is None and arrow2 is None and arrow3 is None and arrow4 is None:
        arrow = ag.locateCenterOnScreen('pic/ad_arrow.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        arrow2 = ag.locateCenterOnScreen('pic/ad_arrow2.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        arrow3 = ag.locateCenterOnScreen('pic/ad_arrow3.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        arrow4 = ag.locateCenterOnScreen('pic/ad_arrow4.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        time.sleep(1)
        timer += 1
        print(timer)
    if timer<5:
        print('arrow found')
        print([arrow, arrow2, arrow3,arrow4])
        arrow = list(filter(None, [arrow,arrow2,arrow3,arrow4]))[0]

        if arrow is not None:
            ag.click(arrow[0], arrow[1])

    while exit is None and exit2 is None and exit3 is None and exit4 is None:
        exit = ag.locateCenterOnScreen('pic/ad_x.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        exit2 = ag.locateCenterOnScreen('pic/ad_x2.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        exit3 = ag.locateCenterOnScreen('pic/ad_x3.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        exit4 = ag.locateCenterOnScreen('pic/ad_x4.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        time.sleep(1)
    print('x found')

    print([exit, exit2, exit3, exit4])
    exit = list(filter(None, [exit, exit2, exit3, exit4]))[0]
    if exit is not None:
        ag.click(exit[0], exit[1])

    ad = None
    while ad is None:
        time.sleep(0.2)
        ad = ag.locateCenterOnScreen('pic/ad_accept_reward.png', region=REGION, confidence=CONFIDENCE)
    print('ad exited')

    while ad is not None:
        ag.click(ad[0], ad[1])
        time.sleep(0.2)
        ad = ag.locateCenterOnScreen('pic/ad_accept_reward.png', region=REGION, confidence=CONFIDENCE)
    print('ad collected')

def handleFinish():
    while True:
        end = ag.locateCenterOnScreen('pic/finished_run.png', region=REGION, confidence=CONFIDENCE)

        if end is not None:
            ag.click(end[0], end[1])
            mode = None
            while mode is None:
                time.sleep(0.2)
                mode = ag.locateCenterOnScreen('pic/jr_normal.png', region=REGION, confidence=CONFIDENCE)
            print('mode entered')

            confirm = None
            while confirm is None:
                ag.click(mode[0], mode[1]+25)
                time.sleep(0.2)
                confirm = ag.locateCenterOnScreen('pic/confirm.png', region=REGION, confidence=CONFIDENCE)
            print('pick_monster entered')

            x = confirm[0]
            y = confirm[1]
            while confirm is not None:
                ag.click(x, y)
                time.sleep(0.2)
                confirm = ag.locateCenterOnScreen('pic/confirm.png', region=REGION, confidence=CONFIDENCE)
            print('run started')
            time.sleep(600)
        else:
            time.sleep(600)

def declineOffers():
    while True:
        offer = ag.locateCenterOnScreen('pic/decline_offer.png', region=REGION, confidence=CONFIDENCE)
        if offer is None:
            time.sleep(5)
        else:
            ag.click(offer[0], offer[1])
            time.sleep(5)

def farm_jr():
    t_1 = threading.Thread(target=handleFinish)
    t_2 = threading.Thread(target=collect_achiev)
    t_3 = threading.Thread(target=declineOffers)
    t_1.daemon = True
    t_2.daemon = True
    t_3.daemon = True

    t_1.start()
    t_2.start()
    t_3.start()

#farm_jr()
def farm_ads():
    t_1 = threading.Thread(target=collect_achiev)
    t_1.daemon = True
    t_1.start()
    while True:
        if enter_ad():
            time.sleep(40)
            skip_ad()
            reset_run('king')
        else:
            reset_run('king')

#farm_ads()

#todo:
#unify locateAllOnScreen
#add try all x/arrow variations
#add 2 modes:
#   jr + achiev + reset
#   king + wait_for_ad + restart/watch_add+restart
#parallel achiev + ads
