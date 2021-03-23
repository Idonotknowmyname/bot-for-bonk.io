from functools import lru_cache, wraps
import cv2 as cv
import imutils
import time
import numpy as np

class cvPipeline():
    def __init__(self):
        self.template_min_scale = 0.04
        self.template_max_scale =  0.09
        self.templates_n_tries = 8

        self.template_matching_score_threshold = .6
        self.break_seach_score_threshold = .7

        self.template = cv.cvtColor(cv.imread('./Images/skin_new.png'), cv.COLOR_BGR2GRAY)
        self.TH, self.TW = self.template.shape
        self.sphere_search_scales = np.linspace(self.template_min_scale, self.template_max_scale, self.templates_n_tries)

    def to_gray_scale(self,mat):
        gray = cv.cvtColor(mat, cv.COLOR_BGR2GRAY)

        return gray


    def sphere_is_on_screen(self,gray):
        assert len(gray.shape) == 2, "Provided matrix should be a 2D grayscale (NxM matrix)"

        found = None
        found_min = None
        start_time = time.time()
        order = {k:0 for k in self.sphere_search_scales}
        for scale in self.sphere_search_scales:
            resized = imutils.resize(self.template, width=int(self.TW * scale))

            mask = cv.matchTemplate(gray, resized, cv.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv.minMaxLoc(mask)
            order[scale] = max_val
            if found is None or max_val > found[0]:
                found = (max_val, max_loc, scale, mask)
            if max_val >=self.break_seach_score_threshold:
                break
        
        max_score, max_loc, scale, mask = found
        self.sphere_search_scales = [k for k, v in sorted(order.items(), key=lambda item: -item[1])]
        print([f'scale: {k} score; {v}' for k, v in sorted(order.items(), key=lambda item: -item[1])][0])
        if max_score > self.template_matching_score_threshold:
            # Template found on screen
            on_screen = True
            # Get rectangle coordinates
            x_start, y_start = int(max_loc[0]), int(max_loc[1])
            x_end, y_end = int(max_loc[0] + self.TW * scale), int(max_loc[1] + self.TH * scale)

            rectangle = (x_start, y_start, x_end, y_end)

            return on_screen, rectangle
        else:
            return False, None


    def arrow_is_on_screen(self,gray):
        return False, None


    def is_dead(self,mat):

        gray = gray_scale(mat)


    def run(self,mat):
        gray = self.to_gray_scale(mat)

        on_screen, rect = self.sphere_is_on_screen(gray)

        if not on_screen:
            arrow_on_screen, rect = self.arrow_is_on_screen(gray)
        else:
            arrow_on_screen, rect = False, rect

        if not on_screen and not arrow_on_screen:
            is_dead = True
        else:
            is_dead = False

        pos_rect_mask = np.zeros_like(gray, np.uint8)
        if rect is not None:
            cv.rectangle(pos_rect_mask, rect[:2], rect[2:], 255, 2)

        # if on_screen:
        #     print(f"I am on screen!!!! rect is: {rect}")
        # else:
        #     print("I am dead!!!")

        return {"states": {
            "is_dead": is_dead
        },
            "masks": {
                "position_rect": pos_rect_mask
        },
            "info": {}
        }
