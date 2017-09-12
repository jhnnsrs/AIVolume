import matplotlib.pyplot as plt
import numpy as np
import random
import os
from os.path import join

from settings import Global
from elements import AreaROI, AreaData


def getAIS(mypath) :
    jpglist = []
    mypath = "Tests"
    for root, subdirs, files in os.walk(mypath):
        jpgfiles= [join(root, f) for f in files if f.endswith(".jpg")]
        jpglist += jpgfiles

    jpgs = []
    for path in jpglist:
        jpgs.append(plt.imread(path))

    return jpgs


def getSobel(image,b4channel=Global.b4channel):
    import cv2

    cvimage = image[:, :, b4channel]
    blured = cv2.GaussianBlur(cvimage, (3, 3), 3)
    sobelx = cv2.Canny(blured, 100, 200)

    return sobelx

def getLineListSobel(sobelx):

    firstover = np.argmax(sobelx, axis=0)
    lastover = sobelx.shape[0] - np.argmax(np.flip(sobelx, axis=0), axis=0)

    linelist = []
    for index, (ystart, yend) in enumerate(zip(firstover, lastover)):
        linelist.append([np.array([index, ystart]), np.array([index, yend])])

    return linelist


def calculateVolume(roi: AreaROI):
    # in pixel right now

    linelengths = []
    for slice in roi.linelist:
        length = np.linalg.norm(slice[0]-slice[1])
        linelengths.append(length)

    lengthmeans = []
    for startx, starty in roi.sections:
        sectionmean = np.mean(linelengths[int(startx):int(starty)])
        print(sectionmean)
        lengthmeans.append(sectionmean)

    volume = np.math.pi * np.mean(lengthmeans)**2 * roi.length
    print(volume)
    return volume
