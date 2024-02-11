from ultralytics import YOLO
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import numpy as np
from utils import order_points, plot_grid_on_transformed_image, connect_square_to_detection


def main(array_image, turn):
    # Orginal phote taken by the app
    #starting_image_link = "dataset\\train\images\\04aed88a8d23cf27e47806eb23948495_jpg.rf.b2b9c08d458461669627c4976b744f46.jpg"
    # starting_image_link = "test_images/IMG-20240208-WA0003.jpg"
    # starting_image_link = "test_images/47237294-c5a012dfa72816098d23fc8baee67834_jpg.rf.e3f72193f30138545bf762265f30083f.jpg"
    # starting_image_link = "test_images/b9402881fa580d0eb8b9b98845417550_jpg.rf.7c401587706c0c03dab27877a8d22f55.jpg"
    starting_image_link = "test_images/3a995397-685b860d412b91f5d4f7f9e643b84452_jpg.rf.5ba8dc0b5d2585d01b28089debd42cd6.jpg"
    # starting_image_link = "test_images/553dbf7c-f1a24b6bb778ee11ba33687415aa84f2_jpg.rf.6e35192bbbb13f887540067e07d5d660.jpg"

    img_PIL = Image.open(starting_image_link)
    # asarray() class is used to convert
    # PIL images into NumPy arrays
    numpy_array_original_image = np.asarray(img_PIL)

    #detect pieces with otiginal yolo model 
    model_pieces = YOLO("best_piecies.pt")
    results_pieces_original = model_pieces.predict(img_PIL, save=True, iou=0.2, show=False, project="yolo_output_final_warped", name="on_original_perspective", exist_ok=True)
    #show yolo detects 
    # input_file_name = starting_image_link.split("/")[1]
    # yolo_detect_pieces_on_input = plt.imread("yolo_output_final_warped/on_original_perspective/"+ input_file_name)
    # plt.imshow(yolo_detect_pieces_on_input)
    # plt.axis('off')
    # plt.show()

    #chessboard corner detection 
    model_corner = YOLO("best_corners.pt")
    results = model_corner.predict(img_PIL, save=True, conf=0.001, iou=0.1, imgsz=640, max_det=4,  show=False, project="yolo_output_final_warped", name="corners_detects", exist_ok=True)
    #show yolo detects 
    # yolo_detect_corners_on_input = plt.imread("yolo_output_final_warped/corners_detects/"+ input_file_name)
    # plt.imshow(yolo_detect_corners_on_input)
    # plt.axis('off')
    # plt.show()

    #extract corners coordinates and orders them 
    boxes = results[0].boxes
    arr = boxes.xywh.numpy()
    points = arr[:,0:2]
    #print("POINTS: \n"+ str(points)+"\n\n")
    corners = order_points(points)
    #print("CORNERS: \n"+ str(corners)+"\n\n")
    # img_show = plt.imread(starting_image_link)
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
    # img = Image.open(starting_image_link)   #CGANGE LINK TO BYTE ARRAY
    # image = np.asarray(img)
    #warping perspective of input image
    warped = cv2.warpPerspective(numpy_array_original_image, M, (maxWidth, maxHeight))
    img_warped = Image.fromarray(warped, "RGB")
    # img_warped.save("warped_image.jpg")
    # plt.imshow(img_warped)
    # plt.show()

    #extract yolo detects of pieces in the original images (coordinates and classes)
    boxes = results_pieces_original[0].boxes
    classes = boxes.cls
    arr = boxes.xywh.numpy()
    # print(arr)
    points = arr[:,0:2]
    heights = arr[:,3]
    # print(heights)
    points = np.float32(np.array(points))

    #trasforms all coordinates of yolo detects into new perspective using the same trasnformation matrix 
    list_point_detetcts = []

    for point, height  in zip(points, heights):
        p = np.float32(np.array([[point]]))
        new_point = cv2.perspectiveTransform(p, M)
        new_point = new_point[0][0]
        new_point[1] = new_point[1] + height * 0.4    #PARAMETER SHIFT
        # print(new_point)
        list_point_detetcts.append(new_point)

    #diplayng new coordinates of yolo detects into warped imaage for showing purposes 
    # img = plt.imread("warped_image.jpg")
    # index = 0
    # for point in list_point_detetcts:
    #     plt.scatter(point[0], point[1])
    #     index = index + 1
    # plt.imshow(img_warped)
    # plt.axis('off')
    # plt.savefig('warped_image_with_detects.jpg', bbox_inches='tight', pad_inches=0)
    # plt.show()

    #display grid on warped image and returning coordinates of every column from top and every line from the left
    ptsT, ptsL = plot_grid_on_transformed_image(img_warped)   #without scattaer
    # warped_image_with_detects = Image.open('warped_image_with_detects.jpg')
    # ptsT, ptsL = plot_grid_on_transformed_image(warped_image_with_detects) #with scattaer
    # print(ptsT)
    # print(ptsL)
    # plt.close()
    # grid_image = plt.imread("chessboard_transformed_with_grid.jpg")
    # plt.imshow(grid_image)
    # plt.axis('off')
    # plt.show()

    fen = connect_square_to_detection(list_point_detetcts, ptsT, ptsL, classes, turn)
    print(fen)

    return fen



