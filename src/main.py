from cap_f import *
from car.mycar import Mycar
from multiprocessing import Process, Queue

# main
def main() :
    car = Mycar()   # def car

    # Multi-Processing
    p1 = Process(target = control, args = (car, ))
    p2 = Process(target = Comm)
    p3 = Process(target = server)

    # start
    p1.start()
    p2.start()
    p3.start()

    # wait until fin
    p1.join()
    p2.join()
    p3.join()

    # clean Queue used for running
    qClean()
    print('main finished')

# is it main
if __name__ == "__main__" :
    main()
