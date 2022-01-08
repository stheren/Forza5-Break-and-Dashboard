import socket
import struct
import serial
import art

import threading
import time
from pynput.keyboard import Key, Controller

keyboard = Controller()
brakeKey = " "


class MonThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.arduino = serial.Serial(port='COM6', baudrate=9600, timeout=.1)

    def run(self):
        is_press = False
        while True:
            value = self.arduino.read()
            if len(value) > 0:
                if not is_press:
                    keyboard.press(Key.space)
                    is_press = True
            else:
                if is_press:
                    keyboard.release(Key.space)
                    is_press = False


forza_format = 'iIfffffffffffffffffffffffffffffffffffffffffffffffffffiiiiifffffffffffffffffHBBBBBBbbb'


def get_data(position=0, test=b""):
    data = -1
    if position > 85 or position < 0:
        raise Exception("Invalid index")
    else:
        data = test[position * 4:position * 4 + 4]
    return data


def convert_data(format="i", data=b""):
    res = 0
    try:
        res = struct.unpack(format, data)
    except Exception as e:
        pass
    return res and res[0] or 0


def get_forza_data(i=0, test=b""):
    data = get_data(i, test)
    res = convert_data(forza_format[i], data)
    return res


if __name__ == '__main__':
    art.tprint("Froza 5 Telemetry", font="small slant")
    arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.1)

    m = MonThread()
    m.start()

    def write(x):
        arduino.write(bytes(x, 'utf-8'))


    localIP = "127.0.0.1"
    localPort = 20001
    bufferSize = 1024 * 16

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))

    while True:

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        speed, rpm, rpmMax = get_forza_data(64, message), get_forza_data(4, message), get_forza_data(2, message)
        if rpmMax == 0:
            rpmMax = 1

        # write(str(int(rpm/rpmMax*100)))
        # write(str(int(speed*3.6)))

        arduino.write(struct.pack('>BBB', int(rpm / rpmMax * 100), int(speed * 3.6) - (int(speed * 3.6) % 255), int(speed * 3.6) % 255))
        # print("\r Speed : " + str(int(speed * 3.6)) + " - Rpm 100% : " + str(int(rpm / rpmMax * 100)), end="")
