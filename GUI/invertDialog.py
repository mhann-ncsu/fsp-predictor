from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import os

from invertThread import InvertThread

class InvertDialog(QDialog, QMainWindow):

    def __init__(self, parent=None):
        super(InvertDialog, self).__init__(parent)

        app_icon = QIcon()
        app_icon.addFile("static/images/ncsu_mse_standard_invert.png", QSize(128, 128))
        self.setWindowIcon(app_icon)

        self.createConfigGroup()
        self.createCommandGroup()
        self.createOptionsGroup()

        grid = QGridLayout()

        grid.addWidget(self.configGroup, 0, 0)
        grid.addWidget(self.commandGroup, 1, 0)
        grid.addWidget(self.optionsGroup, 2, 0)

        grid.setRowStretch(0, 10)
        grid.setRowStretch(1, 10)
        grid.setRowStretch(2, 10)

        self.setLayout(grid)

        self.setWindowTitle("Image Inversion")
        self.resize(800, 600)

        self.imageFilename = None
        self.outputPath = None
        self.normalInvert = True

    def createConfigGroup(self):
        self.configGroup = QGroupBox("Configuration")

        grid = QGridLayout()

        self.imageFilenameEdit = QLineEdit()
        self.loadImageFilenameBtn = QPushButton('')
        self.loadImageFilenameBtn.setIcon(QIcon("static/images/folder.png"))
        self.loadImageFilenameBtn.setIconSize(QSize(12, 12))
        self.loadImageFilenameBtn.setAutoDefault(False)
        self.loadImageFilenameBtn.clicked.connect(self.loadImageFilenameDialog)
        grid.addWidget(QLabel("Image filename"), 0, 0)
        grid.addWidget(self.imageFilenameEdit, 0, 1)
        grid.addWidget(self.loadImageFilenameBtn, 0, 2)

        self.outputPathEdit = QLineEdit()
        self.loadOutputPathBtn = QPushButton("")
        self.loadOutputPathBtn.setIcon(QIcon("static/images/folder.png"))
        self.loadOutputPathBtn.setIconSize(QSize(12, 12))
        self.loadOutputPathBtn.setAutoDefault(False)
        self.loadOutputPathBtn.clicked.connect(self.loadOutputPathDialog)
        grid.addWidget(QLabel("Output path"), 1, 0)
        grid.addWidget(self.outputPathEdit, 1, 1)
        grid.addWidget(self.loadOutputPathBtn, 1, 2)

        grid.setColumnStretch(0, 10)
        grid.setColumnStretch(1, 20)
        grid.setColumnStretch(2, 2)

        self.configGroup.setLayout(grid)

    def createCommandGroup(self):
        self.commandGroup = QGroupBox("Commands")

        vbox = QVBoxLayout()

        self.startBtn = QPushButton("Invert")
        self.startBtn.setToolTip("Invert the image")
        self.startBtn.clicked.connect(self.start)
        vbox.addWidget(self.startBtn)

        self.stopBtn = QPushButton("Stop")
        self.stopBtn.setToolTip("Stop image inversion")
        self.stopBtn.clicked.connect(self.stop)
        self.stopBtn.setEnabled(False)
        vbox.addWidget(self.stopBtn)

        self.closeBtn = QPushButton("Close")
        self.closeBtn.setToolTip("Close the window.")
        self.closeBtn.clicked.connect(self.close)
        vbox.addWidget(self.closeBtn)

        vbox.addStretch(1)

        self.commandGroup.setLayout(vbox)

    def createOptionsGroup(self):
        self.optionsGroup = QGroupBox("Options")

        hbox = QHBoxLayout()

        self.niRB = QRadioButton("Standard")
        self.niRB.setToolTip("Standard image inversion.")
        self.niRB.setChecked(True)
        self.niRB.toggled.connect(self.normalInvertClicked) # implement properly
        hbox.addWidget(self.niRB)

        self.viRB = QRadioButton("Value Invert")
        self.viRB.setToolTip("Inverts value component, color remains the same but brightness is affected.")
        self.viRB.toggled.connect(self.valueInvertClicked)
        hbox.addWidget(self.viRB)

        self.optionsGroup.setLayout(hbox)

    def loadImageFilenameDialog(self):
        self.imageFilename, _ = QFileDialog.getOpenFileName(
            self,
            'Load image filename',
            './'
        )
        self.imageFilenameEdit.setText(self.imageFilename)

    def loadOutputPathDialog(self):
        self.outputPath = QFileDialog.getExistingDirectory(
            self,
            'Load output path',
            './'
        )
        self.outputPathEdit.setText(self.outputPath)

    def normalInvertClicked(self, s):
        if s:
            self.normalInvert = True
            print("normal invert")

    def valueInvertClicked(self, s):
        if s:
            self.normalInvert = False
            print("value invert")
            # self.signals.value_invert_signal.emit()

    def start(self):
        self.running_mode_ui()

        self.imageFilename = self.imageFilenameEdit.text()
        self.outputPath = self.outputPathEdit.text()

        if not os.path.isfile(self.imageFilename):
            self.critical_msg('The image filename is invalid.')
            self.waiting_mode_ui()
            return None
        if not os.path.isdir(self.outputPath):
            self.critical_msg('The output path is invalid.')
            self.waiting_mode_ui()
            return None

        self.invertThread = InvertThread(self.imageFilename, self.outputPath, self.normalInvert)
        self.invertThread.succeed_signal.connect(self.invert_succeed)
        self.invertThread.fail_signal.connect(self.invert_fail)
        self.invertThread.start()

    def stop(self):
        self.invertThread.stop()
        self.invertThread.quit()
        self.waiting_mode_ui()

    def critical_msg(self, s):
        QMessageBox.critical(self, 'Error!', s, QMessageBox.Ok)

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

    def invert_succeed(self):
        QMessageBox.information(self, 'Completed!', 'Inverted image saved to {:s}.'.format(self.outputPath),
                                QMessageBox.Ok)
        self.waiting_mode_ui()

    def invert_fail(self, s):
        QMessageBox.critical(self, 'Error!', s, QMessageBox.Ok)

