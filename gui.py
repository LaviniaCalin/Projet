# -*- coding: utf-8 -*-

''' GUI for the dinning philosophers problem '''

import math

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt

from message import msg_queue, Message


class WidgetWithBackground(QtGui.QLabel):
    """
    Baseclass for the Dining Philosophers GUI

    Inherits QLabel and extends it to feature background image.
    """

    def __init__(self, *args, **kwargs):
        """
        Baseclass constructor

        Searches for width, height and path to image and resize accordingly
        """
        self.orig_width = kwargs.pop('width')
        self.orig_height = kwargs.pop('height')
        self.background = kwargs.pop('background')
        super(WidgetWithBackground, self).__init__(*args, **kwargs)
        self.resize(self.orig_width, self.orig_height)
        self.setAlignment(Qt.AlignCenter)
        self._initBackgroundImage()

    def _initBackgroundImage(self):
        size = self.size()
        self.pixmap = QtGui.QPixmap(self.background).scaled(
            size.width(), size.height(), Qt.KeepAspectRatio
        )
        self.setPixmap(self.pixmap)


class PhilWidget(WidgetWithBackground):
    """
    Widget corresponding to a philosopher

    Extends WidgetWithBackground and resizes the widget
    for proper rotation to be possible
    """
    def __init__(self, *args, **kwargs):
        self.angle = kwargs.pop('angle', None)
        super(PhilWidget, self).__init__(*args, **kwargs)

        diag = self._compute_diagonal(self.width(), self.height())
        self.resize(diag, diag)
        self.angle and self._rotate_pixmap(self.angle)

    def _compute_diagonal(self, a, b):
        return int(math.sqrt(a*a + b*b))

    def _rotate_pixmap(self, angle):
        self.pixmap = self.pixmap.transformed(QtGui.QTransform().rotate(angle))
        self.setPixmap(self.pixmap)

    def move(self, x, y):
        size = self.size()
        super(PhilWidget, self).move(x - self.height()//2, y - self.width()//2)

    def acquire(self):
        self.setStyleSheet('background-color: red;')

    def release(self):
        self.setStyleSheet('background-color: None;')


class ForkWidget(PhilWidget):
    """ Widget corresponding to a fork """
    def __init__(self, *args, **kwargs):
        self.background_acq = kwargs.pop('background_acq')
        super(ForkWidget, self).__init__(*args, **kwargs)

        self.pixmap_acq = QtGui.QPixmap(self.background_acq).scaled(
            self.orig_width, self.orig_height, Qt.KeepAspectRatio
        )
        self.pixmap_acq = self.pixmap_acq.transformed(
            QtGui.QTransform().rotate(self.angle + 180)
        )

        self.pixmap = self.pixmap.transformed(QtGui.QTransform().rotate(180))

        self.setPixmap(self.pixmap)

    def acquire(self):
        self.setPixmap(self.pixmap_acq)

    def release(self):
        self.setPixmap(self.pixmap)


class MainWindow(QtGui.QWidget):
    """ Main window placing all the necessary widgets """
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setGeometry(0, 0, 700, 700)
        self.setWindowTitle("Dining Philosophers")

        self.table = WidgetWithBackground(
            self, background='./assets/table.png', width=500, height=500)
        xoffset = 100
        yoffset = 100
        self.table.move(xoffset, yoffset)

        p_coords = [(250, 0), (488, 173), (397, 452), (103, 452), (12, 173)]
        f_coords = [(103, 48), (397, 48), (487, 327), (250, 500), (13, 327)]
        self.phils = []
        self.forks = []
        for i in range(5):
            phil = PhilWidget(
                self, background='./assets/philosopher.png',
                width=100, height=100, angle=i * 72)
            phil.move(p_coords[i][0] + xoffset, p_coords[i][1] + yoffset)
            self.phils.append(phil)

            fork = ForkWidget(
                self, background='./assets/fork-released.png',
                background_acq='./assets/fork-acquired.png',
                width=100, height=100, angle=i * 72)
            fork.move(f_coords[i][0] + xoffset, f_coords[i][1] + yoffset)
            self.forks.append(fork)

        self.show()

        # Timer to interrupt Qt event loop
        # and check for events in external queue
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.messenger)
        timer.start(100)

    def messenger(self):
        """Method processing the events in the external event queue"""
        while not msg_queue.empty():
            msg = msg_queue.get()
            if msg.item == 'fork':
                if msg.is_acquired:
                    self.forks[msg.ident].acquire()
                else:
                    self.forks[msg.ident].release()
            else:
                if msg.is_acquired:
                    self.phils[msg.ident].acquire()
                else:
                    self.phils[msg.ident].release()
