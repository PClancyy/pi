import cv2
def thread_count(img, thres):
    img_gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    inv_img=cv2.bitwise_not(img_gray)   #invert b&w colors
    res,thresh_img=cv2.threshold(inv_img, thres, 255, cv2.THRESH_BINARY_INV)
    thresh_img=255- thresh_img
    contours,hierarchy=cv2.findContours(thresh_img, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    area = []
    for i in range(len(contours)):
          area.append(cv2.contourArea(contours[i]))
    count=len([num for num in area if num > 4])
    return count, thresh_img