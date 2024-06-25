from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys

from invertDialog import InvertDialog
from fvgDialog import FVGDialog

class MainWindow(QWidget):

	def __init__(self, *args, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)
		self.setWindowTitle("Feature Extraction")
		self.setFixedSize(QSize(800, 600))
		self.createLeftGroup()
		self.createRightGroup()

		hbox = QHBoxLayout()
		hbox.addWidget(self.leftGroup)
		hbox.addWidget(self.rightGroup)

		self.setLayout(hbox)

	def createLeftGroup(self):
		self.leftGroup = QGroupBox('Start')

		invertBtn = QPushButton('Invert')
		invertBtn.setToolTip('Inverts image.')
		invertBtn.clicked.connect(self.openInvertDialog) # make sure to match these up

		pcBtn = QPushButton('Particle Counter')
		pcBtn.setToolTip('Counts the number of particles within a micrograph.')
		# pcBtn.clicked.connect(self.openPCDialog) # make sure to match these up
		pcBtn.setEnabled(False)

		fvgBtn = QPushButton('FVGen')
		fvgBtn.setToolTip('Generating feature vector.')
		fvgBtn.clicked.connect(self.openFVGDialog) # make sure to match these up

		vbox = QVBoxLayout()
		vbox.addWidget(invertBtn)
		vbox.addWidget(pcBtn)
		vbox.addWidget(fvgBtn)
		vbox.addStretch(2)

		self.leftGroup.setLayout(vbox)

	def createRightGroup(self):
		self.rightGroup = QGroupBox('About')

		aboutBtn = QPushButton('About')
		aboutBtn.setToolTip('Open about page in default browser.')
		aboutBtn.clicked.connect(self.openAboutPage)

		docBtn = QPushButton('Documentation')
		docBtn.setToolTip('Open documentation page in default browser.')
		docBtn.clicked.connect(self.openDocPage)

		quitBtn = QPushButton('&Quit')
		quitBtn.clicked.connect(self.close)

		versionLabel = QLabel('version 0.1')

		vbox = QVBoxLayout()
		vbox.addWidget(aboutBtn)
		vbox.addWidget(docBtn)
		vbox.addWidget(quitBtn)
		vbox.addWidget(versionLabel)
		vbox.addStretch(1)

		self.rightGroup.setLayout(vbox)

	def openInvertDialog(self):
		self.hide()
		self.id = InvertDialog()
		self.id.setModal(True)
		self.id.exec()
		self.show()

	# def openPCDialog(self):
	# 	self.hide()
	# 	self.sd = PCDialog()
	# 	self.sd.setModal(True)
	# 	self.sd.exec()
	# 	self.show()
	#
	def openFVGDialog(self):
		self.hide()
		self.fvgd = FVGDialog()
		self.fvgd.setModal(True)
		self.fvgd.exec()
		self.show()

	def openAboutPage(self):
		QDesktopServices.openUrl(QUrl(
			'https://wufeim.github.io/microstructure-characterization-II/',
			QUrl.TolerantMode
		))

	def openDocPage(self):
		QDesktopServices.openUrl(QUrl(
			'https://wufeim.github.io/microstructure-characterization-II/documentation.html',
			QUrl.TolerantMode
		))


if __name__ == '__main__':
	app = QApplication(sys.argv)
	app_icon = QIcon()
	app_icon.addFile('static/images/ncsu_mse.png', QSize(256,256))
	app.setWindowIcon(app_icon)
	window = MainWindow()
	window.show()  # Important!
	sys.exit(app.exec_())


