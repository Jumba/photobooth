import os
from PyQt5 import QtCore

import serial
import time

from PyQt5.QtCore import QThread



class SerialListener(QThread):

    left = QtCore.pyqtSignal()
    right = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.canceled = False

    def initialize_arduino(self):
        try:
            self.serial = serial.Serial('/dev/ttyACM0', 9600) # Connec to the Arduino at 9600 baud
            print(self.serial)
        except serial.serialutil.SerialException:
            self.abort()

    def abort(self):
        self.canceled = True

    def run(self):
        self.initialize_arduino()
        while True and not self.canceled:
            os.system('clear')
            input = self.serial.readline().strip()
            if input == b"right":
                self.right.emit()
            elif input == b"left":
                self.left.emit()

            self.serial.flushInput()
            self.serial.flushOutput()