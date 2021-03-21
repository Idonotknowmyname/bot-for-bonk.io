# must import if working with opencv in python
import numpy as np
import cv2

# removes pixels in image that are between the range of
# [lower_val,upper_val]
def remove_gray(img,lower_val,upper_val):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([0,0,lower_val])
    upper_bound = np.array([255,255,upper_val])
    mask = cv2.inRange(gray, lower_bound, upper_bound)
    return cv2.bitwise_and(gray, gray, mask = mask)

