import cv2

img = cv2.imread("img-data/test.png", 0)

cv2.imshow("Testing", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite("img-data/tester.jpg", img)
