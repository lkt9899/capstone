#from image.myimgframe import Frame
import cv2
import numpy as np
import time

# find contours, return 2 outputs
def img_contours(BGR_img):
    # BGR -> HSV transform
    hsvImg = cv2.cvtColor(BGR_img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsvImg)
    
    # Binarization by color
    binImg = np.where(((h>=20) & (h<=30) & (v>=150) & (s<=220) & (s>=180)), 255, 0)
    #binImg = np.where(((h>=50)& (h<=60) &(v>=110) & (s>=200)), 255, 0)
    binImg = binImg.astype(np.uint8)
    
    # eliminate background noise
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (9, 9))
    erode = cv2.erode(binImg, kernel, anchor=(-1, -1), iterations=1)
    
    # find contours
    isTarget = False
    contours = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[1]
    for i in contours:
        if np.array(i).shape[0] > 500: #error dot >= 500
            print(np.array(i).shape[0])
            cv2.drawContours(BGR_img, i, -1, (0, 0, 255), 2)
            isTarget = True
            break
            
    return BGR_img, isTarget

#webcam
def webcam(queue, qE) :
    # connect webcam, create frame
    cap = cv2.VideoCapture(0)
    nframe = 0
    ntime = 0
    text = '0'
    
    # is running
    while qE.empty() :
        ret, frame = cap.read()
        if not ret :
            break
        
        # calc frame
        start = time.time()
        if ntime >= 1 :
            text = "FPS : " + str(nframe)
            ntime = 0
            nframe = 0
        
        # get contour
        conImg, chk = img_contours(frame)
        cv2.putText(conImg, text, (0, 25), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        if chk :
            cv2.putText(conImg, 'Target', (0, 240), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', conImg, encode_param)

        # add img to data for send to server
        data = np.array(imgencode)
        stringData = data.tostring()
        queue.put(stringData)
        tt = time.time() - start
        ntime += tt
        nframe += 1
        print(tt)
    print('webcam exit')    
    cap.release()

