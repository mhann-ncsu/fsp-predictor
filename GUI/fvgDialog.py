from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import os, fnmatch

from fvgThread import FVGThread
from datetime import date, datetime

class FVGDialog(QDialog, QMainWindow):

    def __init__(self, parent=None):
        super(FVGDialog, self).__init__(parent)

        app_icon = QIcon()
        app_icon.addFile("static/images/vector_dm.jpg", QSize(128, 128))
        self.setWindowIcon(app_icon)

        self.createConfigGroup()
        self.createCommandGroup()
        self.createInputGroup()

        grid = QGridLayout()

        grid.addWidget(self.configGroup, 0, 0)
        grid.addWidget(self.commandGroup, 0, 1)
        grid.addWidget(self.inputGroup, 1, 0)

        self.setLayout(grid)

        self.setWindowTitle("Feature Vector Generator")
        self.resize(720, 480)

        self.outputPrefix = None
        self.PMAPath = None
        self.outputPath = None
        self.outputFiletype = '.csv' # default

        self.params = {} # base params list
        self.params['rotation'] = 1000
        self.params['traversal'] = 10
        self.params['passNum'] = 5
        self.params['passType'] = 'single'

    def createConfigGroup(self):
        self.configGroup = QGroupBox("Configuration")

        grid = QGridLayout()

        self.outputPrefixEdit = QLineEdit()
        self.outputPrefixEdit.setPlaceholderText(f"fv_{str(date.today())}")
        grid.addWidget(QLabel("Output prefix:"), 0, 0)
        grid.addWidget(self.outputPrefixEdit, 0, 1, 1, 2)
        self.outputPrefixEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # NOT READY YET
        # self.PMAPathEdit = QLineEdit()
        # self.loadPMAPathBtn = QPushButton('')
        # self.loadPMAPathBtn.setIcon(QIcon('static/images/folder.png'))
        # self.loadPMAPathBtn.setToolTip("Select the Particle Morphology Analysis file")
        # self.loadPMAPathBtn.setIconSize(QSize(12, 12))
        # self.loadPMAPathBtn.setAutoDefault(False)
        # self.loadPMAPathBtn.clicked.connect(self.loadPMAPathDialog)
        # grid.addWidget(QLabel('PMA file:'), 2, 0)
        # grid.addWidget(self.PMAPathEdit, 2, 1)
        # grid.addWidget(self.loadPMAPathBtn, 2, 2)

        self.outputPathEdit = QLineEdit()
        self.loadOutputPathBtn = QPushButton('')
        self.loadOutputPathBtn.setIcon(QIcon('static/images/folder.png'))
        self.loadOutputPathBtn.setIconSize(QSize(12, 12))
        self.loadOutputPathBtn.setAutoDefault(False)
        self.loadOutputPathBtn.clicked.connect(self.loadOutputPathDialog)
        grid.addWidget(QLabel('Output path:'), 3, 0)
        grid.addWidget(self.outputPathEdit, 3, 1)
        grid.addWidget(self.loadOutputPathBtn, 3, 2)

        self.csvBtn = QRadioButton(".csv")
        self.csvBtn.setToolTip("Convert to .xlsx filetype.")
        self.csvBtn.setChecked(True)
        self.csvBtn.clicked.connect(self.csvExport)
        grid.addWidget(self.csvBtn, 4, 0)

        self.xlsxBtn = QRadioButton(".xlsx")
        self.xlsxBtn.setToolTip("Export as .xlsx filetype")
        self.xlsxBtn.clicked.connect(self.xlsxExport)
        grid.addWidget(self.xlsxBtn, 4, 1)

        self.configGroup.setLayout(grid)

    def createCommandGroup(self):
        self.commandGroup = QGroupBox("Commands")

        vbox = QVBoxLayout()

        self.startBtn = QPushButton('Start')
        self.startBtn.setToolTip('Start feature collection.')
        self.startBtn.clicked.connect(self.start)
        vbox.addWidget(self.startBtn)

        self.stopBtn = QPushButton('Stop')
        self.stopBtn.setToolTip('Stop feature collection. Collected features would not be saved.')
        self.stopBtn.clicked.connect(self.stop)
        self.stopBtn.setEnabled(False)
        vbox.addWidget(self.stopBtn)

        self.closeBtn = QPushButton('Close')
        self.closeBtn.setToolTip('Close the window.')
        self.closeBtn.clicked.connect(self.close)
        vbox.addWidget(self.closeBtn)

        self.commandGroup.setLayout(vbox)

    def createInputGroup(self):
        self.inputGroup = QGroupBox("Processing Parameters")

        grid = QGridLayout()

        self.rotationParamEdit = QLineEdit()
        self.rotationParamEdit.setPlaceholderText("1000")
        grid.addWidget(QLabel("Tool rotation (RPM):"), 0, 0)
        grid.addWidget(self.rotationParamEdit, 0, 1)

        self.traverseParamEdit = QLineEdit()
        self.traverseParamEdit.setPlaceholderText("10")
        grid.addWidget(QLabel("Traversal rate (mm/min):"), 1, 0)
        grid.addWidget(self.traverseParamEdit, 1, 1)

        self.numPassesEdit = QLineEdit()
        self.numPassesEdit.setPlaceholderText("5")
        grid.addWidget(QLabel("Number of passes:"), 2, 0)
        grid.addWidget(self.numPassesEdit, 2, 1)

        self.passTypeEdit = QLineEdit()
        self.passTypeEdit.setPlaceholderText("single")
        grid.addWidget(QLabel("Pass type (single/double):"), 3, 0)
        grid.addWidget(self.passTypeEdit, 3, 1)

        self.inputGroup.setLayout(grid)

    def csvExport(self):
        print("csv export selected")
        self.outputFiletype = ".csv"

    def xlsxExport(self):
        print("xlsx export selected")
        self.outputFiletype = ".xlsx"

    # def loadPMAPathDialog(self):
    #     self.PMAPath = QFileDialog.getExistingDirectory(
    #         self,
    #         'Load PMA path',
    #         './'
    #     )
    #     self.PMAPathEdit.setText(self.PMAPath)

    def loadOutputPathDialog(self):
        self.outputPath = QFileDialog.getExistingDirectory(
            self,
            'Load output path',
            './'
        )
        self.outputPathEdit.setText(self.outputPath)

    def validate(self):
        # if self.PMAPath == '':
        #     return False, 'Error: Please specify the path to the images.'
        # if not os.path.isdir(self.PMAPath):
        #     return False, 'Error: The path to the images is not valid.'
        if self.outputPath == '':
            return False, 'Error: Please specify the path to save outputs.'
        if not os.path.isdir(self.outputPath):
            return False, 'Error: The path for output files is not valid.'
        if self.outputPrefix == '':
            return False, 'Error: Please specify a filename'

        return True, None

    def patternMatch(self, s):
        for p in self.filenamePatternS:
            if fnmatch.fnmatch(s, p):
                return True
        return False

    def start(self):
        self.running_mode_ui()

        self.outputPrefix = self.outputPrefixEdit.text()
        # self.PMAPath = self.PMAPathEdit.text()
        self.outputPath = self.outputPathEdit.text()

        # declaring parameters list from text inputs in the form field
        if self.rotationParamEdit.text() != '':
            self.params['rotation'] = int(self.rotationParamEdit.text())

        if self.traverseParamEdit.text() != '':
            self.params['traversal'] = int(self.traverseParamEdit.text())

        if self.numPassesEdit.text() != '':
            self.params['passNum'] = int(self.numPassesEdit.text())

        if self.passTypeEdit.text() != '':
            self.params['passType'] = self.passTypeEdit.text()

        ready, msg = self.validate()
        if not ready:
            QMessageBox.critical(self, 'Error!', msg, QMessageBox.Ok)
            self.waiting_mode_ui()
            return None

    # @Debugging
        # print('self.outputPrefix = ', self.outputPrefix)
        # print('self.PMAPath =', self.PMAPath)
        # print('self.outputPath = ', self.outputPath)

        self.outputFilename = os.path.join(self.outputPath, self.outputPrefix + self.outputFiletype)
        self.outputFilename = os.path.normpath(self.outputFilename)

        self.fvgThread = FVGThread(self.outputFilename, self.params)
        self.fvgThread.complete_signal.connect(self.completed)
        self.fvgThread.start()

    def stop(self):
        self.fvgThread.stop()
        self.fvgThread.quit()
        self.waiting_mode_ui()

    def completed(self):
        QMessageBox.information(self, "Success.", "Feature vector generation completed.", QMessageBox.Ok)
        self.waiting_mode_ui()

    def running_mode_ui(self):
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.startBtn.update()
        self.stopBtn.update()

    def waiting_mode_ui(self):
        self.stopBtn.setEnabled(False)
        self.startBtn.setEnabled(True)
        self.stopBtn.update()
        self.startBtn.update()
