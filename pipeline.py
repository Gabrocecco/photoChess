from ultralytics import YOLO
from PIL import Image
from IPython.display import display
import os
import cv2
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
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


def plot_grid_on_transformed_image(image):
    
    corners = np.array([[0,0], 
                    [image.size[0], 0], 
                    [0, image.size[1]], 
                    [image.size[0], image.size[1]]])
    
    corners = order_points(corners)

    figure(figsize=(10, 10), dpi=80)

    # im = plt.imread(image)
    implot = plt.imshow(image)
    
    TL = corners[0]
    BL = corners[3]
    TR = corners[1]
    BR = corners[2]

    def interpolate(xy0, xy1):
        x0,y0 = xy0
        x1,y1 = xy1
        dx = (x1-x0) / 8
        dy = (y1-y0) / 8
        pts = [(x0+i*dx,y0+i*dy) for i in range(9)]
        return pts

    ptsT = interpolate( TL, TR )
    ptsL = interpolate( TL, BL )
    ptsR = interpolate( TR, BR )
    ptsB = interpolate( BL, BR )
        
    for a,b in zip(ptsL, ptsR):
        plt.plot( [a[0], b[0]], [a[1], b[1]], 'ro', linestyle="--" )
    for a,b in zip(ptsT, ptsB):
        plt.plot( [a[0], b[0]], [a[1], b[1]], 'ro', linestyle="--" )
        
    plt.axis('off')

    plt.savefig('chessboard_transformed_with_grid.jpg')
    return ptsT, ptsL


# connects detected piece to the right square

def connect_square_to_detection(points, ptsT, ptsL):
    
    # di = {0: 'b', 1: 'k', 2: 'n',
    #   3: 'p', 4: 'q', 5: 'r', 
    #   6: 'B', 7: 'K', 8: 'N',
    #   9: 'P', 10: 'Q', 11: 'R'}
    
    # print("ciao")
    # print(ptsT)
    # print("\n")
    # print(ptsL)
    square_list_centers = []
    for t in range(1,len(ptsT)):
        for l in range(1,len(ptsL)):
            # # x =  ptsT[t][0] - ptsT[t-1][0]
            
            # # y =  ptsL[l][1] - ptsL[l-1][1]

            # print(np.array(ptsT[t])[0])
            # print(np.array(ptsT[t])[1])
            p = [x,y]
            print(t)
            print(l)
            print("\n")
            print(p)
            square_list_centers.append(p)
    return 


# Orginal phote taken by the app
#starting_image_link = "dataset\\train\images\\04aed88a8d23cf27e47806eb23948495_jpg.rf.b2b9c08d458461669627c4976b744f46.jpg"
starting_image_link = "test_images\\test_images_real\IMG-20240208-WA0003.jpg"

#detect pieces with otiginal yolo model 
model_pieces = YOLO("training_output\content\\runs\detect\\train2_200_epocs\weights\\best.pt")
results_pieces_original = model_pieces.predict(starting_image_link, save=True, iou=0.2, show=False, project="yolo_output_final_warped", name="on_original_perspective", exist_ok=True)

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
img_warped = Image.fromarray(warped, "RGB")
img_warped.save("p_test.jpg")
# img.show()



boxes = results_pieces_original[0].boxes
arr = boxes.xywh.numpy()
points = arr[:,0:2]
print("POINTS_DETECTS_ORIGINAL: \n"+ str(points)+"\n\n")
points = np.float32(np.array(points))
print("POINTS_DETECTS_ORIGINAL: \n"+ str(points)+"\n\n")

list_point_detetcts = []

for point in points:
    p = np.float32(np.array([[point]]))
    new_point = cv2.perspectiveTransform(p, M)
    new_point = new_point[0][0]
    new_point[1] = new_point[1] + 40
    print(new_point)
    list_point_detetcts.append(new_point)

print(len(list_point_detetcts))
np.size(list_point_detetcts)


img = plt.imread("p_test.jpg")
index = 0
for point in list_point_detetcts:
    plt.scatter(point[0], point[1])
    index = index + 1
plt.imshow(img)
plt.show()



ptsT, ptsL = plot_grid_on_transformed_image(img_warped)

print(ptsT)
print(ptsL)

img = plt.imread("chessboard_transformed_with_grid.jpg")
# img = plt.imread("Figure_1.png")
index = 0
for point in list_point_detetcts:
    plt.scatter(point[0], point[1])
    index = index + 1
plt.imshow(img)
plt.show()




connect_square_to_detection(list_point_detetcts, ptsT, ptsL)
#conf_par = 0.1
#results = model_pieces.predict("p_test.jpg", save=True, show=False, project="yolo_output_final_warped",name="on_warped_perspective", exist_ok=True)


