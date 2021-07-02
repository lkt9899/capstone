import cv2
import numpy as np
import time

############################################################
#                       read images                        #
############################################################

# btn size
button_size = 100

# atk btn pushed
pushed_button = cv2.imread('./pushed_button.png')
pushed_button = cv2.resize(pushed_button, (button_size, button_size))

# atk btn normal
shoot_button = cv2.imread('./shoot_button.png')
shoot_button = cv2.resize(shoot_button,(button_size, button_size))

# aim
aim = cv2.imread("./real_aim.png")

############################################################
#                       HP Box Set                         #
############################################################

# box size
box_width, box_height = 70, 110
health_width, health_height = 55, 85

box = []
for i in range(4):
    box.append([])

# HP Box change by HP
box[0].append(cv2.resize(cv2.imread('./level_0_box.png'), (box_width, box_height)))         # HP  25%
box[0].append(cv2.resize(cv2.imread('./level_0_health.png'), (health_width, health_height)))

box[1].append(cv2.resize(cv2.imread('./level_1_box.png'), (box_width, box_height)))         # HP  50%
box[1].append(cv2.resize(cv2.imread('./level_1_health.png'), (health_width, health_height)))

box[2].append(cv2.resize(cv2.imread('./level_2_box.png'), (box_width, box_height)))         # HP  75%
box[2].append(cv2.resize(cv2.imread('./level_2_health.png'), (health_width, health_height)))

box[3].append(cv2.resize(cv2.imread('./level_3_box.png'), (box_width, box_height)))         # HP 100%
box[3].append(cv2.resize(cv2.imread('./level_3_health.png'), (health_width, health_height)))

# box[i][j] //... i = level, j = box or health

# HP set
max_health = 4                                      # can not change
health = max_health                                 # max HP
OneAttack_health = int(health_height/max_health)    # One hit damage

# generate mask
# INPUT     : image             -> UI image,                alpha           -> transparency
# OUTPUT    : mask_background   -> mask for original frame, mask_foreground -> mask for UI image
def make_mask(image, alpha) :
    w, h = fore_ground.shape[1], fore_ground.shape[0]   # width, height
    mask_background = np.ones((h,w,3))                  # arr[h][w][3] fill with 1

    for i in range(h) :
        for j in range(w) :
            if (image[i][j][0] == 0) & (image[i][j][1] == 0) & (image[i][j][2] == 0) :
                continue
            mask_back[i][j] = 1 - alpha
    mask_foreground = np.ones((h,w,3)) - mask_back

    return mask_background, mask_foreground

# 배경 제거 및 투명화 하려는 이미지와 투명도를 인자로 받는다.
# 인자로 받은 이미지의 너비와 높이를 계산 한 뒤에 그와 같은 크기로 모두 1로 채워진 h X w X 3 mask를 생성한다.
# image의 background는 rgb값이 모두 0으로 되어 있기 때문에 rgb값이 0인 부분은 그대로 1로 남기고 그 외의 값에 1-투명도를 넣어준다.
# 이 때 이 마스크가 원본 이미지의 mask가 된다.
# 그리고 모두 1로 채워진 mask에서 방금 구한 mask를 빼서 image의 mask를 생성해준다.
# 이 때 생성 된 두개의 mask를 가지고 mask_back * original image + mask_fore * UI image를 통해 투명화 및 배경이 제거 된 이미지를 얻을 수 있다. 

# detect target
def img_contours(BGR_img):
    # BGR -> HSV transform
    hsvImg = cv2.cvtColor(BGR_img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsvImg)
    
    # Binarization by color
    binImg = np.where(((h >= 15) & (h <= 45) & (v >= 100) & (s >= 150)), 255, 0)
    binImg = binImg.astype(np.uint8)
    
    # eliminate background noise
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
    erode = cv2.erode(binImg, kernel, anchor = (-1, -1), iterations = 1)
    
    # find contours
    isTarget = False
    isPoint = False
    contours = cv2.findContours(erode, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[1]
    Rect_target = []        # target
    Rect_point = []         # aim
    
    if np.array(contours).shape :
        for i in contours :
            if np.array(i).shape[0] >=200 :
                x, y, w, h = cv2.boundingRect(i)
                cv2.rectangle(BGR_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                Rect_target.append(x)
                Rect_target.append(y)
                Rect_target.append(w)
                Rect_target.append(h)
                isTarget = True

        for i in contours :
            if (np.array(i).shape[0] >= 50) & (np.array(i).shape[0] < 200) & (isTarget) :
                x, y, w, h = cv2.boundingRect(i)
                Rect_point.append(x)
                Rect_point.append(y)
                Rect_point.append(w)
                Rect_point.append(h)
                cv2.rectangle(BGR_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                isPoint = True

    return BGR_img, isTarget, Rect_target,isPoint, Rect_point

def webcam() :
    # connect webcam, create frame
    global box                  # HP box
    cap = cv2.VideoCapture(0)   # frame
    
    nframe = 0      # var count frame
    ntime = 0       # var count time
    text = '0'      # text express FPS on display
    
    alpha = 0.2     # transparency
    hit = 0         # is hit?
    bl_start = 0    # HP bar start index
    
    # is running
    cnt = 0
    
    ## make mask
    # make mask for atk button
    mask_back_n, mask_fore_n = make_mask(shoot_button, 0.2)     # mask for atk btn 
    mask_back_t, mask_fore_t = make_mask(shoot_button, 0.9)     # mask for atk btn when target detected
    mask_back_p, mask_fore_p = make_mask(pushed_button, 0.9)    # mask for atk btn pushed

    # mask for HP bar
    mask_box = []
    for i in range(4):
        mask_box.append([])

    mask_box[0].append(make_mask(box[0][0], 0.7))   # 25%
    mask_box[0].append(make_mask(box[0][1], 0.7))
    
    mask_box[1].append(make_mask(box[1][0], 0.7))   # 50%
    mask_box[1].append(make_mask(box[1][1], 0.7))
    
    mask_box[2].append(make_mask(box[2][0], 0.7))   # 75%
    mask_box[2].append(make_mask(box[2][1], 0.7))
    
    mask_box[3].append(make_mask(box[3][0], 0.7))   # 100%
    mask_box[3].append(make_mask(box[3][1], 0.7))


    aim_re = []     # real aim image
    aim_back =[]    # background of mask
    aim_fore = []   # foreground of mask
    rect_tmp = []   # rect
    
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
            
        # get contour
        conImg, chk_t, Rect_t, chk_p, Rect_p = img_contours(frame)
        cv2.putText(conImg, text, (0, 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

        
        global box_height    # HP box h
        global box_width     # HP box w
        global health        # HP
        global aim           # aim
        global health_height # HP h
        global health_width  # HP w
        
        k = cv2.waitKey(1)

        # if hit
        if cnt > 0 :
            if bl_start < health_height :
                bl_start += 2
                cnt -= 2
                
                if cnt <= 0 :
                    health -= 1
        
        back = conImg[360 : 360+button_size, 520 : 520+button_size]

        # no target
        if chk_t == False :
            conImg[360 : 360+button_size, 520 : 520+button_size] = mask_back_n*back + mask_fore_n*shoot_button

        # target detected
        if chk_t :
            conImg[360 : 360+button_size, 520 : 520+button_size] = mask_back_t*back + mask_fore_t*shoot_button  # atk button activate  
            target_box_x,   target_box_y  = Rect_t[0] + Rect_t[2] + 7,      Rect_t[1] + Rect_t[3]               # target box axis
            target_x,       target_y      = Rect_t[0] + Rect_t[2] + 16,     Rect_t[1] + Rect_t[3] - 12          # target axis
            
            # axis display HP bar
            if (target_y <= 480) & (target_x <= 640) :          # MAX SIZE
                health_x = target_x + health_width              # HP bar axis to display right side of target
                health_y = target_y - (health_height - bl_start)# 
                
                box_x = target_box_x + box_width                # HP Box axis to display right side of target
                box_y = target_box_y - box_height               #

                # define undefined case(axis out of range)
                if health_x > 640 :
                   health_x = 640
                   
                if health_y < 0 :
                    health_y = 0
                    
                if box_x > 640 :
                    box_x = 640
                    
                if box_y < 0 :
                    box_y = 0

                ## display thief's HP
                # mask_box[i][j][k] (i = level,  j : 0 -> box, 1 -> HP,  k = 0 -> mask background,  1 -> mask foreground)
                # if UI size bigger than frame size, cut it
                y_idx = health_height - (target_y - health_y)      # real y axis of HP bar
                x_idx = health_x - target_x                        # real x axit of HP bar

                # mask_back*original image + mask_fore*UI image
                # HP Bar
                blood_background    = conImg[health_y : target_y, target_x : health_x, :]
                blood               = mask_box[health - 1][1][0][y_idx:, 0:x_idx, :]*blood_background +
                                      mask_box[health - 1][1][1][y_idx:, 0:x_idx, :]*box[health - 1][1][y_idx:, 0:x_idx, :]

                y_idx = box_height - (target_box_y - box_y)
                x_idx = box_x-target_box_x
                
                # HP Box
                back_box    = conImg[box_y : target_box_y, target_box_x : box_x, :]
                box_img     = mask_box[health - 1][0][0][y_idx:, 0:x_idx, :]*back_box +
                              mask_box[health - 1][0][1][y_idx:, 0:x_idx, :]*box[health - 1][0][y_idx:, 0:x_idx, :]

                # display HP UI on original frame
                conImg[box_y : target_box_y, target_box_x : box_x] = box_img
                conImg[health_y : target_y, target_x : health_x]   = blood
                
            # if aim is on target
            if chk_p :
                if (!qB.empty()) & (time.time() - hit > 2): # no damage after hit during 2sec
                    qB.get()
                    aim_re = cv2.resize(aim, (Rect_p[2], Rect_p[3]))
                    rect_tmp = Rect_p
                    aim_back, aim_fore = make_mask(aim_re, 0.7)

                    # if HP is not 0
                    if health > 0:
                        cnt += OneAttack_health
                        hit = time.time()

        # display aim image during 0.5sec
        if time.time() - hit < 0.5 :
            back_aim = conImg[rect_tmp[1] : rect_tmp[1]+rect_tmp[3], rect_tmp[0] : rect_tmp[0]+rect_tmp[2]]
            conImg[rect_tmp[1] : rect_tmp[1]+rect_tmp[3], rect_tmp[0] : rect_tmp[0]+rect_tmp[2]] = aim_back*back_aim + aim_fore*aim_re
            conImg[360 : 360+button_size, 520 : 520+button_size] = mask_back_p*back + mask_fore_p*pushed_button
        
        cv2.imshow('frame', conImg)

        if k == ord('q'):
            break
        
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', conImg, encode_param)
        
        # add img to data for send to server
        data = np.array(imgencode)
        stringData = data.tostring()
        queue.put(stringData)
        
        tt = time.time() - start
        ntime += tt
        nframe += 1
        #print(tt)
    print('webcam exit')    
    cap.release()

if __name__ == "__main__" :
    webcam()
