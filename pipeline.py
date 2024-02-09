from ultralytics import YOLO
from PIL import Image
from IPython.display import display
import os
import cv2
import matplotlib.pyplot as plt
import numpy as np

# order points in this way:
    # 0: top-left,
    # 1: top-right
    # 2: bottom-right,
    # 3: bottom-left
def order_points(pts):
    rect = np.zeros((4, 2), dtype = "float32")
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
        
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect

# Orginal phote taken by the app
#starting_image_link = "dataset\\train\images\\04aed88a8d23cf27e47806eb23948495_jpg.rf.b2b9c08d458461669627c4976b744f46.jpg"
starting_image_link = "test_images\\test_images_real\IMG-20240208-WA0003.jpg"

#detect pieces with otiginal yolo model 
model_pieces = YOLO("training_output\content\\runs\detect\\train2_200_epocs\weights\\best.pt")
results = model_pieces.predict(starting_image_link, save=True, show=False, project="yolo_output_final_warped", name="on_original_perspective", exist_ok=True)

#chessboard corner detection 
model_corner = YOLO("best_corners_repo.pt")
results = model_corner.predict(starting_image_link, conf=0.001, iou=0.1, imgsz=640, max_det=4, save=False)
boxes = results[0].boxes
arr = boxes.xywh.numpy()
points = arr[:,0:2]
print("POINTS: \n"+ str(points)+"\n\n")
corners = order_points(points)
print("CORNERS: \n"+ str(corners)+"\n\n")
img_show = plt.imread(starting_image_link)
#plt.imshow(img_show)


# plotting the corners in original image 
# colors = ["red", "yellow", "blue", "purple"]
# index = 0
# for corner in corners:
#     plt.scatter(corner[0], corner[1], color=colors[index])
#     index = index + 1
# plt.show()


# results_master = model_corner.predict("test_images\\test_images_real\master_chessbord.jpg", conf=0.001, iou=0.1, imgsz=640, max_det=4, save=True)
# img_link = starting_image_link
# img = Image.open(img_link)
# image = np.asarray(img)
# dst_master = np.array([
#  [     114.75  ,     104.9],
#  [     1931.7   ,   108.47],
#  [     1926.4   ,   1890.1],
#  [     111.55   ,   1873.8]], dtype = "float32")
# M = cv2.getPerspectiveTransform(corners, dst_master)

# print(M)
#warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

tl = corners[0]
tr = corners[1]
br = corners[2]
bl = corners[3]

# compute the width of the new image
widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
maxWidth = max(int(widthA), int(widthB))
   

# compute the height of the new image
heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
maxHeight = max(int(heightA), int(heightB))

# construct set of destination points to obtain a "birds eye view"
dst = np.array([
    [0, 0],
    [maxWidth - 1, 0],
    [maxWidth - 1, maxHeight - 1],
    [0, maxHeight - 1]], dtype = "float32")

M = cv2.getPerspectiveTransform(corners, dst)
print("TRANSFORM MATRIX: \n"+str(M)+"\n\n")
img = Image.open(starting_image_link)
image = np.asarray(img)
warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
img = Image.fromarray(warped, "RGB")
img.save("p_test.jpg")
# img.show()


conf_par = 0.1
results = model_pieces.predict("p_test.jpg", save=True, show=False, project="yolo_output_final_warped",name="on_warped_perspective", exist_ok=True)


