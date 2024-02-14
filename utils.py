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
    # ptsR = interpolate( TR, BR )
    # ptsB = interpolate( BL, BR )
        
    # for a,b in zip(ptsL, ptsR):
    #     plt.plot( [a[0], b[0]], [a[1], b[1]], 'ro', linestyle="--" )
    # for a,b in zip(ptsT, ptsB):
    #     plt.plot( [a[0], b[0]], [a[1], b[1]], 'ro', linestyle="--" )
        
    # plt.axis('off')

    # plt.savefig('chessboard_transformed_with_grid.jpg')
    return ptsT, ptsL


# connects detected piece to the right square

def connect_square_to_detection(points, ptsT, ptsL, classes, turn):
    
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
            # print(t)
            square_list_centers.append([(ptsT[t][0]) + ((ptsT[1][0]/2)),  (ptsL[l][1]) + ((ptsL[1][1]/2))])
    
    # print(square_list_centers)

    cells = spatial.KDTree(square_list_centers)
    index = 0
    
    chessboard_list = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
    # img = plt.imread("chessboard_transformed_with_grid.jpg")
    for point in points:
        cell = cells.query([point[0], point[1]])
        plt.scatter(point[0], point[1])
        # plt.scatter(square_list_centers[cell[1]][0], square_list_centers[cell[1]][1], marker='x')
        if(len(chessboard_list[cell[1]]) < 1):
            chessboard_list[cell[1]] = dictPieces[classes[index].item()]
        index = index + 1


    # plt.imshow(img)
    # plt.show()
    fen = create_fen(chessboard_list, turn)
    # print(fen)
    return fen

def create_fen(chessboard_list, turn):

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
        
    fen = fen + " "+ turn + " KQkq - 0 1"
    
    return fen