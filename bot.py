import numpy as np
from sklearn.cluster import DBSCAN
import os
import argparse
import datetime
from pyautogui import *
import threading
import pyautogui as ag
import pygetwindow as gw
import time
import keyboard
from PIL import ImageGrab
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

###
#Bot for Summoners Greed 31.01.2022
#farming ads for stones for special monsters:
#   king normal > wait for ad seller > if stones > watch&collect > restart
#farming jr normal for gems and gold
#   parallel collect gems for achievements, decline offers, reset run when complete
#
#farming ads:
#ads last ~35s and end with double arrow  or x in right upper corner
#/pic/x and /pic/arrow contain known variations of those
#all are tested, if found the ad can be skipped
#if arrow/x is not recognised it waits for manual user click
#
###

#find window with BlueStacks and set that as working region
region_window = gw.getWindowsWithTitle('BlueStack')[0]
REGION = (region_window.left, region_window.top, region_window.width, region_window.height)
CONFIDENCE = 0.9
PICTURE_PATH = 'pic/'

def cluster(array, sort_by):
    """
    Clusters points. Img recognition often finds mutiple instances. It reduces it to number of points = clusters
    Arg: array of points, 0,1 sort by point.x or point.y
    Ret: points representing clusters
    """
    clusters = DBSCAN(eps=10, min_samples=1).fit(array)
    dic = {}
    for i,cluster_label in enumerate(clusters.labels_):
        dic[cluster_label] = array[i]
    representatives = list(dic.values())
    representatives = sorted(representatives, key=lambda tup: tup[1])
    return representatives

def locate(pic, timeout=3600):
    """
    try to find given image for timeout seconds or until found
    Arg: img to serach for
    Ret:    0 timeout
            1 point of center of the img found
    """
    point = None
    timer = 0
    while timer<timeout and point is None:
        point = ag.locateCenterOnScreen(PICTURE_PATH+pic, region=REGION, confidence=CONFIDENCE)
        time.sleep(1)
        timer += 1
    if timer == timeout:
        return 0
    else:
        return point

def locateAll(pic, timeout=3600):
    """
    try to find all instances of given img
    Arg: img
    Ret: array of center points of found img instances
    """
    points = []
    timer = 0
    while timer<timeout and len(points) == 0:
        points = list(ag.locateAllOnScreen(PICTURE_PATH+pic, region=REGION, confidence=CONFIDENCE))
        time.sleep(1)
        timer += 1
    if timer == timeout:
        return 0
    else:
        #centers = list(map(lambda x: ag.center(x), list(point)))
        centers = [ag.center(x) for x in points]
        centers = cluster(centers, 1)
        return centers

def click_until(point, until, timeout=60*60, conf_modifier=0):
    """
    try to click on point until img is detected as a safeguard from faulty clicks
    Arg: point, img, optionl conf_modifier to modify confidence of img search
    Ret:    0 timeout
            1 center point of img found
    """
    exit = None
    timer = 0
    while timer<timeout and exit is None:
        ag.click(point[0], point[1])
        time.sleep(0.5)
        timer += 0.5
        exit = ag.locateCenterOnScreen(PICTURE_PATH+until, region=REGION, confidence=CONFIDENCE+conf_modifier)
    if timer == timeout:
        return 0
    else:
        return exit

def collect_achiev(achiev):
    """
    collect avaiable gems for achievements
    Arg: center point of achievements button
    Ret:    0 failed to open achievements
            1 gems collected
    """
    exit = click_until(achiev, 'exit.png')
    if not exit:
        return 0

    centers = locateAll('achievement_collectable.png')
    for c in centers:
        ag.click(c[0], c[1])
        time.sleep(0.05)

    ag.click(exit[0], exit[1])
    return 1

def achiev():
    """
    checks if there are any achievements completed > attempts to collect them
    """
    achiev = None
    while True:
        achiev = locate('achievements_on.png')
        if not achiev:
            print('timeout')
            continue
        else:
            print('achiev found')
            break
    if not collect_achiev(achiev):
        print('timeout')
    else:
        print('achiev collected')

def achiev_loop():
    """
    Indefinite achiev()
    """
    while True:
        achiev = None
        while True:
            achiev = locate('achievements_on.png')
            if not achiev:
                print('timeout')
                continue
            else:
                print('achiev found')
                break
        if not collect_achiev(achiev):
            print('timeout')
        else:
            print('achiev collected')

def reset_run(level):
    """
    restets level
    Arg: reset into given level
    """
    settings = locate('settings.png')
    if not settings:
        print('settings timeout')
    else:
        print('settings found')

    map = click_until(settings, 'map_select.png')
    if not map:
        print('settings timeout')
    else:
        print('settings entered')

    click_until(map, 'normal.png')
    mode = locateAll('normal.png')
    mode = mode[level]
    confirm = click_until(mode, 'confirm.png')
    click_until(confirm, 'settings.png')
    print('run restarted')

def handleFinish():
    """
    checks for finished run screen and resets run if found
    """
    while True:
        end = ag.locateCenterOnScreen('pic/finished_run.png', region=REGION, confidence=CONFIDENCE)

        if end is not None:
            print('run ended')
            ag.click(end[0], end[1])
            mode = locateAll('normal.png')
            mode = mode[2]
            confirm = click_until(mode, 'confirm.png')
            click_until(confirm, 'settings.png')
            print('run restarted')
            #optional logging of restarts
            #with open('restart_log.txt', 'a') as log:
            #    log.write('restart at: %s\n' % (datetime.datetime.now()))
        time.sleep(60)

def declineOffers():
    """
    checks for offers popups and declines them
    """
    while True:
        offer = ag.locateCenterOnScreen('pic/decline_offer.png', region=REGION, confidence=CONFIDENCE)
        if offer is not None:
            ag.click(offer[0], offer[1])
        time.sleep(5)

def enter_ad():
    """
    checks for ads accepts if stone ads, declines if other
    """
    ad = None
    stone = None
    timer = 0
    while timer<35 and ad is None:
        ad = ag.locateCenterOnScreen('pic/ad.png', region=REGION, confidence=CONFIDENCE)
        time.sleep(0.5)
        timer += 0.5

    if timer == 35:
        print('timeout')
        return 0
    stone = ag.locateCenterOnScreen('pic/stone.png', region=REGION, confidence=CONFIDENCE)
    if stone is not None:
        print('ad found')
        ag.click(ad[0], ad[1])
        return 1
    else:
        offer = ag.locateCenterOnScreen('pic/decline_offer.png', region=REGION, confidence=CONFIDENCE)
        ag.click(offer[0], offer[1])
        return 0

def skip_ad():
    """
    checks for arrows and x at the end of ad and clicks them to end ad watching
    """
    arrow_list = list(filter(lambda file: file.endswith('.PNG'), os.listdir('./pic/arrow')))
    arrow = None
    timer = 0
    while timer<5 and arrow is None:
        for image in arrow_list:
            arrow = ag.locateCenterOnScreen('pic/arrow/'+image, grayscale=True, region=REGION, confidence=CONFIDENCE)
            if arrow is not None:
                break
        time.sleep(1)
        timer += 1

    if timer == 5:
        print('arrow timeout')
    else:
        print('arrow found')
        ag.click(arrow[0], arrow[1])

    x_list = list(filter(lambda file: file.endswith('.PNG'), os.listdir('./pic/x')))
    exit = None
    while exit is None:
        for image in x_list:
            exit = ag.locateCenterOnScreen('pic/x/'+image, grayscale=True, region=REGION, confidence=CONFIDENCE)
            if exit is not None:
                break
        time.sleep(1)
    print('x found')

    ag.click(exit[0], exit[1])

    ad = locate('ad_accept_reward.png')
    ag.click(ad[0], ad[1])
    print('ad reward collected')

def summon():
    """
    useup orb to summon monsters
    """
    portal = locate('summon_ready.png', 3)
    if not portal:
        return 0
    summon = click_until(portal, 'orb_summon.png')
    skip = click_until(summon, 'skip_summon.png')
    conf = click_until(skip, 'confirm_summon.png')
    exit = click_until(conf, 'exit_summon.png')
    ag.click(exit[0], exit[1])
    return 1

def farm_jr():
    """
    parallel collect gems for achievements, decline offers and reset run when finished
    """
    t_1 = threading.Thread(target=handleFinish)
    t_2 = threading.Thread(target=achiev_loop)
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
    """
    checks for relevant ads, watches them and collects rewards
    then reset run
    parallel collect available achievements
    """
    t_1 = threading.Thread(target=achiev_loop)
    t_1.daemon = True
    t_1.start()
    while not keyboard.is_pressed('q'):
        if enter_ad():
            time.sleep(40)
            skip_ad()
            reset_run(0)
        else:
            reset_run(0)

def farm_summon():
    """
    summon and collect achievements interchangably
    simultaneously decline offers (not sure if working properly, not colliding with the loop)
    """
    t_1 = threading.Thread(target=declineOffers)
    t_1.daemon = True
    t_1.start()
    while summon():
        achiev()

def main(args):
    modeList = [k for k, v in vars(args).items() if v]
    if 'lvl' in modeList:
        level = vars(args)['lvl']

    if 's' in modeList:
        farm_summon()
    elif 'ad' in modeList:
        farm_ad()
    elif 'jr' in modeList:
        farm_jr()
    elif 'a' in modeList:
        achiev_loop()
    elif 'r' in modeList:
        reset_run(level)
    else:
        print('wrong option, select -h for help')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automate repetetive tasks in game.')
    actionType = parser.add_mutually_exclusive_group(required=True)
    actionType.add_argument("-s", action="store_true", help="spend ords for summonings")
    actionType.add_argument("-ad", action="store_true", help="farm ads for stones")
    actionType.add_argument("-jr", action="store_true", help="farm jr")
    actionType.add_argument("-a", action="store_true", help="collect achievemens")
    actionType.add_argument("-r", action="store_true", help="reset run")
    actionType = parser.add_mutually_exclusive_group(required=False)
    actionType.add_argument("-lvl", type=int, help="reset to level 0-King, 1-Chief, 2-JR", choices = [0,1,2])
    args = parser.parse_args()
    main(args)


#todo:
#interface to call the script
#decline offers doesnt always work, maybe doesnt work on sellers only on ads?
