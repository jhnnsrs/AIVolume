import random

import sys
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QApplication, QPushButton
from matplotlib import lines
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector

import logic
from elements import AreaROI, AreaData
from settings import Global


class ImageWindow(QWidget):
    def __init__(self):
        super(ImageWindow, self).__init__()
        self.data = None
        self.setWindowTitle("BioImageFile")
        Global.imageWindow = self
        self.layout = QVBoxLayout(self)

        self.fig, self.axes = plt.subplots(3,sharex=False)
        self.canvas = FigureCanvas(self.fig)

        self.span = SpanSelector(self.axes[2], self.onselect, 'horizontal', useblit=True,
                            rectprops=dict(alpha=0.5, facecolor='red'))

        self.setUI()
        self.updateUI()

    def updateUI(self):
        self.setWindowTitle(Global.filepath)

        self.jpglist = logic.getAIS(Global.filepath)
        self.jpg = random.choice(self.jpglist)

        self.sobelx = logic.getSobel(self.jpg, Global.b4channel)
        self.linelist = logic.getLineListSobel(self.sobelx)

        self.axes[0].set_ylim(0, self.sobelx.shape[0])
        self.axes[0].set_xlim(0, self.sobelx.shape[1])
        self.axes[0].imshow(self.jpg)

        self.axes[1].set_ylim(0, self.sobelx.shape[0])
        self.axes[1].set_xlim(0, self.sobelx.shape[1])
        self.axes[1].imshow(self.sobelx)

        self.axes[2].clear()
        self.axes[2].set_ylim(0, self.sobelx.shape[0])
        self.axes[2].set_xlim(0, self.sobelx.shape[1])
        self.axes[2].imshow(self.jpg)

        for index, element in enumerate(self.linelist):
            line = lines.Line2D([element[0][0], element[1][0]], [element[0][1], element[1][1]], color='b', alpha=0.6)
            self.axes[2].add_line(line)



        self.canvas.draw()

        self.show()
        self.spawnRoi()

    def spawnRoi(self):

        self.roi = AreaROI()
        self.roi.linelist = self.linelist
        self.roi.image = self.jpg
        self.roi.sobel = self.sobelx


    def setUI(self):
        self.layout.addWidget(self.canvas)



        self.changefilebutton = QPushButton('Change File')
        self.changefilebutton.clicked.connect(self.changeFile)
        self.layout.addWidget(self.changefilebutton)

        self.changefilebutton = QPushButton('Calculate')
        self.changefilebutton.clicked.connect(self.calculate)
        self.layout.addWidget(self.changefilebutton)

        self.setLayout(self.layout)
        self.show()

    def calculate(self):
        self.startParsing()

    def startParsing(self):
        self.data = logic.calculateVolume(self.roi)
        print(self.data)

    def changeFile(self,**kwargs):
        self.updateUI()

    def onselect(self, xmin, xmax):
        print( xmin, xmax)
        self.roi.sections.append([xmin,xmax])


if __name__ == '__main__':

    app = QApplication(sys.argv)

    image = ImageWindow()

    image.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
