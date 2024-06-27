import os
import cv2
import numpy as np
from PyQt5.QtCore import *

kernel = np.ones((5, 5), np.uint8)

class InvertThread(QThread):
    succeed_signal = pyqtSignal()
    fail_signal = pyqtSignal(str)

    def __init__(self, imageFilename, outputPath, normalInvert):
        QThread.__init__(self)
        self.imageFilename = imageFilename
        self.outputPath = outputPath

        self.img = None
        self.running = True
        self.normalInvert = normalInvert

    def __del__(self):
        try:
            self.wait()
        except RuntimeError:
            return

    def run(self):
        self.running = True

        img = cv2.imread(self.imageFilename)
        if img is None:
            self.fail_signal.emit("Unexpected error...")
            return

        # normal invert
        if self.normalInvert:
            inv_img = 255 - img
            invertType = "_standard_invert.png"

        # value invert
        else:
            hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            hsv_img[:, :, 2] = 255 - hsv_img[:, :, 2]
            inv_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
            invertType = "_value_invert.png"

        basename = '.'.join(os.path.basename(self.imageFilename).split('.')[:-1])
        self.outputFilename = os.path.join(self.outputPath, basename + invertType)

        if self.running:
            cv2.imwrite(self.outputFilename, inv_img)
            self.succeed_signal.emit()

    def stop(self):
        self.running = False
