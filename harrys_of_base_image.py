import numpy as np
import cv2
import matplotlib.pyplot as plt

#img_captured = cv2.imread('test_con_pezzi.jpg')
img_captured_1 = cv2.imread('test.jpg')
gray1 = cv2.cvtColor(img_captured_1,cv2.COLOR_BGR2GRAY)

#blur = cv2.GaussianBlur(img1_warp,(5,5),0)
#_, img_binary = cv2.threshold(blur,120,255,cv2.THRESH_BINARY)

gray_harrys = np.float32(gray1)
dst = cv2.cornerHarris(gray_harrys,2,3,0.2)
#result is dilated for marking the corners, not important

dst = cv2.dilate(dst,None)
# Threshold for an optimal value, it may vary depending on the image.

#gray1[dst>0.01*dst.max()]=[0,0,255]
out = cv2.cornerEigenValsAndVecs(dst,2,3)

cv2.imwrite("img1_base__warp_after_harris.jpg", out) 
#cv2.waitKey(0)


