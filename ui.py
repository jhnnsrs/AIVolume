import random

import sys
from PyQt5 import Qt, QtCore

import h5py
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QApplication, QPushButton, QFileDialog, QTextEdit, QLineEdit, \
    QMessageBox, QGroupBox, QGridLayout, QLabel, QHBoxLayout, QMainWindow, QDockWidget
from matplotlib import lines
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector

import logic
from elements import AreaROI
from settings import Global


class ImageWindow(QMainWindow):
    def __init__(self):
        super(ImageWindow, self).__init__()
        self.ais = None
        self.h5file = None
        self.data = None
        self.setWindowTitle(Global.windowtitle)
        Global.imageWindow = self

        self.fig, self.axes = plt.subplots(3,sharex=False)
        self.canvas = FigureCanvas(self.fig)

        self.roidock = QDockWidget("Settings", self)

        self.span = SpanSelector(self.axes[2], self.onselect, 'horizontal', useblit=True,
                            rectprops=dict(alpha=0.5, facecolor='red'))

        self.setUI()

    def updateUI(self):
        self.setWindowTitle(Global.filepath)

        self.flagsText.setText(self.ais.flags)
        self.fileEdit.setText(Global.filepath.split("/")[-1])
        self.indexEdit.setText(str(self.ais.index))

        self.sobelx = logic.getSobel(self.ais.image, self.ais.b4channel)
        self.linelist = logic.getLineListSobel(self.sobelx)

        self.axes[0].set_ylim(0, self.sobelx.shape[0])
        self.axes[0].set_xlim(0, self.sobelx.shape[1])
        self.axes[0].imshow(self.ais.image)

        self.axes[1].set_ylim(0, self.sobelx.shape[0])
        self.axes[1].set_xlim(0, self.sobelx.shape[1])
        self.axes[1].imshow(self.sobelx)

        self.axes[2].clear()
        self.axes[2].set_ylim(0, self.sobelx.shape[0])
        self.axes[2].set_xlim(0, self.sobelx.shape[1])
        self.axes[2].imshow(self.ais.image)

        for index, element in enumerate(self.linelist):
            line = lines.Line2D([element[0][0], element[1][0]], [element[0][1], element[1][1]], color='b', alpha=0.6)
            self.axes[2].add_line(line)



        self.canvas.draw()
        self.show()

    def setRoi(self):

        self.ais.linelist = self.linelist
        self.ais.sobel = self.sobelx

    def instantiateFiles(self):
        self.aish5list = logic.getAIS(Global.filepath)
        random.shuffle(self.aish5list)
        self.newinstance()

    def newinstance(self):
        if len(self.aish5list) >= 1:
            self.ais, self.h5file = self.aish5list.pop()
            print("HFile", self.h5file, " ROI: ", self.ais.index)
            self.updateUI()
        else:
            QMessageBox.about(self, "All Done", "Every single file is already evaluated. YEAAHHHH")
            self.openDir()


    def setUI(self):

        self.setCentralWidget(self.canvas)

        self.settings = QWidget()
        self.settingsLayout = QVBoxLayout()


        self.settingBox = QGroupBox("Roi-Meta")
        self.settingLayout  = QGridLayout()


        self.indexLabel = QLabel("Roi")
        self.indexEdit = QLineEdit()
        self.indexEdit.setDisabled(True)
        self.settingLayout.addWidget(self.indexLabel, 1, 0)
        self.settingLayout.addWidget(self.indexEdit, 1, 1)

        self.fileLabel = QLabel("File")
        self.fileEdit = QLineEdit()
        self.fileEdit.setDisabled(True)
        self.settingLayout.addWidget(self.fileLabel, 0, 0)
        self.settingLayout.addWidget(self.fileEdit, 0, 1)

        self.volumeLabel = QLabel("Volume")
        self.volumeEdit = QLineEdit()
        self.volumeEdit.setDisabled(True)
        self.settingLayout.addWidget(self.volumeLabel,2,0)
        self.settingLayout.addWidget(self.volumeEdit,2,1)

        self.diameterLabel = QLabel("Diameter")
        self.diameterEdit = QLineEdit()
        self.diameterEdit.setDisabled(True)
        self.settingLayout.addWidget(self.diameterLabel, 3, 0)
        self.settingLayout.addWidget(self.diameterEdit , 3, 1)


        self.settingBox.setLayout(self.settingLayout)

        self.settingsLayout.addWidget(self.settingBox)

        self.fileBox = QGroupBox("Files")
        self.filesLayout = QGridLayout()

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.saveROI)
        self.filesLayout.addWidget(self.saveButton,0,0)

        self.calculateButton = QPushButton("Calculate")
        self.calculateButton.clicked.connect(self.calculate)
        self.filesLayout.addWidget(self.calculateButton, 0, 0)

        self.changefilebutton = QPushButton('Change File')
        self.changefilebutton.clicked.connect(self.changeFile)
        self.filesLayout.addWidget(self.changefilebutton, 0, 1)

        self.calculateandsavebutton = QPushButton('Calculate and Save')
        self.calculateandsavebutton.clicked.connect(self.calculateandSave)
        self.filesLayout.addWidget(self.calculateandsavebutton,1,0)
        # set button to call somefunction() when clicked

        self.flagsBox = QGroupBox("Flags")
        self.flagsLayout = QVBoxLayout()
        self.flagsText = QLineEdit()
        self.flagsLayout.addWidget(self.flagsText)
        self.flagsBox.setLayout(self.flagsLayout)
        self.settingsLayout.addWidget(self.flagsBox)

        self.fileBox.setLayout(self.filesLayout)
        self.settingsLayout.addWidget(self.fileBox)
        self.settingsLayout.addStretch()


        self.filebutton = QPushButton("Choose Directory", self)
        self.filebutton.clicked.connect(self.openDir)

        self.settingsLayout.addWidget(self.filebutton)

        self.settings.setLayout(self.settingsLayout)
        self.roidock.setWidget(self.settings)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,self.roidock)
        self.show()

    def saveROI(self):

        with h5py.File(self.h5file, "a") as f:
            print("Data/"+self.ais.key+"/Physical")
            nana = f["Data/"+self.ais.key+"/Physical"].attrs["Diameter"] = self.ais.diameter
            soso = f["Data/"+self.ais.key+"/Physical"].attrs["Volume"] = self.ais.volume

        return 0


    def quit(self):
        pass

    def openDir(self):
        # this is called when button1 is clicked
        # put directory specific tasks here
        # examples:
        ddir = QFileDialog.getExistingDirectory(self, "Get Dir Path")
        print(ddir)
        # ddir is a QString containing the path to the directory you selected
        if ddir != "":
            Global.filepath = ddir
            self.instantiateFiles()


        # lets get a list of files from the directory:

    def calculate(self):
        self.startParsing()

    def calculateandSave(self):
        self.calculate()
        self.saveROI()

    def startParsing(self):
        self.setRoi()
        self.ais.diameter, self.ais.volume = logic.calculateDiameterAndVolume(self.ais)

        self.volumeEdit.setText(str(self.ais.volume) + " µm")
        self.diameterEdit.setText(str(self.ais.diameter) + " µm")

    def changeFile(self,**kwargs):
        self.linelist = []
        self.newinstance()


    def onselect(self, xmin, xmax):
        print( xmin, xmax)
        self.ais.sections.append([xmin,xmax])



h_excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    h_excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


if __name__ == '__main__':

    app = QApplication(sys.argv)

    image = ImageWindow()

    image.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
