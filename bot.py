import numpy as np
from sklearn.cluster import KMeans
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
PICTURE_PATH = 'pic/'

def cluster(array, cluster_num, sort_by):
    k_means = KMeans(init='k-means++', n_clusters=cluster_num, n_init=10)
    k_means.fit(array)
    cluster_centers = k_means.cluster_centers_
    sorted = cluster_centers[cluster_centers[:,sort_by].argsort()]
    return sorted

def locate(pic, timeout=60*60):
    point = None
    point = 0
    while timer<timeout and point is None:
        point = ag.locateCenterOnScreen(PICTURE_PATH+pic, region=REGION, confidence=CONFIDENCE)
        time.sleep(1)
        timer += 1
    if timer == timeout:
        return 0
    else:
        return point

def click_until(point, until, timeout=60*60):
    exit = None
    timer = 0
    while timer<timeout and exit is None:
        ag.click(point[0], point[1])
        time.sleep(0.5)
        timer += 0.5
        exit = ag.locateCenterOnScreen(PICTURE_PATH+until, region=REGION, confidence=CONFIDENCE)
    if timer == timeout:
        return 0
    else:
        return exit


def collect_achiev():
    """
    checks whether achievements are available, if true then collects them and exits achievements window
    """
    while True:
        achiev = locate('achievements_on.png')
        if not achiev:
            print('timeout')
            continue

        exit = click_until(achiev, 'exit.png')
        if not exit:
            print('timeout')
            continue
        else:
            print('achiev entered')

        collect = ag.locateAllOnScreen('pic/achievement_collectable.png', region=REGION, confidence=CONFIDENCE)
        centers = list(map(lambda x: ag.center(x), collect))
        centers = cluster(centers, 3, 1)

        for c in centers:
            ag.click(c[0], c[1])
            time.sleep(0.05)
        print('achiev collected')

        ag.click(exit[0], exit[1])
        print('achiev exited')

def reset_run():
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
        mode = ag.locateCenterOnScreen('pic/king_normal.png', region=REGION, confidence=CONFIDENCE)
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
    while timer<35 and ad is None:
        ad = ag.locateCenterOnScreen('pic/ad.png', region=REGION, confidence=CONFIDENCE)
        time.sleep(1)
        timer += 1

    if timer == 35:
        print('timeout')
        return 0
    stone = ag.locateCenterOnScreen('pic/stone.png', region=REGION, confidence=CONFIDENCE)
    gem = ag.locateCenterOnScreen('pic/gem.png', region=REGION, confidence=CONFIDENCE)
    if stone is not None or gem is not None:
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

    if timer == 5:
        print('arrow timeout')
    else:
        print('arrow found')
        #print([arrow, arrow2, arrow3,arrow4])
        arrow = list(filter(None, [arrow,arrow2,arrow3,arrow4]))[0]
        ag.click(arrow[0], arrow[1])

    while exit is None and exit2 is None and exit3 is None and exit4 is None:
        exit = ag.locateCenterOnScreen('pic/ad_x.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        exit2 = ag.locateCenterOnScreen('pic/ad_x2.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        exit3 = ag.locateCenterOnScreen('pic/ad_x3.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        exit4 = ag.locateCenterOnScreen('pic/ad_x4.png', grayscale=True, region=REGION, confidence=CONFIDENCE)
        time.sleep(1)
    print('x found')

    #print([exit, exit2, exit3, exit4])
    exit = list(filter(None, [exit, exit2, exit3, exit4]))[0]
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

    while not keyboard.is_pressed('q'):
        pass


def farm_ads():
    t_1 = threading.Thread(target=collect_achiev)
    t_1.daemon = True
    t_1.start()
    while not keyboard.is_pressed('q'):
        if enter_ad():
            time.sleep(40)
            skip_ad()
            reset_run()
        else:
            reset_run()

#farm_ads()
#farm_jr()



#todo:
#unify locateAllOnScreen
#add try all x/arrow variations
#add 2 modes:
#   jr + achiev + reset
#   king + wait_for_ad + restart/watch_add+restart
#parallel achiev + ads
