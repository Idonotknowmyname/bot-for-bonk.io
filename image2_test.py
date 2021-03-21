import numpy as np
# import argparse
import imutils
# import glob
import cv2
import time

template = cv2.imread('./Images/skin2.png')
template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
(tH, tW) = template.shape[:2]
# cv2.imshow("Template", template)
# cv2.waitKey(0)



image = cv2.imread('testV.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
found = None
foundMin = None
# loop over the scales of the image
gray = cv2.Canny(gray, 50, 200)
template = cv2.Canny(template, 50, 200)
t = time.time()
for scale in np.linspace(0.04, 0.1, 5)[::-1]:
    # resize the image according to the scale, and keep track
    # of the ratio of the resizing
    resized = imutils.resize(template, width = int(template.shape[1] * scale))
    r = template.shape[1] / float(resized.shape[1])


    # detect edges in the resized, grayscale image and apply template
    # matching to find the template in the image
    result = cv2.matchTemplate(gray, resized, cv2.TM_CCOEFF_NORMED)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
    # maxVal /= resized.shape[0]*resized.shape[1]
    # minVal /= resized.shape[0]*resized.shape[1]
    print(f'Scaling :{scale}, maxVal: {maxVal}')
    # check to see if the iteration should be visualized
    if True:
        # draw a bounding box around the detected region
        clone = np.dstack([gray, gray, gray])
        cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
            (maxLoc[0] + resized.shape[1], maxLoc[1] + resized.shape[0]), (0, 0, 255), 2)
        cv2.imshow("Visualize", clone)
        cv2.waitKey(0)
    # if we have found a new maximum correlation value, then update
    # the bookkeeping variable
    if found is None or maxVal > found[0]:
        print("MAX")
        found = (maxVal, maxLoc, r)
    if foundMin is None or minVal < foundMin[0]:
        print("MIN")
        foundMin = (minVal, minLoc, r)
# unpack the bookkeeping variable and compute the (x, y) coordinates
# of the bounding box based on the resized ratio
(_, maxLoc, r) = found
(startX, startY) = (int(maxLoc[0]), int(maxLoc[1]))
(endX, endY) = (int((maxLoc[0] + tW/ r) ), int((maxLoc[1] + tH/r) ))
# draw a bounding box around the detected result and display the image
cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
print(time.time()-t)
print(r)
cv2.imshow("Image", image)
cv2.waitKey(0)
