# import asyncio
import cv2 as cv
import numpy as np
from PIL.ImageGrab import grab


class ImageClient:
    def __init__(self, screen_size: tuple[int, int], image_library: dict):
        #  todo : add bounding zone for all image checks to support multiple separate clients
        self.window_size = screen_size
        self.image_library = image_library
        self.window_position = self.look_for_window()

    def look_for_image(self, img: cv.Mat, screen: cv.Mat = None) -> list[tuple[int, int]] | bool:
        # yes_matches = match_screen(yes_button_image, screen, 0.7)
        if screen is None:
            screen = self.grab_screen((self.window_position[0], self.window_position[1], self.window_position[0] +
                                       self.window_size[0], self.window_position[1] + self.window_size[1]))
        res = cv.matchTemplate(img, screen, cv.TM_CCOEFF_NORMED)
        matches = np.where(res >= 0.7)
        matches_pos_list = []
        # print(matches[0])
        if matches[0].any():
            for pt in zip(*matches[::-1]):
                matches_pos_list.append(pt)
            return matches_pos_list
        else:
            return False

    def look_for_window(self) -> tuple[int, int] | bool:
        screen_grayscale = self.grab_screen()
        matches_rbx_img = self.look_for_image(self.image_library['roblox'], screen_grayscale)
        if matches_rbx_img:
            return matches_rbx_img[0]
        return False

    def grab_screen(self, bbox: tuple = ()):
        screen_array = np.array(grab(bbox))[:, :, ::-1].copy()
        screen_gray = cv.cvtColor(screen_array, cv.COLOR_BGR2GRAY)
        return cv.adaptiveThreshold(screen_gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
