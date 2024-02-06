import numpy as np
import cv2
import matplotlib.pyplot as plt

#img_captured = cv2.imread('test_con_pezzi.jpg')
img_captured_1 = cv2.imread('test.jpg')
gray1 = cv2.cvtColor(img_captured_1,cv2.COLOR_BGR2GRAY)
img_captured_2 = cv2.imread('test_v.jpg')
gray2 = cv2.cvtColor(img_captured_2,cv2.COLOR_BGR2GRAY)
#plt.imshow(img_captured)
#cv2.waitKey(0)

pattern = (7, 7)
ret1, corners1 = cv2.findChessboardCorners(gray1, pattern,
                                         flags=cv2.CALIB_CB_ADAPTIVE_THRESH +
                                               cv2.CALIB_CB_FAST_CHECK +
                                               cv2.CALIB_CB_NORMALIZE_IMAGE)

ret2, corners2 = cv2.findChessboardCorners(gray2, pattern,
                                         flags=cv2.CALIB_CB_ADAPTIVE_THRESH +
                                               cv2.CALIB_CB_FAST_CHECK +
                                               cv2.CALIB_CB_NORMALIZE_IMAGE)


H, _ = cv2.findHomography(corners1, corners2)
print(H)
img1_warp = cv2.warpPerspective(img_captured_1, H, (img_captured_1.shape[1]+400, img_captured_1.shape[0]+900))
#blur = cv2.GaussianBlur(img1_warp,(5,5),0)
#_, img_binary = cv2.threshold(blur,120,255,cv2.THRESH_BINARY)

gray_harrys = np.float32(img1_warp)
dst = cv2.cornerHarris(gray_harrys,2,3,0.04)
#result is dilated for marking the corners, not important
dst = cv2.dilate(dst,None)
img1_warp[dst>0.01*dst.max()]=[0,0,255]

cv2.imshow('dst',img1_warp)
cv2.waitKey(0)


