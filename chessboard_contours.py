import cv2

# Carica l'immagine
image = cv2.imread('test.jpg')

# Converti l'immagine in scala di grigi
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Trova i contorni nell'immagine in scala di grigi
contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(contours)

# Seleziona il contorno con l'area massima
chessboard_contour = max(contours, key=cv2.contourArea)



# Disegna il contorno sulla copia dell'immagine originale
image_with_contour = image.copy()
cv2.drawContours(image_with_contour, contours, -1, (0, 255, 0), 2)

cv2.imwrite("contours.jpg", image_with_contour) 