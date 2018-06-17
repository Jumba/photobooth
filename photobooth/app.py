import signal
import threading
from enum import Enum
from threading import Lock

import sys

import time
from PyQt5 import uic
from qtpy import QtCore
from qtpy.QtWidgets import QApplication, QMainWindow, QLabel
import qtpy.QtGui as QtGui

from photobooth import NEW_IMAGES, Options, PROCESSED_IMAGES, UPLOADED_IMAGES
from photobooth.camera import Camera
from photobooth.process import ImageProcessor
from photobooth.serial import SerialListener
from photobooth.uploader import UploadManager


class PhotobootStatus(Enum):
    START = 0
    SHOOTING = 1
    PROCESSING = 2
    DISPLAYING = 3

class Button(Enum):
    LEFT = 0
    RIGHT = 1


class PhotoboothApplication(QApplication):

    _actions = None

    def __init__(self, *argv):
        QApplication.__init__(self, *argv)

        self._status = PhotobootStatus.START
        self._setup_actions()

        self.transfer_lock = Lock()
        self.setup = False
        self.camera = None
        self.options = Options()
        self.processor = ImageProcessor(self, self.options, NEW_IMAGES, PROCESSED_IMAGES)
        self.uploader = UploadManager(self, PROCESSED_IMAGES, UPLOADED_IMAGES )
        self.listener = SerialListener(self)
        self.listener.left.connect(self.left_button)
        self.listener.right.connect(self.right_button)

        self._next_image = None

        self.image_window = None
        self.main_window = MainWindowController(None, self)
        self.main_window.show()


    def setup_photobooth(self, camera_model):
        self.camera = Camera(self, camera_model, NEW_IMAGES)
        self.setup = True
        self.uploader.start()
        self.listener.start()


    def start(self):
        assert self.setup, "Setup not completed.'"

    def force_exit(self, message):
        print("Exiting: {}".format(message))
        sys.exit(0)

    def next_image(self, filename):
        self.status = PhotobootStatus.DISPLAYING
        self._next_image = filename
        self.image_window = PhotoWindow(self, filename, None)
        self.image_window.show()

    def clear_next(self):
        self._next_image = None

    def single_shot(self):
        self.countdown()
        QtCore.QTimer.singleShot(4000, self.init_single)

    def init_single(self):
        self.camera.take_picture()
        self.camera.download_images()
        self.processor.process()

    def collage_shot(self):
        self.countdown()
        QtCore.QTimer.singleShot(4000, self.init_collage)


    def init_collage(self):
        self.camera.take_picture(count=4, interval=1)
        self.camera.download_images()
        self.processor.process()

    def reset(self):
        if self.image_window:
            self.image_window.hide()
            self.image_window = None
        self.main_window.stackedWidget.setCurrentIndex(0)
        self.status = PhotobootStatus.START

        self.main_window.show()


    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        self._status = new_status
        print("Status now: {}".format(self._status))


    def left_button(self):
        print("left")
        self.step(Button.LEFT)

    def right_button(self):
        print("right")
        self.step(Button.RIGHT)

    def countdown(self):
        self.status = PhotobootStatus.SHOOTING
        QtCore.QTimer.singleShot(1000, self.main_window.count3)
        QtCore.QTimer.singleShot(2000, self.main_window.count2)
        QtCore.QTimer.singleShot(3000, self.main_window.count1)
        QtCore.QTimer.singleShot(3500, self.main_window.hide)


    def _setup_actions(self):
        self._actions = {
            PhotobootStatus.START: {
                Button.RIGHT: self.single_shot,
                Button.LEFT: self.collage_shot,
            },
            PhotobootStatus.SHOOTING: {
                Button.RIGHT: lambda: None,
                Button.LEFT: lambda: None,
            },
            PhotobootStatus.PROCESSING: {
                Button.RIGHT: lambda: None,
                Button.LEFT: lambda: None,
            },
            PhotobootStatus.DISPLAYING: {
                Button.RIGHT: self.reset,
                Button.LEFT: self.reset,
            },
        }

    def step(self, button):
        self._actions[self.status][button]()



class MainWindowController(QMainWindow):
    """

        Create a MainWindowController. Extends QMainWindow from the PyQt5 library.

        Takes a MarketApplication and the location of the ui file as parameters during construction.

        Used for hooking up the controllers to the view that is generated during runtime.

    """
    def __init__(self, parent=None, app=None, ui_location='photobooth/main.ui'):
        super(MainWindowController, self).__init__(parent)
        self.app = app
        uic.loadUi(ui_location, self)
        self.center()

    def center(self):
        frame_gm = self.frameGeometry()
        screen =  self.app.desktop().screenNumber( self.app.desktop().cursor().pos())
        center_point = self.app.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def count3(self):
        self.stackedWidget.setCurrentIndex(1)

    def count2(self):
        self.stackedWidget.setCurrentIndex(2)

    def count1(self):
        self.stackedWidget.setCurrentIndex(3)


class PhotoWindow(QMainWindow):

    def __init__(self, app, filename, flags, *args, **kwargs):
        super(PhotoWindow, self).__init__(flags, *args, **kwargs)
        self.app = app
        self.filename = filename
        self.init()

    def init(self):
        self.setGeometry(0, 0, 1500, 1000)
        pic = QLabel(self)
        pic.setGeometry(0,0, 1500, 1000)
        pixmap = QtGui.QPixmap(self.filename)
        pixmap = pixmap.scaledToHeight(1000)
        pic.setPixmap(pixmap)
        self.center()

    def center(self):
        frame_gm = self.frameGeometry()
        screen =  self.app.desktop().screenNumber( self.app.desktop().cursor().pos())
        center_point = self.app.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())