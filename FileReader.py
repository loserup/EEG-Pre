'''
FileReader can read the next EEG formats:
.mat
.gdf/.edf
.rec
.bci2000
.acq
.eeg
It returns a EEGData object.
'''
#lib imports
import os
import bioread
import h5py
import numpy as np
import pyedflib
import scipy.io as sio

#local imports
from EEGData import *

class FileReader:
    __error = False

    def hasError(self):
        return self.__error

    def setError(self, t):
        if t == 0:
            print("The file could not be opened.")
        elif t == 1:
            print("File not supported.")
        else:
            print("An Unknown error has occurred")
        self.__error = True

    def readFile(self, fileAddress):
        #restarting the error
        self.__error = False
        try:
            #opening the eeg file
            eegFile = open(fileAddress, 'r')
        except:
            self.setError(0)
            return None
        #extracting basic data of the eeg file
        fileName, fileExt = os.path.splitext(fileAddress)
        #reading the important data depending on the extension
        if fileExt == ".mat":
            eeg = self.readMAT(fileAddress)
        elif fileExt[2:] == "df":
            eeg = self.read_DF(fileAddress)
        elif fileExt == ".rec":
            eeg = self.readREC(eegFile)
        elif fileExt == ".bci2000":
            eeg = self.readBCI(eegFile)
        elif fileExt == ".acq":
            eeg = self.readACQ(eegFile)
        elif fileExt == ".eeg":
            eeg = self.readEEG(eegFile)
        else:
            self.setError(1)
            return None
        return eeg

    def readMAT(self, fileAddress):
        #TODO .mat is gay
        new = False
        try:
            matfile = sio.loadmat(fileAddress)
        except:
            try:
                matfile = h5py.File(fileAddress, 'r')
                new = True
            except:
                self.setError(1)
                return None
        if new:
            print(matfile.keys())
            eegDSet = matfile['EEG']
            channelinfo = eegDSet. get('chaninfo', default=None, getclass=False, getlink=False)
            data = channelinfo.items()
            print(sio.whosmat(fileAddress))
        return None
        #return EEGData(sData, channels, units, filtr, add)

    def read_DF(self, fileAddress):
        try:
            _dfFile = pyedflib.EdfReader(fileAddress)
            n = _dfFile.signals_in_file
            labels = _dfFile.getSignalLabels()
            signals = np.zeros((n, _dfFile.getNSamples()[0]))
            for i in np.arange(n):
                signals[i, :] = _dfFile.readSignal(i)
        except:
            self.setError(2)
            return None
        #getting how many samples per second
        frecuency = signals.shape[1]/_dfFile.datarecord_duration
        #getting if the signals where prefiltered
        try:
            filtr = _dfFile.getPrefilter()
        except:
            filtr = None
        return EEGData(frecuency, _dfFile.datarecord_duration, signals, filtr, None, labels)

    def readREC(self, eegFile):

        return None

    def readBCI(self, eegFile):

        return None

    def readACQ(self, fileAddress):
        try:
            acq = bioread.read_file(fileAddress)
        except:
            self.setError(2)
            return None
        return None

    def readEEG(self, eegFile):

        return None