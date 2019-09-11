import os
import time
import win32api
import win32print
from HslCommunication import *

siemens = SiemensS7Net(SiemensPLCS.S1200, "192.168.1.100")
BASE_DIR = os.path.dirname(os.path.abspath(
    __file__))

while True:
    try:
        if int(siemens.ReadBool('M31.7').Content) == 1:
            if os.path.exists(BASE_DIR + '\order.txt'):
                win32api.ShellExecute(
                    0, "print", BASE_DIR + '\order.txt', None, ".", 0)
            time.sleep(0.5)
            os.remove(BASE_DIR + '\order.txt')
            siemens.WriteBool('M6643.0', 0)
    except Exception as e:
        siemens.ConnectClose()
