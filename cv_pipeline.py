from functools import lru_cache, wraps
import cv2 as cv
import imutils
import time
import numpy as np


TEMPLATE_MIN_SCALE = 0.04
TEMPLATE_MAX_SCALE = 0.09
TEMPLATE_N_TRIES = 8

TEMPLATE_MATCHING_SCORE_THRESHOLD = .6

TEMPLATE = cv.cvtColor(cv.imread('./Images/skin.png'), cv.COLOR_BGR2GRAY)
TH, TW = TEMPLATE.shape


def to_gray_scale(mat):
    gray = cv.cvtColor(mat, cv.COLOR_BGR2GRAY)

    return gray


def sphere_is_on_screen(gray):
    assert len(gray.shape) == 2, "Provided matrix should be a 2D grayscale (NxM matrix)"

    found = None
    found_min = None
    start_time = time.time()
    for scale in np.linspace(TEMPLATE_MIN_SCALE, TEMPLATE_MAX_SCALE, TEMPLATE_N_TRIES):
        resized = imutils.resize(TEMPLATE, width=int(TW * scale))

        mask = cv.matchTemplate(gray, resized, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(mask)

        if found is None or max_val > found[0]:
            found = (max_val, max_loc, scale, mask)

    max_score, max_loc, scale, mask = found

    if max_score > TEMPLATE_MATCHING_SCORE_THRESHOLD:
        # Template found on screen
        on_screen = True
        # Get rectangle coordinates
        x_start, y_start = int(max_loc[0]), int(max_loc[1])
        x_end, y_end = int(max_loc[0] + TW * scale), int(max_loc[1] + TH * scale)

        rectangle = (x_start, y_start, x_end, y_end)

        return on_screen, rectangle
    else:
        return False, None


def arrow_is_on_screen(gray):
    return False, None


def is_dead(mat):

    gray = gray_scale(mat)


def run_cv_pipeline(mat):
    gray = to_gray_scale(mat)

    on_screen, rect = sphere_is_on_screen(gray)

    if not on_screen:
        arrow_on_screen, rect = arrow_is_on_screen(gray)
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
