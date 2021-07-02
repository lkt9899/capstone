import os, struct, array
import select
from fcntl import ioctl

# axis name list
axname = {
    0x00 : 'x',
    0x01 : 'y',
    0x02 : 'z',
    0x03 : 'rx',
    0x04 : 'ry',
    0x05 : 'rz',
    0x06 : 'throttle',
    0x07 : 'rudder',
    0x08 : 'wheel',
    0x09 : 'gas',
    0x0a : 'brake',
    0x10 : 'hat0x',
    0x11 : 'hat0y',
    0x12 : 'hat1x',
    0x13 : 'hat1y',
    0x14 : 'hat2x',
    0x15 : 'hat2y',
    0x16 : 'hat3x',
    0x17 : 'hat3y',
    0x18 : 'pressure',
    0x19 : 'distance',
    0x1a : 'tilt_x',
    0x1b : 'tilt_y',
    0x1c : 'tool_width',
    0x20 : 'volume',
    0x28 : 'misc'
}

# button name list
btnname = {
    0x120 : 'trigger',
    0x121 : 'thumb',
    0x122 : 'thumb2',
    0x123 : 'top',
    0x124 : 'top2',
    0x125 : 'pinkie',
    0x126 : 'base',
    0x127 : 'base2',
    0x128 : 'base3',
    0x129 : 'base4',
    0x12a : 'base5',
    0x12b : 'base6',
    0x12f : 'dead',
    0x130 : 'a',
    0x131 : 'b',
    0x132 : 'c',
    0x133 : 'x',
    0x134 : 'y',
    0x135 : 'z',
    0x136 : 'tl',
    0x137 : 'tr',
    0x138 : 'tl2',
    0x139 : 'tr2',
    0x13a : 'select',
    0x13b : 'start',
    0x13c : 'mode',
    0x13d : 'thumbl',
    0x13e : 'thumbr',

    0x220 : 'dpad_up',
    0x221 : 'dpad_down',
    0x222 : 'dpad_left',
    0x223 : 'dpad_right',

    # XBox 360 controller uses these codes.
    0x2c0 : 'dpad_left',
    0x2c1 : 'dpad_right',
    0x2c2 : 'dpad_up',
    0x2c3 : 'dpad_down',
}

# joystick file name
fn = '/dev/input/js0'

class Joy() :
    axis_states = {}
    ax_map = []
    button_states = {}
    btn_map = []
    dev = ''
    buf = bytearray(63)
    
    def __init__(self) :
        self.dev = open(fn, 'rb')
        self.initmap()
        print("gamepad connected...")
        
    def initmap(self) :
        self.buf = array.array('B', [0])
        ioctl(self.dev, 0x80016a11, self.buf)
        naxes = self.buf[0]

        self.buf = array.array('B', [0])
        ioctl(self.dev, 0x80016a12, self.buf)
        nbtn = self.buf[0]
        
        self.buf = array.array('B', [0] * 0x40)
        ioctl(self.dev, 0x80406a32, self.buf)
        
        # save axis
        for axis in self.buf[:naxes] :
            axis_name = axname.get(axis, 'unknown(0x%02x)' % axis)
            self.ax_map.append(axis_name)
            self.axis_states[axis_name] = 0.0

        self.buf = array.array('H', [0] * 200)
        ioctl(self.dev, 0x80406a34, self.buf)

        # save btns
        for btn in self.buf[:nbtn] :
            btn_name = btnname.get(btn, 'unknown(0x%03x)' % btn)
            self.btn_map.append(btn_name)
            self.button_states[btn_name] = 0
