import numpy as np
import math
from Utils import sampleToMS


class WindowCharacterization:

    def getMV(self, eegs, ch):
        MVE = []
        # gets the max-min voltaje of eeg and ms when it happened per channel
        for eeg in eegs:
            MV = []
            for i in ch:
                max = np.amax(eeg.channels[i].readings)
                imax = np.argmax(eeg.channels[i].readings)
                msmax = sampleToMS(imax, eeg.frequency, eeg.duration)
                min = np.amin(eeg.channels[i].readings)
                imin = np.argmin(eeg.channels[i].readings)
                msmin = sampleToMS(imin, eeg.frequency, eeg.duration)
                MV.append([[min, msmin], [max, msmax]])
            MVE.append(MV)
        return MVE

    def getMagFase(self, eegs, n, ch):
        MagFase = []
        for eeg in eegs:
            Mag = []
            Frequency = []
            Phase = []
            for i in ch:
                mag = []
                frequency = []
                phases = []
                for j in range(n):
                    mag.append(0)
                    frequency.append(0)
                    phases.append(0)
                fft = np.fft.rfft(eeg.channels[i].readings, len(eeg.channels[i].readings))
                # normalizing
                real = (fft.real * 2) / len(eeg.channels[i].readings)
                imag = (fft.imag * 2) / len(eeg.channels[i].readings)
                for v in range(len(fft)):
                    # getting the magnitude for each value of fft
                    magnitude = round(np.sqrt(real[v]**2 + imag[v]**2), 2)
                    # getting the phase for each value of fft
                    phase = np.arctan((imag[v] / real[v]))
                    numN = 0
                    for j in range(n):
                        if mag[j] != 0:
                            numN += 1
                    if numN < len(mag):
                        mag[numN] = magnitude
                        frequency[numN] = v
                        if math.isnan(phase):
                            phase = 0
                        phases[numN] = phase
                    else:
                        for j in range(n):
                            if magnitude > mag[j]:
                                mag[j] = magnitude
                                frequency[j] = v
                                if math.isnan(phase):
                                    phase = 0
                                phases[j] = phase
                Mag.append(mag)
                Frequency.append(frequency)
                Phase.append(phases)
            MagFase.append([Mag, Frequency, Phase])
        return MagFase

    def getAUC(self, eegs, ch):
        AUCE =[]
        for eeg in eegs:
            areas = []
            for i in ch:
                dx = 1
                area = np.trapz(eeg.channels[i].readings, dx=dx)
                areas.append(area)
            AUCE.append(areas)
        return AUCE