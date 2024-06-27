from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import os, fnmatch

from fvgThread import FVGThread
from datetime import date, datetime

class FVGDialog(QDialog, QMainWindow):

    def __init__(self, parent=None):
        super(FVGDialog, self).__init__(parent)

        self.createConfigGroup()
        self.createCommandGroup()
        self.createInputGroup()

        app_icon = QIcon()
        app_icon.addFile("static/images/vector_dm.jpg", QSize(128, 128))
        self.setWindowIcon(app_icon)
        grid = QGridLayout()

        grid.addWidget(self.configGroup, 0, 0)
        grid.addWidget(self.commandGroup, 0, 1)
        grid.addWidget(self.inputGroup, 1, 0)

        self.setLayout(grid)

        self.setWindowTitle("Feature Vector Generator")
        self.resize(720, 480)

        self.outputPrefix = None
        self.filenamePattern = None
        self.filenamePatternS = None # not sure if I need this
        self.imagePath = None
        self.outputPath = None
        self.outputFiletype = None

        # might need more things here idk

    def createConfigGroup(self):
        self.configGroup = QGroupBox("Configuration")

        grid = QGridLayout()

        self.outputPrefixEdit = QLineEdit()
        self.outputPrefixEdit.setPlaceholderText(f"fv_{str(date.today())}")
        grid.addWidget(QLabel("Output prefix:"), 0, 0)
        grid.addWidget(self.outputPrefixEdit, 0, 1, 1, 2)
        # not sure what each number does...
        self.outputPrefixEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.filenamePatternEdit = QLineEdit()
        self.filenamePatternEdit.setPlaceholderText("*.csv *.xlsx")
        grid.addWidget(QLabel("Feature vector filename pattern:"), 1, 0)
        grid.addWidget(self.filenamePatternEdit, 1, 1, 1, 2)
        self.filenamePatternEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.imagePathEdit = QLineEdit()
        self.loadImagePathBtn = QPushButton('')
        self.loadImagePathBtn.setIcon(QIcon('static/images/folder.png'))
        self.loadImagePathBtn.setIconSize(QSize(12, 12))
        self.loadImagePathBtn.setAutoDefault(False)
        self.loadImagePathBtn.clicked.connect(self.loadImagePathDialog)
        grid.addWidget(QLabel('Image path'), 2, 0)
        grid.addWidget(self.imagePathEdit, 2, 1)
        grid.addWidget(self.loadImagePathBtn, 2, 2)

        self.outputPathEdit = QLineEdit()
        self.loadOutputPathBtn = QPushButton('')
        self.loadOutputPathBtn.setIcon(QIcon('static/images/folder.png'))
        self.loadOutputPathBtn.setIconSize(QSize(12, 12))
        self.loadOutputPathBtn.setAutoDefault(False)
        self.loadOutputPathBtn.clicked.connect(self.loadOutputPathDialog)
        grid.addWidget(QLabel('Output path'), 3, 0)
        grid.addWidget(self.outputPathEdit, 3, 1)
        grid.addWidget(self.loadOutputPathBtn, 3, 2)

        self.csvBtn = QRadioButton(".csv")
        self.csvBtn.setToolTip("Convert to .xlsx filetype.")
        self.csvBtn.setChecked(True)
        self.csvBtn.clicked.connect(self.csvExport)  # implement this function
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

        self.rotationParam = QLineEdit()
        self.rotationParam.setPlaceholderText("ex. 1000")
        grid.addWidget(QLabel("Tool rotation (RPM)"), 0, 0)
        grid.addWidget(self.rotationParam, 0, 1)

        self.traverseParam = QLineEdit()
        self.traverseParam.setPlaceholderText("ex. 10")
        grid.addWidget(QLabel("Traversal rate (mm/min)"), 1, 0)
        grid.addWidget(self.traverseParam, 1, 1)

        self.numPasses = QLineEdit()
        self.numPasses.setPlaceholderText("ex. 3")
        grid.addWidget(QLabel("Number of passes"), 2, 0)
        grid.addWidget(self.numPasses, 2, 1)

        self.passType = QLineEdit()
        self.passType.setPlaceholderText("ex. double")
        grid.addWidget(QLabel("Pass type (single/double)"), 3, 0)
        grid.addWidget(self.passType, 3, 1)

        self.inputGroup.setLayout(grid)

    def csvExport(self):
        print("csv export selected")
        self.outputFiletype = ".csv"

    def xlsxExport(self):
        print("xlsx export selected")
        self.outputFiletype = ".xlsx"

    def loadImagePathDialog(self):
        self.imagePath = QFileDialog.getExistingDirectory(
            self,
            'Load image path',
            './'
        )
        self.imagePathEdit.setText(self.imagePath)

    def loadOutputPathDialog(self):
        self.outputPath = QFileDialog.getExistingDirectory(
            self,
            'Load output path',
            './'
        )
        self.outputPathEdit.setText(self.outputPath)

    def validate(self):
        if self.imagePath == '':
            return False, 'Error: Please specify the path to the images.'
        if not os.path.isdir(self.imagePath):
            return False, 'Error: The path to the images is not valid.'
        if self.outputPath == '':
            return False, 'Error: Please specify the path to save outputs.'
        if not os.path.isdir(self.outputPath):
            return False, 'Error: The path for output files is not valid.'

        if not (self.featuresActive[0] or self.featuresActive[1] or self.featuresActive[2] or self.featuresActive[3]):
            return False, 'Error: Feature set cannot be empty.'

        return True, None

    def patternMatch(self, s):
        for p in self.filenamePatternS:
            if fnmatch.fnmatch(s, p):
                return True
        return False

    def start(self):
        self.running_mode_ui()

        self.outputPrefix = self.outputPrefixEdit.text()
        self.filenamePattern = self.filenamePatternEdit.text()
        self.imagePath = self.imagePathEdit.text()
        self.outputPath = self.outputPathEdit.text()

        if self.outputPrefix == "":
            self.outputPrefix = "fv-" + str(date.today())
        if self.filenamePattern == "":
            self.filenamePattern = "*.csv *.xlsx"

        ready, msg = self.validate()
        if not ready:
            QMessageBox.critical(self, 'Error!', msg, QMessageBox.Ok)
            self.output(msg)
            self.waiting_mode_ui()
            return None
        self.output('Start generating feature vector.')

        self.filenamePatternS = self.filenamePattern.split(' ')
        print('self.outputPrefix = ', self.outputPrefix)
        print('self.filenamePattern = ', self.filenamePattern)
        print('self.filenamePatternS =', self.filenamePatternS)
        print('self.imagePath =', self.imagePath)
        print('self.outputPath =', self.outputPath)

        filenames = sorted([x for x in os.listdir(self.imagePath)
                            if self.patternMatch(x)])
        filenames = [os.path.join(self.imagePath, x) for x in filenames]

        outputFilename = self.outputPrefix + '_' + str(len(filenames)) + '_'
        outputFilename = os.path.join(self.outputPath, f"{outputFilename}{self.outputFiletype}") # this might not work

        self.fvThread = FVGThread(
            filenames,
            outputFilename
        )
        self.fvThread.complete_signal.connect(self.completed)
        self.fvThread.start()

    def stop(self):
        self.output('Thread stopped.')
        self.fvThread.stop()
        self.fvThread.quit()
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

