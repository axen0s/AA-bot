from ImageClient import ImageClient
import cv2 as cv
import asyncio
import pydirectinput
import numpy as np
import datetime

image_filenames = ['next', 'replay', 'roblox', 'yes']
image_lib = {}

for fn in image_filenames:
    image_lib[fn] = cv.imread(f'img/{fn}.png', cv.IMREAD_GRAYSCALE)

bot1 = ImageClient((1472, 605), image_lib)


def failsafe_click_attempt(x=None, y=None):  # moves mouse to xy, clicks, moves mouse a little then back, clicks again
    if x and y:
        pydirectinput.moveTo(x, y)
    pydirectinput.mouseDown()
    pydirectinput.mouseUp()
    pydirectinput.move(5, 5)
    pydirectinput.move(-5, -5)
    pydirectinput.mouseDown()
    pydirectinput.mouseUp()


orwin = cv.imread('img/orwin.png', cv.IMREAD_GRAYSCALE)
upgrade = cv.imread('img/upgrade.png', cv.IMREAD_GRAYSCALE)
orwins_placed = 0
green_boundary = ([20, 190, 60], [70, 215, 110])
lower_green = np.array(green_boundary[0], dtype="uint8")
upper_green = np.array(green_boundary[1], dtype="uint8")


def orwin_attempt_place(screen, screen_array, orwin_state) -> str:
    if orwins_placed < 6:  # if max orwins arent placed yet, attempt to place and upgrade another
        print(orwin_state)
        if orwin_state == "upgrading":
            upgrade_search = bot1.look_for_image(upgrade, screen)
            if upgrade_search:
                if orwin_state != "upgrading":
                    print("beginning to upgrade")
                failsafe_click_attempt(upgrade_search[0][0] + bot1.window_position[0], upgrade_search[0][1] + bot1.window_position[1])
                return "upgrading"
        elif orwin_state == "placing":  # look for a green area to place orwin
            # print()
            green_mask = cv.inRange(screen_array, lower_green, upper_green)
            # cv.imshow("masktest", green_mask)
            # cv.waitKey(0)
            upgrade_search = bot1.look_for_image(upgrade, screen)
            if upgrade_search:
                if orwin_state != "upgrading":
                    print("beginning to upgrade")
                failsafe_click_attempt(upgrade_search[0][0] + bot1.window_position[0], upgrade_search[0][1] + bot1.window_position[1])
                return "upgrading"
            mousex, mousey = pydirectinput.position()
            relpos_left = (bot1.window_position[0] - mousex) *-1
            relpos_right = bot1.window_position[0] + bot1.window_size[0] - mousex
            relpos_up = mousey - bot1.window_position[1]
            relpos_down = -1 * (mousey - bot1.window_position[1] - bot1.window_size[1])
            print(f"up {relpos_up} left {relpos_left} down {relpos_down} right {relpos_right}")
            wheretomove = (-10, 10)
            if relpos_right < 150:
                wheretomove = (bot1.window_size[0]*-.8, 10)
            elif relpos_left < 150:
                wheretomove = (bot1.window_size[0]*.8, 10)
            if relpos_up < 50:
                wheretomove = (wheretomove[0], (bot1.window_size[1]*.83))
            elif relpos_down < 50:
                wheretomove = (wheretomove[0], bot1.window_size[1]*-.83)
            pydirectinput.move(round(wheretomove[0]), round(wheretomove[1]))
            failsafe_click_attempt()
            return "placing"
        else:
            orwin_search = bot1.look_for_image(orwin, screen)
            if orwin_search:
                print(f"attempting to place orwin at {orwin_search[0]}")
                failsafe_click_attempt(orwin_search[0][0] + bot1.window_position[0], orwin_search[0][1] + bot1.window_position[1])
                return "placing"
            return "none"


def inf_attempt_continue(screen) -> str | None:
    for img in image_lib:
        if img != 'roblox':
            # print("looking for " + img)
            search = bot1.look_for_image(image_lib[img], screen)
            # print(search)
            if search:
                print(
                    f"found {img} @ ({search[0]}). attempting to click at absolute pos ({search[0][0] + bot1.window_position[0], search[0][1] + bot1.window_position[1]})")
                # print(f"window pos {bot1.window_position}")
                failsafe_click_attempt(search[0][0] + bot1.window_position[0], search[0][1] + bot1.window_position[1])
                return img
    return None


async def inf_play_loop(grey_screen, screen_array, inf_state, orwin_state):
    attempt_state_update = inf_attempt_continue(grey_screen)
    if attempt_state_update:
        print(f"updating infinite state: {attempt_state_update}")
        if inf_state != attempt_state_update and attempt_state_update == 'yes':  # detect change in inf state. if change to 'yes', reset orwin state
            orwin_state = 'none'
            await asyncio.sleep(10)  # wait 10 seconds after hitting 'yes' for the first time
        inf_state = attempt_state_update
    if inf_state == 'yes':  # we are within the wave state of infinite
        _orwin_state = orwin_attempt_place(grey_screen, screen_array, orwin_state)
        orwin_state = _orwin_state
        if orwin_state == 'placing':
            await asyncio.sleep(.25)
    if inf_state == 'replay' or inf_state == 'next':
        failsafe_click_attempt()  # dont have img recognition for xp drops yet lol..
    if inf_state == 'replay':
        await asyncio.sleep(10)  # wait 10 seconds after hitting replay
    return inf_state, orwin_state


async def detect_reconnect_loop(screen):  # todo : find reconnect & walk to inf + restart
    # print("searching for rc")
    await asyncio.sleep(0.1)


async def summon_loop(screen):
    await asyncio.sleep(0)


async def main():  # todo : implement summon checker/summoner
    inf_state = 'none'
    orwin_state = 'none'
    current_inf_starttime = None
    inf_results = []
    while True:
        screen, screen_array = bot1.grab_screen((bot1.window_position[0], bot1.window_position[1], bot1.window_position[0] +
                                   bot1.window_size[0], bot1.window_position[1] + bot1.window_size[1]))
        results = await asyncio.gather(inf_play_loop(screen, screen_array, inf_state, orwin_state), detect_reconnect_loop(screen), summon_loop(screen))
        inf_state = results[0][0]
        if inf_state == 'yes' and not current_inf_starttime:
            current_inf_starttime = datetime.datetime.now()
        if (inf_state == 'replay' or inf_state == 'next') and current_inf_starttime:
            inf_results.append((datetime.datetime.now()-current_inf_starttime).total_seconds())
            current_inf_starttime = None
            print(inf_results)
        orwin_state = results[0][1]


asyncio.run(main())
