import h5py
import matplotlib.pyplot as plt
import numpy as np
import random
import copy
import os
from os.path import join

from settings import Global
from elements import AreaROI

def getAIS(mypath):

    aish5list = []
    h5filelist = []
    for root, subdirs, files in os.walk(mypath):
        h5file = [join(root, f) for f in files if f.endswith(".h5")]
        h5filelist += h5file

    for h5file in h5filelist:
        if h5py.is_hdf5(h5file):
            with h5py.File(h5file, "r") as lala:

                try:
                    rois = [key for key in lala["Data"].keys()]
                    for roi in rois:
                        try:
                            nana = lala["Data/" + roi + "/Physical"].attrs["Diameter"]
                            print("FILE ", h5file, " already has a Diameter. Skipping")
                        except KeyError as e:
                            print("FILE ", h5file, " has no Diameter. Taking into account")
                            newroi = AreaROI()
                            newroi.length = float(lala["Data/" + roi + "/Physical"].attrs["AISPhysicalLength"])
                            newroi.image = np.array(lala["Data/" + roi + "/Image"])
                            newroi.flags = str(lala["Data/" + roi].attrs["Flags"])
                            newroi.index = int(lala["Data/" + roi].attrs["index"])
                            newroi.voxelsize = lala.attrs["physicalsizex"]
                            newroi.key = roi
                            print(newroi.flags)
                            # should only add the ones that are not already set
                            aish5list.append([newroi,h5file])
                except KeyError as e:
                    print("File {0} doesnt hava data Object: {1}".format(h5file, e))
                    pass

        else:
            print("File " + h5file + " doesn't conform with h5 standards")
            pass


    return aish5list


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


def calculateDiameterAndVolume(roi: AreaROI):
    # in pixel right now

    linelengths = []
    for slice in roi.linelist:
        length = np.linalg.norm(slice[0]-slice[1])
        linelengths.append(length)

    lengthmeans = []
    for startx, starty in roi.sections:
        sectionmean = np.mean(linelengths[int(startx):int(starty)])
        lengthmeans.append(sectionmean)

    diameter = np.mean(lengthmeans) * roi.voxelsize
    volume = np.math.pi * diameter ** 2 * roi.length
    print("Volume: ",volume)
    print("Diameter: ",diameter)
    return diameter, volume
