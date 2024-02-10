from ultralytics import YOLO
from PIL import Image
import os
import cv2
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
from scipy import spatial

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

def connect_square_to_detection(points, ptsT, ptsL, classes):
    
    square_list_centers = []
    #for l in range(0,len(ptsL)-1):
    #    for t in range(0,len(ptsT)-1):
        
            # print(np.array(ptsT[t])[0])
            # print(np.array(ptsT[t])[1])
            
    #        square_list_centers.append([(ptsT[t][0]) + ((ptsT[1][0]/2)),  (ptsL[l][1]) + ((ptsL[1][1]/2))])
    
    dictPieces = {
        1:'b', 2:'k', 3:'n', 4:'p', 5:'q', 6:'r', 7:'B', 8:'K', 9:'N', 10:'P', 11:'Q', 12:'R'
    }

    for t in range(len(ptsT)-2, -1, -1):
        for l in range(0, len(ptsT)-1):
            print(t)
            square_list_centers.append([(ptsT[t][0]) + ((ptsT[1][0]/2)),  (ptsL[l][1]) + ((ptsL[1][1]/2))])
    
    print(square_list_centers)

    cells = spatial.KDTree(square_list_centers)
    index = 0
    
    chessboard_list = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]

    for point in points:
        cell = cells.query([point[0], point[1]])
        #plt.scatter(point[0], point[1])
        #plt.scatter(square_list_centers[cell[1]][0], square_list_centers[cell[1]][1], marker='x')
        if(len(chessboard_list[cell[1]]) < 1):
            chessboard_list[cell[1]] = dictPieces[classes[index].item()]
        index = index + 1

    #plt.imshow(image_11)
    #plt.show()
    fen = create_fen(chessboard_list)
    print(fen)
    return 

def create_fen(chessboard_list):

    arr = np.array(chessboard_list)
 
    chessboard_matrix = arr.reshape(-1, 8)

    print(chessboard_matrix)
    fen = ""

    for line in range(8):
        count = 0
        tempString = ""
        for cell in range(8): 
            if(len(chessboard_matrix[line][cell]) < 1):
                count = count + 1
            else:
                if(count > 0):
                    tempString = tempString + str(count)
                    count = 0
                tempString = tempString + chessboard_matrix[line][cell]
        if(count > 0):
            tempString = tempString + str(count)
        
        fen = fen + tempString
        if(line < 7):
            fen = fen + "/"
        
    fen = fen + " w KQkq - 0 1"
    return fen



# Orginal phote taken by the app
#starting_image_link = "dataset\\train\images\\04aed88a8d23cf27e47806eb23948495_jpg.rf.b2b9c08d458461669627c4976b744f46.jpg"
# starting_image_link = "test_images\\test_images_real\IMG-20240208-WA0003.jpg"
starting_image_link = "test_images/47237294-c5a012dfa72816098d23fc8baee67834_jpg.rf.e3f72193f30138545bf762265f30083f.jpg"

#detect pieces with otiginal yolo model 
model_pieces = YOLO("best_piecies.pt")
results_pieces_original = model_pieces.predict(starting_image_link, save=True, iou=0.2, show=False, project="yolo_output_final_warped", name="on_original_perspective", exist_ok=True)
#show yolo detects 
input_file_name = starting_image_link.split("/")[1]
yolo_detect_pieces_on_input = plt.imread("yolo_output_final_warped/on_original_perspective/"+ input_file_name)
plt.imshow(yolo_detect_pieces_on_input)
plt.show()

#chessboard corner detection 
model_corner = YOLO("best_corners.pt")
results = model_corner.predict(starting_image_link, save=True, conf=0.001, iou=0.1, imgsz=640, max_det=4,  show=False, project="yolo_output_final_warped", name="corners_detects", exist_ok=True)
#show yolo detects 
yolo_detect_pieces_on_input = plt.imread("yolo_output_final_warped/corners_detects/"+ input_file_name)
plt.imshow(yolo_detect_pieces_on_input)
plt.show()

#estract corners coordinates and orders them 
boxes = results[0].boxes
arr = boxes.xywh.numpy()
points = arr[:,0:2]
#print("POINTS: \n"+ str(points)+"\n\n")
corners = order_points(points)
#print("CORNERS: \n"+ str(corners)+"\n\n")
img_show = plt.imread(starting_image_link)
#plt.imshow(img_show)

#assigning logical names to individual corners coordinates 
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

#calculate the persepctive transform matrix 
M = cv2.getPerspectiveTransform(corners, dst)
img = Image.open(starting_image_link)
image = np.asarray(img)
#warping perspective of input image
warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
img_warped = Image.fromarray(warped, "RGB")
img_warped.save("warped_image.jpg")
plt.imshow(img_warped)
plt.show()


boxes = results_pieces_original[0].boxes
classes = boxes.cls
arr = boxes.xywh.numpy()
points = arr[:,0:2]
points = np.float32(np.array(points))

list_point_detetcts = []

for point in points:
    p = np.float32(np.array([[point]]))
    new_point = cv2.perspectiveTransform(p, M)
    new_point = new_point[0][0]
    new_point[1] = new_point[1] + 40
    print(new_point)
    list_point_detetcts.append(new_point)



img = plt.imread("warped_image.jpg")
index = 0
for point in list_point_detetcts:
    plt.scatter(point[0], point[1])
    index = index + 1
#plt.imshow(img)
#plt.show()



ptsT, ptsL = plot_grid_on_transformed_image(img_warped)

print(ptsT)
print(ptsL)

img = plt.imread("chessboard_transformed_with_grid.jpg")
# img = plt.imread("Figure_1.png")
index = 0
for point in list_point_detetcts:
    plt.scatter(point[0], point[1])
    index = index + 1
#plt.imshow(img)
#plt.show()




connect_square_to_detection(list_point_detetcts, ptsT, ptsL, classes)
#conf_par = 0.1
#results = model_pieces.predict("p_test.jpg", save=True, show=False, project="yolo_output_final_warped",name="on_warped_perspective", exist_ok=True)


