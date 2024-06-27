import os
import pandas as pd
from PyQt5.QtCore import pyqtSignal, QThread

class FVGThread(QThread):
    complete_signal = pyqtSignal()

    def __init__(self, filenames, outputFilename):
        QThread.__init__(self)
        self.filenames = filenames
        self.outputFilename = outputFilename
        self.running = True

    def __del__(self):
        self.wait()

    def run(self):
        self.running = True

        if self.running:
            self.save_features()
            self.complete_signal.emit()


    def stop(self):
        self.running = False