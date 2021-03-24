import numpy as np
# import argparse
import imutils
# import glob
import cv2
import time

template = cv2.imread('./Images/arrow.png')
template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
(tH, tW) = template.shape[:2]
# cv2.imshow("Template", template)
# cv2.waitKey(0)



image = cv2.imread('./Images/testArrow_3.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
lines_width = 30
lines_cut_corners = 40
corners = 55
og_W = gray.shape[1]
of_H = gray.shape[0]
top_row = gray[:lines_width,lines_cut_corners:-lines_cut_corners]#keep 30 pixels from top border, discard 40 pizels from right and from left border
# cv2.imshow("t", top_row)
# cv2.waitKey(0)
right_row= gray[lines_cut_corners:,-lines_width:]#discard 40 pixels from top border,keep 30 pixels from the right border
# cv2.imshow("t", right_row)
# cv2.waitKey(0)
left_row = gray[lines_cut_corners:,:lines_width] #discard 40 pixels from top border,keep 30 pixels from the left border
# cv2.imshow("t", left_row)
# cv2.waitKey(0)
top_right_corner=gray[:corners,-corners:]
# cv2.imshow("t", top_right_corner)
# cv2.waitKey(0)
top_left_corner = gray[:corners,:corners]
# cv2.imshow("t", top_left_corner)
# cv2.waitKey(0)

# t = time.time()
#look for top arrows
def find_top(top_row,template):
    found = None
    for scale in np.linspace(0.8, 1,2)[::-1]:
        # resize the image according to the scale, and keep track
        # of the ratio of the resizing
        resized = imutils.resize(template, width = int(template.shape[1] * scale))
        r = template.shape[1] / float(resized.shape[1])

        # matching to find the template in the image
        result = cv2.matchTemplate(top_row, resized, cv2.TM_CCOEFF_NORMED)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
        if True:
            print(f'Scaling :{scale}, maxVal: {maxVal}')
            # draw a bounding box around the detected region
            clone = np.dstack([top_row, top_row, top_row])
            cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                (maxLoc[0] + resized.shape[1], maxLoc[1] + resized.shape[0]), (0, 0, 255), 2)
            cv2.imshow("Visualize", clone)
            cv2.waitKey(0)
        # if we have found a new maximum correlation value, then update
        # the bookkeeping variable
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)
    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (maxScore, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0]+lines_cut_corners), int(maxLoc[1]))
    (endX, endY) = (int((maxLoc[0]+lines_cut_corners + tW/ r) ), int((maxLoc[1]+ tH/r) ))
    # draw a bounding box around the detected result and display the image
    cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
    print("R "+str(r))
    print("MAX "+str(maxScore))
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    return maxScore, (startX,endX),(startY,endY)



def find_vertical_right(right,template):
    #right
    found = None
    right_template = imutils.rotate(template,90)
    #right
    for scale in np.linspace(0.8, 1,2)[::-1]:
        # resize the image according to the scale, and keep track
        # of the ratio of the resizing
        resized = imutils.resize(right_template, width = int(right_template.shape[1] * scale))
        r = right_template.shape[1] / float(resized.shape[1])

        # matching to find the right_template in the image
        result = cv2.matchTemplate(right, resized, cv2.TM_CCOEFF_NORMED)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
        if True:
            print(f'Scaling :{scale}, maxVal: {maxVal}')
            # draw a bounding box around the detected region
            clone = np.dstack([right, right, right])
            cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                (maxLoc[0] + resized.shape[1], maxLoc[1] + resized.shape[0]), (0, 0, 255), 2)
            cv2.imshow("Visualize", clone)
            cv2.waitKey(0)
        # if we have found a new maximum correlation value, then update
        # the bookkeeping variable
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)
    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (maxScore, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0]+og_W-lines_width), int(maxLoc[1]+lines_cut_corners))
    (endX, endY) = (int((maxLoc[0]+og_W-lines_width + tW/ r) ), int((maxLoc[1]+lines_cut_corners+ tH/r) ))
    # draw a bounding box around the detected result and display the image
    cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
    print("R "+str(r))
    print("MAX "+str(maxScore))
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    return maxScore, (startX,endX),(startY,endY)

def find_vertical_left(left,template):
    #left
    found = None
    left_template = imutils.rotate(template,-90)
    #left
    for scale in np.linspace(0.8, 1,2)[::-1]:
        # resize the image according to the scale, and keep track
        # of the ratio of the resizing
        resized = imutils.resize(left_template, width = int(left_template.shape[1] * scale))
        r = left_template.shape[1] / float(resized.shape[1])

        # matching to find the left_template in the image
        result = cv2.matchTemplate(left, resized, cv2.TM_CCOEFF_NORMED)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
        if True:
            print(f'Scaling :{scale}, maxVal: {maxVal}')
            # draw a bounding box around the detected region
            clone = np.dstack([left, left, left])
            cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                (maxLoc[0] + resized.shape[1], maxLoc[1] + resized.shape[0]), (0, 0, 255), 2)
            cv2.imshow("Visualize", clone)
            cv2.waitKey(0)
        # if we have found a new maximum correlation value, then update
        # the bookkeeping variable
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)
    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (maxScore, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0]), int(maxLoc[1]+lines_cut_corners))
    (endX, endY) = (int((maxLoc[0] + tW/ r) ), int((maxLoc[1]+lines_cut_corners+ tH/r) ))
    # draw a bounding box around the detected result and display the image
    cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
    print("R "+str(r))
    print("MAX "+str(maxScore))
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    return maxScore, (startX,endX),(startY,endY)

def find_corner_right(top_right_corner,template):
    found = None
    for scale in np.linspace(1, 1,1)[::-1]:
        for rotation in np.linspace(0,-90,5 ):
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(template, width = int(template.shape[1] * scale))
            r = template.shape[1] / float(resized.shape[1])

            resized = imutils.rotate(resized,rotation)
            cv2.imshow('t',resized)
            cv2.waitKey()
            # matching to find the template in the image
            result = cv2.matchTemplate(top_right_corner, resized, cv2.TM_CCOEFF_NORMED)
            (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
            if True:
                print(f'Scaling :{scale},ROTATION: {rotation}, maxVal: {maxVal}')
                # draw a bounding box around the detected region
                clone = np.dstack([top_right_corner, top_right_corner, top_right_corner])
                cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                    (maxLoc[0] + resized.shape[1], maxLoc[1] + resized.shape[0]), (0, 0, 255), 2)
                cv2.imshow("Visualize", clone)
                cv2.waitKey(0)
            # if we have found a new maximum correlation value, then update
            # the bookkeeping variable
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)
    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (maxScore, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0]+(og_W-corners)), int(maxLoc[1]))
    (endX, endY) = (int((maxLoc[0]+(og_W-corners) + tW/ r) ), int((maxLoc[1]+ tH/r) ))
    # draw a bounding box around the detected result and display the image
    cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
    print("R "+str(r))
    print("MAX "+str(maxScore))
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    return maxScore, (startX,endX),(startY,endY)

def find_corner_left(top_left_corner,template):
    found = None
    for scale in np.linspace(1, 1,1)[::-1]:
        for rotation in np.linspace(0,90,5 ):
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(template, width = int(template.shape[1] * scale))
            r = template.shape[1] / float(resized.shape[1])

            resized = imutils.rotate(resized,rotation)
            cv2.imshow('t',resized)
            cv2.waitKey()
            # matching to find the template in the image
            result = cv2.matchTemplate(top_left_corner, resized, cv2.TM_CCOEFF_NORMED)
            (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
            if True:
                print(f'Scaling :{scale},ROTATION: {rotation}, maxVal: {maxVal}')
                # draw a bounding box around the detected region
                clone = np.dstack([top_left_corner, top_left_corner, top_left_corner])
                cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                    (maxLoc[0] + resized.shape[1], maxLoc[1] + resized.shape[0]), (0, 0, 255), 2)
                cv2.imshow("Visualize", clone)
                cv2.waitKey(0)
            # if we have found a new maximum correlation value, then update
            # the bookkeeping variable
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)
    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (maxScore, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0]), int(maxLoc[1]))
    (endX, endY) = (int((maxLoc[0] + tW/ r) ), int((maxLoc[1]+ tH/r) ))
    # draw a bounding box around the detected result and display the image
    cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
    print("R "+str(r))
    print("MAX "+str(maxScore))
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    return maxScore, (startX,endX),(startY,endY)
find_top(top_row,template)
find_vertical_right(right_row,template)
find_vertical_left(left_row,template)
find_corner_right(top_right_corner,template)
find_corner_left(top_left_corner,template)

# print("TIME: "+str(time.time()-t))
