import numpy as np
import os
import pandas as pd
from PyQt5.QtCore import *
import xlsxwriter

class FVGThread(QThread):
    complete_signal = pyqtSignal()

    def __init__(self, outputFilename, params):
        QThread.__init__(self)
        self.running = True

        self.outputFilename = outputFilename
        self.params = params

    def __del__(self):
        try:
            self.wait()
        except RuntimeError:
            return

    def run(self):
        self.running = True

        paramsList = []
        valuesList = []
        for i in self.params.keys():
            paramsList.append(i)
            valuesList.append(self.params[i])
        d = {'Parameters': paramsList, 'Values': valuesList}
        df = pd.DataFrame(data=d)

        if self.running:
            try:
                if self.outputFilename.split('.')[-1] == 'csv':
                    # df.to_csv(self.outputFilename)
                    print(rf'File: {self.outputFilename}'.replace('\\', '/'))
                if self.outputFilename.split('.')[-1] == 'xlsx':
                    print(rf'File: {self.outputFilename}'.replace('\\', '/'))
                    df.to_excel(self.outputFilename, sheet_name='Sheet1', index=False, engine='xlsxwriter')
            except OSError:
                print("Didn't export, file is open in another program.")
            self.complete_signal.emit()

    def stop(self):
        self.running = False
