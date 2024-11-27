import cv2

cap = cv2.VideoCapture(0)
r,i = cap.read()
cv2.imwrite("toto.jpg",i)

