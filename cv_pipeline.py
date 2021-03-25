from functools import lru_cache, wraps
import cv2 as cv
import imutils
import time
import numpy as np

class cvPipeline():
    def __init__(self):
        self.debug = True#plot for debugging, must be false when running
        #self finding HYPERPARAMS
        self.template_min_scale = 0.04
        self.template_max_scale =  0.1
        self.templates_n_tries = 8
        self.template_matching_score_threshold = .6
        self.break_seach_score_threshold = .7
        self.template = cv.cvtColor(cv.imread('./Images/skin_new.png'), cv.COLOR_BGR2GRAY)
        self.TH, self.TW = self.template.shape
        self.sphere_search_scales = np.linspace(self.template_min_scale, self.template_max_scale, self.templates_n_tries)

        #arrow finding HYPERPARAMS
        self.lines_width = 40#top and vertical line width (should be same as width of arrow)
        self.lines_cut_corners = 40# how much close to the corner should you ignore (because you will deal with corners by themselves)
        self.corners = 55#how big are the corners? a cornersXcorners square, should be bigger than lines_width
        self.arrow_min_scale = 0.9
        self.arrow_max_scale = 1.5
        self.arrow_n_tries = 3
        self.arrow_corner_rotations = 6   
        self.ARROW_template_matching_score_threshold = .7
        self.arrowCannyLowT, self.arrowCannyHighT = 5,10
        self.arrow_template =  cv.Canny(cv.cvtColor(cv.imread('./Images/arrow.png'),cv.COLOR_BGR2GRAY),self.arrowCannyLowT, self.arrowCannyHighT)
        self.arrow_TH, self.arrow_TW = self.arrow_template.shape[:2]
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
            if self.debug:
                    print(f'Scaling :{scale}, maxVal: {max_val}')
                    # draw a bounding box around the detected region
                    clone = np.dstack([gray, gray, gray])
                    cv.rectangle(clone, (max_loc[0], max_loc[1]),
                        (max_loc[0] + resized.shape[1], max_loc[1] + resized.shape[0]), (0, 0, 255), 2)
                    cv.imshow("Visualize", clone)
                    cv.imshow('vis',resized)
                    cv.waitKey(0)
            if found is None or max_val > found[0]:
                found = (max_val, max_loc, scale, mask)
            if max_val >=self.break_seach_score_threshold:
                break
        
        max_score, max_loc, scale, mask = found
        self.sphere_search_scales = [k for k, v in sorted(order.items(), key=lambda item: -item[1])]
        # print([f'scale: {k} score; {v}' for k, v in sorted(order.items(), key=lambda item: -item[1])][0])
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
        og_W = gray.shape[1]
        of_H = gray.shape[0]
        #get pieces
        top_row = cv.Canny(gray[:self.lines_width,self.lines_cut_corners:-self.lines_cut_corners],self.arrowCannyLowT, self.arrowCannyHighT)#keep 30 pixels from top border, discard 40 pizels from right and from left border
        right_row= cv.Canny(gray[self.lines_cut_corners:,-self.lines_width:],self.arrowCannyLowT, self.arrowCannyHighT)#discard 40 pixels from top border,keep 30 pixels from the right border
        left_row = cv.Canny(gray[self.lines_cut_corners:,:self.lines_width],self.arrowCannyLowT, self.arrowCannyHighT) #discard 40 pixels from top border,keep 30 pixels from the left border
        top_right_corner=cv.Canny(gray[:self.corners,-self.corners:],self.arrowCannyLowT, self.arrowCannyHighT)
        top_left_corner = cv.Canny(gray[:self.corners,:self.corners],self.arrowCannyLowT, self.arrowCannyHighT)

        #find near edges
        found = None
        targets = {0:top_row,-90:right_row,90:left_row}#mapt the rotation for the arrow with the correct art of image
        for rotation in [0,90,-90]:
            arrow_template = imutils.rotate(self.arrow_template,rotation)
            for scale in np.linspace(self.arrow_min_scale, self.arrow_max_scale,self.arrow_n_tries)[::-1]:
                resized = imutils.resize(arrow_template, width = int(self.arrow_template.shape[1] * scale))

                # matching to find the template in the image
                result = cv.matchTemplate(targets[rotation], resized, cv.TM_CCOEFF_NORMED)
                (minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(result)
                if self.debug:
                    print(f'Scaling :{scale},ROTATION: {rotation}, maxVal: {maxVal}')
                    # draw a bounding box around the detected region
                    clone = np.dstack([targets[rotation], targets[rotation], targets[rotation]])
                    cv.rectangle(clone, (maxLoc[0], maxLoc[1]),
                        (maxLoc[0] + resized.shape[1], maxLoc[1] + resized.shape[0]), (0, 0, 255), 2)
                    cv.imshow("Visualize", clone)
                    cv.imshow('vis',resized)
                    cv.waitKey(0)
                if found is None or maxVal > found[0]:
                    found = (maxVal, maxLoc, scale, rotation)
                #TODO BREAK HERE LOOP IF OVER THRESHOLD

        #find in corners
        for rotation in np.linspace(-90,90,self.arrow_corner_rotations*2 ):
            arrow_template = imutils.rotate(self.arrow_template,rotation)
            if rotation<0:
                target = top_right_corner
                corner_type = -1
            else:
                corner_type = 1
                target = top_left_corner
            for scale in np.linspace(self.arrow_min_scale, self.arrow_max_scale,self.arrow_n_tries)[::-1]:
                resized = imutils.resize(arrow_template, width = int(arrow_template.shape[1] * scale))
                result = cv.matchTemplate(target, resized, cv.TM_CCOEFF_NORMED)
                (minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(result)
                if self.debug:
                    print(f'Scaling :{scale},ROTATION: {rotation}, maxVal: {maxVal}')
                    # draw a bounding box around the detected region
                    clone = np.dstack([target, target, target])
                    cv.rectangle(clone, (maxLoc[0], maxLoc[1]),
                        (maxLoc[0] + resized.shape[1], maxLoc[1] + resized.shape[0]), (0, 0, 255), 2)
                    cv.imshow("Visualize", clone)
                    cv.imshow('vis',resized)
                    cv.waitKey(0)
                if found is None or maxVal > found[0]:
                    found = (maxVal, maxLoc, scale,corner_type)
        (maxScore, max_loc, scale,found_where) = found
        adjust_map = {0:(self.lines_cut_corners,0),-90:(0,self.lines_cut_corners),90:(self.arrow_TW-self.lines_width,self.lines_cut_corners),-1:(self.arrow_TW-self.corners,0),1:(0,0)}
        adjust_x, adjust_y = adjust_map[found_where]
        if maxScore > self.ARROW_template_matching_score_threshold:
            arrow_on_screen = True
            x_start, y_start = int(max_loc[0]+adjust_x), int(max_loc[1]+adjust_y)
            x_end, y_end = int(max_loc[0]+adjust_x + self.arrow_TW * scale), int(max_loc[1] +adjust_y+ self.arrow_TH * scale)
            rectangle = (x_start, y_start, x_end, y_end)
            return arrow_on_screen, rectangle
        else:
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

if __name__=='__main__':
    c = cvPipeline()
    gray = cv.imread('./Images/test5.png',0)
    # cv.imshow('t',gray)
    # cv.waitKey()
    cv.imshow('t',cv.Canny(gray,5,10))
    cv.waitKey()
    c.arrow_is_on_screen(gray)
    # c.sphere_is_on_screen(gray)
