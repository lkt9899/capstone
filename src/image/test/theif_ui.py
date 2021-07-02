import cv2
import numpy as np
import time

# blood
bl = cv2.imread('./blood.png')
bl_size = 440 # assert  bl_size + 170 < 640
bl = cv2.resize(bl, (bl_size, 20))

# bkg red
red = cv2.imread('./red.png')
red = cv2.resize(red,(640,480))

# bkg blood
g_bl = cv2.imread('./blood_ground.png')
g_bl_size = 460 # assert  bl_size + 160 < 640
g_bl = cv2.resize(g_bl, (g_bl_size, 30))

# aim
aim = cv2.imread("./aim.png")

# target
target_img = cv2.imread("./real_target.png")

# HP set
max_health = 4
health = max_health
OneAttack_health = int(bl_size/max_health)

def webcam() :
    # connect webcam, create frame
    cap = cv2.VideoCapture(0)
    
    nframe = 0      # var count frame
    ntime = 0       # var count time
    text = '0'      # text express FPS on display
    
    alpha = 0.2     # transparency
    hit = 0         # is hit?

    # is running
    cnt = 0
    
    while True :
        ret, frame = cap.read()

        if not ret :
            break
        
        # calc frame
        start = time.time()
        if ntime >= 1 :
            text = "FPS : " + str(nframe)
            ntime = 0
            nframe = 0
            
        cv2.putText(frame, text, (0, 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

        global bl           # HP
        global bl_size      # HP Bar size
        global health       # HP count
        global aim          # aim image
        global target_img   # targe image

        g_blood = cv2.addWeighted(frame[0 : 30, 160 : 160+g_bl_size, :], alpha, g_bl[:, 0 : g_bl_size, :], 1 - alpha, 0)    # HP BOX
        blood = cv2.addWeighted(frame[5 : 25, 170 : 170+bl_size, :], alpha, bl[:, 0 : bl_size, :], 1 - alpha, 0)            # HP

        #Frame End x = 160
        
        frame[0 : 30, 160 : 160+g_bl_size]   = g_blood      #g_bl   # shape = (30, g_bl_size)
        if health >= 0 :
            frame[5 : 25, 170 : 170+bl_size] = blood        #bl     # shape = (20, bl_size)

        k = cv2.waitKey(1)

        # if hit
        if cnt > 0 :
            if bl_size > 2 :
                bl_size -= 2
                cnt -= 2
            if health >= 0 :
                bl = bl[:, 0 : bl_size, :]
        
        if (k == ord('b')) & (time.time() - hit > 2) :     # no damage after hit during 2sec
            if health > 0 :
                cnt += OneAttack_health
                health -= 1
                hit = time.time()

        # if hit, be bkg red during 2sec
        if time.time() - hit < 2 :
            frame = cv2.addWeighted(frame[:, :, :], 1 - alpha, red[:, :, :], alpha, 0)

        cv2.imshow('frame', frame)

        # if press q ==> quit
        if (k == ord('q')) :
            break
        
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', conImg, encode_param)
        
        # add img to data for send to server
        data = np.array(imgencode)
        stringData = data.tostring()
        queue.put(stringData)

        # calc time per frame
        tt = time.time() - start
        ntime += tt
        nframe += 1
        #print(tt)
        
    print('webcam exit')    
    cap.release()

if __name__ == "__main__" :
    webcam()
