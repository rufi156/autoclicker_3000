
from discordwebhook import Discord
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
#Author: RafalRobet Karpiński
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
#When using on different device, resolution doesnt matter, scaling does matter. Hence bluestacs windows size does matter.
###

#find window with BlueStacks and set that as working region
region_window = gw.getWindowsWithTitle('BlueStack')[0]
# pics taken at REGION = (1276, 69, 381, 747) and screen Size(width=1920, height=1080)
region_window.resizeTo(381, 747)
REGION = (region_window.left, region_window.top, region_window.width, region_window.height)
print(f'window: {REGION} screen: {ag.size()}')
CONFIDENCE = 0.9
PICTURE_PATH = 'pic/'
WEBHOOK = ''
with open('webhook.txt', 'r') as f:
    WEBHOOK = f.readline()


def notifyInactivity(limit=60*5):
    discord = Discord(url=WEBHOOK)
    timeout = limit
    refractory_period = 60*60
    last_notification = 0.0
    while True:
        isNotMoving = 0
        oldPosition = ag.position()
        while isNotMoving < timeout:
            time.sleep(0.5)
            newPosition = ag.position()
            if newPosition == oldPosition:
                isNotMoving = round(isNotMoving+0.5, 1)
            else:
                isNotMoving = 0
            oldPosition = newPosition
        if time.time() - last_notification >= refractory_period:
            discord.post(content=f'mouse stationary for {timeout/60} minutes')
            last_notification = time.time()

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

def locate(img, timeout=3600, gray=False):
    """
    try to find given image for timeout seconds or until found
    Arg: img to serach for
    Ret:    0 timeout
            1 point of center of the img found
    """
    point = None
    timer = 0
    while timer<timeout and point is None:
        point = ag.locateCenterOnScreen(PICTURE_PATH+img, grayscale=gray, region=REGION, confidence=CONFIDENCE)
        time.sleep(0.1)
        timer = round(timer+0.1, 1)
    if timer == timeout:
        return 0
    else:
        return point

def locate_n_click(img, timeout=3):
    pic = locate(img, timeout)
    if pic != 0:
        ag.click(pic.x, pic.y)
        return 1
    else:
        return 0

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
        time.sleep(0.5)
        timer = round(timer+0.5, 1)
    if timer == timeout:
        return 0
    else:
        #centers = list(map(lambda x: ag.center(x), list(point)))
        centers = [ag.center(x) for x in points]
        #print(centers)
        centers = cluster(centers, 1)
        #print(centers)
        return centers

def click_until(point, until, timeout=3600):
    """
    try to click on point until img is detected as a safeguard from faulty clicks
    Arg: point, img
    Ret:    0 timeout
            1 center point of img found
    """
    exit = None
    timer = 0
    while timer<timeout and exit is None:
        ag.click(point[0], point[1])
        time.sleep(0.5)
        timer = round(timer+0.5, 1)
        exit = ag.locateCenterOnScreen(PICTURE_PATH+until, region=REGION, confidence=CONFIDENCE)
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

    centers = locateAll('achievement_collectable.png', 10)
    if not centers:
        ag.click(exit[0], exit[1])
        return 0
    for c in centers:
        ag.click(c[0], c[1])
        time.sleep(0.05)

    ag.click(exit[0], exit[1])
    return 1

def achiev():
    """
    checks if there are any achievements completed > attempts to collect them
    """
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
        achiev = locate('achievements_on.png')
        if not achiev:
            print('timeout')
            continue
        else:
            print('achiev found')
            if not collect_achiev(achiev):
                #if entered achiev but no exit found this failsafe exits achiev
                locate_n_click('exit.png')
                print('timeout')
            else:
                print('achiev collected')

def reset_run(level, normal = 1):
    """
    restets level
    Arg: reset into given level
    """
    settings = locate('settings.png')
    if not settings:
        print('settings timeout')
    else:
        print('settings found')
    """
    map = click_until(settings, 'map_select.png')
    if not map:
        print('settings timeout')
    else:
        print('settings entered')
    """
    click_until((settings.x, settings.y-30), 'normal.png')
    
    if normal:
        mode = locateAll('normal.png')
    else:
        mode = locateAll('hard.png')
    mode = mode[level]
    confirm = click_until(mode, 'confirm.png')
    click_until(confirm, 'settings.png')
    print('run restarted')

def handleFinish(lvl=2, normal = 1):
    """
    checks for finished run screen and resets run if found
    """
    end = locate('finished_run.png')
    if not end:
        return 0
    print('run ended')
    click_until(end, 'normal.png')
    if normal:
        mode = locateAll('normal.png')
    else:
        mode = locateAll('hard.png')
    mode = mode[lvl]
    confirm = click_until(mode, 'confirm.png')
    click_until(confirm, 'settings.png')
    print('run restarted')
    return 1
    #optional logging of restarts
    #with open('restart_log.txt', 'a') as log:
    #    log.write('restart at: %s\n' % (datetime.datetime.now()))

def handleFinish_loop(lvl=2, normal=1):
    while True:
        handleFinish(lvl, normal)
        time.sleep(10)

def declineOffers():
    """
    checks for offers popups and declines them
    """
    while True:
        offer = ag.locateCenterOnScreen('pic/decline_offer.png', region=REGION, confidence=CONFIDENCE)
        offer2 = ag.locateCenterOnScreen('pic/seller_decline.png', region=REGION, confidence=CONFIDENCE)
        if offer is not None:
            ag.click(offer[0], offer[1])
        elif offer2 is not None:
            ag.click(offer2[0], offer2[1])
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
    if stone is None: #temp  change - farm all ads
        print('ad found')
        time.sleep(0.5)
        ag.click(ad[0], ad[1])
        return 1
    else:
        offer = ag.locateCenterOnScreen('pic/decline_offer.png', region=REGION, confidence=CONFIDENCE)
        time.sleep(0.05)
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
    click_until(portal, 'exit.png')
    summon = ag.locateCenterOnScreen(PICTURE_PATH+'orb_summon.png', region=REGION, confidence=CONFIDENCE)
    summon2 = ag.locateCenterOnScreen(PICTURE_PATH+'orb_summon10.png', region=REGION, confidence=CONFIDENCE)
    if summon is not None:
        skip = click_until(summon, 'skip_summon.png')
    elif summon2 is not None:
        skip = click_until(summon2, 'skip_summon.png')
    conf = click_until(skip, 'confirm_summon.png')
    exit = click_until(conf, 'exit.png')
    ag.click(exit[0], exit[1])
    return 1

def buy_all():
    """
    checks for offers popups and accepts them
    USE WITH ADBLOCKER
    """
    offer = ag.locateOnScreen('pic/seller_decline.png', region=REGION, confidence=CONFIDENCE)
    if offer is not None:
        offer_center = ag.center(offer)
        time.sleep(0.2)
        ag.click(offer_center.x + offer.width, offer_center.y)
        locate_n_click('ad_accept_reward.png')
    return 1

def buy_stones():
    """
    checks for seller accepts if stone seller, declines if other
    """
    while True:
        decline = locate('seller_decline.png', 60)
        if decline:
            time.sleep(0.3)
            ag.click(decline[0]+150, decline[1])
            reset_run(0)
        else:
            reset_run(0)
    #todo: ad stone verification

def farm_jr():
    """
    parallel collect gems for achievements, decline offers and reset run when finished
    """
    t_1 = threading.Thread(target=handleFinish_loop, args=(2,0), daemon=True)
    t_2 = threading.Thread(target=achiev_loop, daemon=True)
    #t_3 = threading.Thread(target=declineOffers)
    t_3 = threading.Thread(target=buy_all, daemon=True)
    t_4 = threading.Thread(target=notifyInactivity, daemon=True)

    t_1.start()
    t_2.start()
    t_3.start()
    t_4.start()

    while buy_all():
        time.sleep(2)

def farm_ads():
    """
    checks for relevant ads, watches them and collects rewards
    then reset run
    parallel collect available achievements
    """
    #t_1 = threading.Thread(target=achiev_loop)
    #t_1.daemon = True
    #t_1.start()
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
    t_1 = threading.Thread(target=declineOffers, daemon=True)
    t_2 = threading.Thread(target=notifyInactivity, daemon=True)
    t_1.start()
    t_2.start()
    while summon():
        achiev()

def farm_mythic():
    """
    summon red orbs for non epic, reset save file if summoned epic
    """
    discord = Discord(url=WEBHOOK)
    locate_n_click('exit.png', 6)
    locate_n_click('exit.png', 2)
    locate_n_click('settings.png')
    map = locate('map_select.png')
    x = map[0]+40
    y = map[1]
    ag.moveTo(x,y)
    ag.drag(0,-160,0.2,button='left')
    ag.click(ag.position()) #stop the scrolling animation
    if not locate_n_click('facebook_connected.png'):
        discord.post(content=f'Error: couldnt disconnect FB')
        return 0
    locate_n_click('exit.png')
    locate_n_click('summon_ready.png')
    locate_n_click('red_summon.png')
    locate_n_click('skip_summon.png')
    time.sleep(0.1)
    #epic = locate('epic_summon.png', 0.5)
    #legendary = locate('legendary_summon.png', 0.5)
    epic = ag.locateCenterOnScreen(PICTURE_PATH+'epic_summon.png', region=REGION, confidence=CONFIDENCE)
    legendary = ag.locateCenterOnScreen(PICTURE_PATH+'legendary_summon.png', region=REGION, confidence=CONFIDENCE)
    if not epic and not legendary:
        print('Mythic found!')
        discord.post(content=f'Mythic found!')
        return 0
    locate_n_click('confirm_summon.png')
    locate_n_click('exit.png')
    locate_n_click('settings.png')
    locate_n_click('fb_not_connected.png')
    locate_n_click('fb_connect_now.png')
    locate_n_click('fb_accept.png', 30)
    save = locate('save_found.png')
    ag.click(save.x, save.y+50)
    locate_n_click('save_confirm.png')
    return 1

def pekos_magic():
    """
    kill first two jr hard bosses and reset
    """
    t_1 = threading.Thread(target=achiev_loop, daemon=True)
    t_1.start()
    while not keyboard.is_pressed('q'):
        time.sleep(30)
        locate_n_click('settings.png',10)
        locate_n_click('map_select.png')
        hard = locateAll('hard.png')
        jr = hard[2]
        ag.click(jr[0], jr[1])
        conf = locate('confirm.png')
        click_until(conf, 'settings.png')

def cmg():
    """
    loading game to last wave fills offline gold chest
    collect, finish game, reload to last wave
    """
    discord = Discord(url=WEBHOOK)
    if not handleFinish(2,0):
        return 0
    set = locate('settings.png')
    click_until(set, 'map_select.png')
    map = locate('map_select.png')
    x = map[0]+40
    y = map[1]+20
    ag.moveTo(x,y)
    ag.drag(0,-150,0.3,button='left')
    ag.click(ag.position()) #stop the scrolling animation
    time.sleep(0.01)
    if not locate_n_click('facebook_connected.png'):
        #try to scroll again
        ag.moveTo(x,y)
        ag.drag(0,-150,0.3,button='left')
        ag.click(ag.position())
        time.sleep(0.01)
        if not locate_n_click('facebook_connected.png'):
            discord.post(content=f'Error: couldnt disconnect FB')
            return 0
    locate_n_click('fb_not_connected.png')
    if not locate_n_click('fb_connect_now.png'): #safeguard against not registered click, click_until cant be used
        locate_n_click('fb_not_connected.png')
        locate_n_click('fb_connect_now.png')
    locate_n_click('fb_accept.png', 30)
    save = locate('save_found.png')
    ag.click(save.x, save.y+50)
    locate_n_click('save_confirm.png')
    locate_n_click('exit.png', 6)
    locate_n_click('exit.png', 2)
    gold = locate('offline_gold.png')
    if not gold:
        discord.post(content=f'Error: couldnt find offline gold')
        return 0
    ag.click(gold.x, gold.y)
    locate_n_click('offline_gold_collect.png')
    locate_n_click('ad_accept_reward.png')

def cmg_loop():
    t_1 = threading.Thread(target=notifyInactivity, args=(60*2,), daemon=True)
    t_1.start()
    while True:
        timer = 0
        while timer<100:
            cmg()
            timer += 1
        time.sleep(60*1)

def king15():
    offer = None
    timer = 0
    timeout = 60
    while timer<timeout and offer is None:
        offer = ag.locateOnScreen('pic/seller_decline.png', region=REGION, confidence=CONFIDENCE)
        timer = round(timer+0.2, 1)
        time.sleep(0.2)
    if offer is not None:
        offer_center = ag.center(offer)
        accept = click_until([offer_center.x + offer.width, offer_center.y], 'ad_accept_reward.png')
        ag.click(accept.x, accept.y)
    reset_run(0,1)

def king15_loop():
    t_1 = threading.Thread(target=notifyInactivity, args=(60*5,), daemon=True)
    t_1.start()
    while True:
        king15()

def main(args):
    modeList = [k for k, v in vars(args).items() if v]
    if 'lvl' in modeList:
        level = vars(args)['lvl']

    if 's' in modeList:
        farm_summon()
    elif 'ad' in modeList:
        farm_ads()
    elif 'jr' in modeList:
        farm_jr()
    elif 'a' in modeList:
        achiev_loop()
    elif 'r' in modeList:
        reset_run(level)
    elif 'm' in modeList:
        t_1 = threading.Thread(target=notifyInactivity, daemon=True)
        t_1.start()
        while farm_mythic():
            pass
    elif 'p' in modeList:
        pekos_magic()
    elif 'cmg' in modeList:
        cmg_loop()
    elif 'k' in modeList:
        king15_loop()
    elif 'b' in modeList:
        t_1 = threading.Thread(target=notifyInactivity, daemon=True)
        t_1.start()
        while buy_all():
            time.sleep(2)
    else:
        print('wrong option, select -h for help')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automate repetetive tasks in game.')
    actionType = parser.add_mutually_exclusive_group(required=True)
    actionType.add_argument("-s", action="store_true", help="spend ords for summonings")
    actionType.add_argument("-ad", action="store_true", help="farm ads for stones")
    actionType.add_argument("-jr", action="store_true", help="farm jr")
    actionType.add_argument("-a", action="store_true", help="collect achievemens")
    actionType.add_argument("-r", action="store_true", help="reset normal run")
    actionType.add_argument("-m", action="store_true", help="fb glitch summon for mythic")
    actionType.add_argument("-p", action="store_true", help="pekos magic")
    actionType.add_argument("-b", action="store_true", help="buy all seller offers")
    actionType.add_argument("-cmg", action="store_true", help="cmg glitch")
    actionType.add_argument("-k", action="store_true", help="King 1-5")
    actionType = parser.add_mutually_exclusive_group(required=False)
    actionType.add_argument("-lvl", type=int, help="reset to level 0-King, 1-Chief, 2-JR", choices = [0,1,2])
    args = parser.parse_args()
    main(args)

#print(locate('fb_not_connected.png'))
#print(REGION)
#print(ag.size())
#todo:
#resolution doesnt matter! bluestacs size does matter! and bluestacs resolution
#how to make sure bluestacks open in the same resolution?
