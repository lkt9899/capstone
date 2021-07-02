from multiprocessing import Process, Queue
from joy import Joy
from image.img_f import *
import os, struct, array
from fcntl import ioctl
import serial
import select
import socket
from _thread import *
import numpy as np

# LEFT : left psd value,    RIGHT : right psd value
LEFT = 0
RIGHT = 0

# Queue for receiving sensor value
qL = Queue()
qR = Queue()
qE = Queue()

# Queue for TCP
enclosure_queue = Queue()

# Thread Function
def threaded(client_socket, addr, queue) :
    print('Connected by ', addr[0], ':', addr[1])

    while qE.empty() :
        try :
            data = client_socket.recv(1024)

            if not data :
                print('Disconnected by ' + addr[0], ':', addr[1])
                break

            stringData = queue.get()
            client_socket.send(str(len(stringData)).ljust(16).encode())
            client_socket.send(stringData)

        except ConnectionResetError as e :
            print('Disconnected by ' + addr[0], ':', addr[1])
            break
    print('threaded exit')
    client_socket.close()

# Serial Comm
def Comm() :
    print('Start Comm')
    
    # get Arduino name
    an = '/dev/'
    BR = 9600
    for fn in os.listdir('/dev') :
        if fn.startswith('ttyACM') :
            an += fn

    # connect Serial Comm
    ser = serial.Serial(an, BR)
    print(an, "... Connected")

    # get data and separation
    cnt = 0
    while qE.empty() :
        r, w, e = select.select([ser], [], [], 0.2)
        if ser in r :
            q = ''
            state = ser.readline()
            for i in state :
                if i == 13 :    # separate at space
                    break
                q += chr(i)
                
            cut = q.find(' ')
            
            if cut != -1 :
                LEFT = int(q[0:cut])
                RIGHT = int(q[cut+1:])
                qL.put(LEFT)
                qR.put(RIGHT)
  
    print('comm exit')

# control
def control(car) :
    print('control')
    R = 0
    L = 0
    evbuf = 0
    
    j = Joy()
    jsdev = j.dev
    while qE.empty() :            
        r, w, e = select.select([jsdev], [], [], 0.01)
        if jsdev in r :
            evbuf = jsdev.read(8)
        
        if evbuf :
            while not qL.empty() :
                R = qR.get()
                L = qL.get()

            time, value, type, number = struct.unpack('IhBB', evbuf)
            
            # initial
            if type & 0x80 :
                pass

            # button
            if type & 0x01 :
                button = j.btn_map[number]
                # exit
                if button == 'x' :
                    if value :
                        #print("%s pressed" % (button))
                        qE.put(1)
                    else :
                        print("%s released" % (button))

            # axis
            if type & 0x02 :
                axis = j.ax_map[number]
                fvalue = value / 32767.0
                
                # psd value > 200 ==> go back slowly
                if L > 200 or R > 200 :
                    car.throttle = -0.8

                # steering    
                if axis == 'x' :
                    car.steering = fvalue
                    j.axis_states[axis] = fvalue
                    #print("%s : %.3f" % (axis, fvalue))
                    
                # throttle
                if axis == 'rz' :
                    if L < 200 and R < 200 :
                        car.throttle = fvalue
                        j.axis_states[axis] = fvalue
                        #print("%s : %.3f" % (axis, fvalue))
    
    car.throttle = 0
    car.steering = 0
    print('control exit')

# TCP Tran
def server() :
    print('server start')
    HOST = '192.168.43.235'
    PORT = 9999

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    while True :
        print('wait.')
        client_socket, addr = server_socket.accept()
        start_new_thread(webcam, (enclosure_queue, qE))
        start_new_thread(threaded, (client_socket, addr, enclosure_queue,))
        
    exit()
    server_socket.close()
    print('server exit')
    os.system('fuser -k 9999/tcp')      # kill process

# clean Queue before exit
def qClean() :
    while True :
        if not qL.empty() :
            qL.get()
        elif not qR.empty() :
            qR.get()
        elif not qE.empty() :
            qE.get()
        else :
            print('clean fin')
            break
    
