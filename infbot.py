from ImageClient import ImageClient
import cv2 as cv
import asyncio
import pydirectinput

image_filenames = ['next', 'replay', 'roblox', 'yes']
image_lib = {}

for fn in image_filenames:
    image_lib[fn] = cv.imread(f'img/{fn}.png', cv.IMREAD_GRAYSCALE)

bot1 = ImageClient((1472, 605), image_lib)


async def inf_play_loop(screen):
    for img in image_lib:
        if img != 'roblox':
            # print("looking for " + img)
            search = bot1.look_for_image(image_lib[img], screen)
            # print(search)
            if search:
                print(f"found {img} @ ({search[0]}). attempting to click at absolute pos ({search[0][0] + bot1.window_position[0], search[0][1] + bot1.window_position[1]})")
                # print(f"window pos {bot1.window_position}")
                pydirectinput.moveTo(search[0][0] + bot1.window_position[0], search[0][1] + bot1.window_position[1])
                pydirectinput.move(5, 5)
                pydirectinput.move(-5, -5)
                pydirectinput.mouseDown()
                pydirectinput.mouseUp()

    await asyncio.sleep(.2)


async def detect_reconnect_loop(screen):
    print("searching for rc")
    await asyncio.sleep(1)


async def main():
    while True:
        screen = bot1.grab_screen((bot1.window_position[0], bot1.window_position[1], bot1.window_position[0] +
                                   bot1.window_size[0], bot1.window_position[1] + bot1.window_size[1]))
        await asyncio.gather(inf_play_loop(screen), detect_reconnect_loop(screen))


asyncio.run(main())
