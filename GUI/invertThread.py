# noinspection PyUnresolvedReferences
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import os, cv2, numpy as np

kernel = np.ones((5, 5), np.uint8)

class InvertThread(QThread):

    succeed_signal = pyqtSignal()
    fail_signal = pyqtSignal(str)

    def __init__(self, imageFilename, outputPath):
        QThread.__init__(self)
        self.imageFilename = imageFilename
        self.outputPath = outputPath

        self.img = None

        self.running = True

    def __del__(self):
        self.wait()

    def run(self):
        self.running = True

        img = cv2.imread(self.imageFilename)
        if img is None:
            self.fail_signal.emit("Unexpected error...")

        inv_img = 255 - img

        basename = '.'.join(os.path.basename(self.imageFilename).split('.')[:-1])
        self.outputFilename = os.path.join(self.outputPath, basename + '_inverted.png')

        if self.running:
            cv2.imwrite(self.outputFilename, inv_img)
            self.succeed_signal.emit()

    def stop(self):
        self.running = False