import time

class Frame :
    nframe = 0
    ntime = 0
    text = ''
    onesec = False
    fps = 0
    start = 0

    def __init__(self) :
        self.nframe = 0
        self.ntime = 0
        self.text = ''
        self.fps = 0
        self.start = 0
        print("new frame generated !")
        
    # timer start
    def timerset(self) :
        self.start = time.time()
    
    # inc per each frame 
    def inc(self) :
        self.nframe += 1
        t = time.time() - self.start
        self.ntime += t
    
    def set_zero(self) :
        self.ntime = 0
        self.nframe = 0
        
    def calc(self) :
        self.fps = self.nframe
        self.text = 'FPS : ' + str(self.fps)
        self.set_zero()
