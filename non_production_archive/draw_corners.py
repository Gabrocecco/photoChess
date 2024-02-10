import numpy as np
import cv2
import matplotlib.pyplot as plt

#img_captured = cv2.imread('test_con_pezzi.jpg')
img_captured = cv2.imread('test_v.jpg')
#plt.imshow(img_captured)
#cv2.waitKey(0)

pattern = (7, 7)
ret, corners = cv2.findChessboardCorners(img_captured, pattern,
                                         flags=cv2.CALIB_CB_ADAPTIVE_THRESH +
                                               cv2.CALIB_CB_FAST_CHECK +
                                               cv2.CALIB_CB_NORMALIZE_IMAGE)

#ret, corners = cv2.findChessboardCornersSB(img_captured, pattern, flags=cv2.CALIB_CB_EXHAUSTIVE)
if ret:
    print(corners)
    fnl = cv2.drawChessboardCorners(img_captured, pattern, corners, ret)
    cv2.imshow("fnl", fnl)
    cv2.waitKey(0)
else:
    print("No Checkerboard Found")