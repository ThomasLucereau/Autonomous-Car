import cv2
import matplotlib.pyplot as plt

cap = cv2.VideoCapture(0)
ret,img = cap.read()
plt.imshow(img)
plt.show()
