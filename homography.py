import numpy as np
import cv2
import matplotlib.pyplot as plt

#img_captured = cv2.imread('test_con_pezzi.jpg')
img_captured_1 = cv2.imread('test.jpg')
img_captured_2 = cv2.imread('test_v.jpg')
#plt.imshow(img_captured)
#cv2.waitKey(0)

pattern = (7, 7)
ret1, corners1 = cv2.findChessboardCorners(img_captured_1, pattern,
                                         flags=cv2.CALIB_CB_ADAPTIVE_THRESH +
                                               cv2.CALIB_CB_FAST_CHECK +
                                               cv2.CALIB_CB_NORMALIZE_IMAGE)

ret2, corners2 = cv2.findChessboardCorners(img_captured_2, pattern,
                                         flags=cv2.CALIB_CB_ADAPTIVE_THRESH +
                                               cv2.CALIB_CB_FAST_CHECK +
                                               cv2.CALIB_CB_NORMALIZE_IMAGE)


H, _ = cv2.findHomography(corners1, corners2)
print(H)
img1_warp = cv2.warpPerspective(img_captured_1, H, (img_captured_1.shape[1]+400, img_captured_1.shape[0]+900))
blur = cv2.GaussianBlur(img1_warp,(5,5),0)
_, img_binary = cv2.threshold(blur,120,255,cv2.THRESH_BINARY)
cv2.imwrite("img1_warp.jpg", img1_warp) 
cv2.imshow("img1_warp", img_binary)
cv2.waitKey(0)


pattern = (8, 8)

for i in range(3,10):
    for j in range(3,10):
        pattern = (i, j)
        ret3, corners3 = cv2.findChessboardCorners(img_binary, pattern,
                                         flags=cv2.CALIB_CB_ADAPTIVE_THRESH +
                                               cv2.CALIB_CB_FAST_CHECK +
                                               cv2.CALIB_CB_NORMALIZE_IMAGE)
        if ret3:
            #print(corners3)
            print(i)
            print()
            print(j)
            fnl = cv2.drawChessboardCorners(img_binary, pattern, corners3, ret3)
            cv2.imshow("fnl", fnl)
            cv2.waitKey(0)
        else:
            print("No Checkerboard Found")


