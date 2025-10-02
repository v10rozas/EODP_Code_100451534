from math import pi
from config.ismConfig import ismConfig
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.special import j1
from numpy.matlib import repmat
from common.io.readMat import writeMat
from common.plot.plotMat2D import plotMat2D
from scipy.interpolate import interp2d
from numpy.fft import fftshift, ifft2
import os

class mtf:
    """
    Class MTF. Collects the analytical modelling of the different contributions
    for the system MTF
    """
    def __init__(self, logger, outdir):
        self.ismConfig = ismConfig()
        self.logger = logger
        self.outdir = outdir

    def system_mtf(self, nlines, ncolumns, D, lambd, focal, pix_size,
                   kLF, wLF, kHF, wHF, defocus, ksmear, kmotion, directory, band):
        """
        System MTF
        :param nlines: Lines of the TOA
        :param ncolumns: Columns of the TOA
        :param D: Telescope diameter [m]
        :param lambd: central wavelength of the band [m]
        :param focal: focal length [m]
        :param pix_size: pixel size in meters [m]
        :param kLF: Empirical coefficient for the aberrations MTF for low-frequency wavefront errors [-]
        :param wLF: RMS of low-frequency wavefront errors [m]
        :param kHF: Empirical coefficient for the aberrations MTF for high-frequency wavefront errors [-]
        :param wHF: RMS of high-frequency wavefront errors [m]
        :param defocus: Defocus coefficient (defocus/(f/N)). 0-2 low defocusing
        :param ksmear: Amplitude of low-frequency component for the motion smear MTF in ALT [pixels]
        :param kmotion: Amplitude of high-frequency component for the motion smear MTF in ALT and ACT
        :param directory: output directory
        :return: mtf
        """

        self.logger.info("Calculation of the System MTF")

        # Calculate the 2D relative frequencies
        self.logger.debug("Calculation of 2D relative frequencies")
        fn2D, fr2D, fnAct, fnAlt = self.freq2d(nlines, ncolumns, D, lambd, focal, pix_size)

        # Diffraction MTF
        self.logger.debug("Calculation of the diffraction MTF")
        Hdiff = self.mtfDiffract(fr2D)

        # Defocus
        Hdefoc = self.mtfDefocus(fr2D, defocus, focal, D)

        # WFE Aberrations
        Hwfe = self.mtfWfeAberrations(fr2D, lambd, kLF, wLF, kHF, wHF)

        # Detector
        Hdet  = self. mtfDetector(fn2D)

        # Smearing MTF
        Hsmear = self.mtfSmearing(fnAlt, ncolumns, ksmear)

        # Motion blur MTF
        Hmotion = self.mtfMotion(fn2D, kmotion)

        # Calculate the System MTF
        self.logger.debug("Calculation of the Sysmtem MTF by multiplying the different contributors")
        Hsys = Hdiff * Hdefoc * Hwfe * Hdet * Hsmear * Hmotion

        # Plot cuts ACT/ALT of the MTF
        self.plotMtf(Hdiff, Hdefoc, Hwfe, Hdet, Hsmear, Hmotion, Hsys, nlines, ncolumns, fnAct, fnAlt, directory, band)


        return Hsys

    def freq2d(self, nlines, ncolumns, D, lambd, focal, w):
        """
        Calculate the relative frequencies 2D (for the diffraction MTF)
        :param nlines: Lines of the TOA
        :param ncolumns: Columns of the TOA
        :param D: Telescope diameter [m]
        :param lambd: central wavelength of the band [m]
        :param focal: focal length [m]
        :param w: pixel size in meters [m]
        :return fn2D: normalised frequencies 2D (f/(1/w))
        :return fr2D: relative frequencies 2D (f/(1/fc))
        :return fnAct: 1D normalised frequencies 2D ACT (f/(1/w))
        :return fnAlt: 1D normalised frequencies 2D ALT (f/(1/w))
        """
        #TODO
        # Section 7.1.3.19.1. 2D frequencies array
        fstepAlt = 1 / nlines / w
        fstepAct = 1 / ncolumns / w

        eps = 1e-10
        fAlt = np.arange(-1 / (2 * w), 1 / (2 * w) - eps, fstepAlt)
        fAct = np.arange(-1 / (2 * w), 1 / (2 * w) - eps, fstepAct)

        cut_off = D / (lambd * focal)

        frAlt = fAlt / cut_off
        frAct = fAct /  cut_off

        fnAlt = fAlt / (1 / w)
        fnAct = fAct / (1 / w)

        [frAltxx, frActxx] = np.meshgrid(frAlt, frAct, indexing='ij')
        fr2D = np.sqrt(frAltxx * frAltxx + frActxx * frActxx)

        [fnAltxx, fnActxx] = np.meshgrid(fnAlt, fnAct, indexing='ij')
        fn2D = np.sqrt(fnAltxx * fnAltxx + fnActxx * fnActxx)

        return fn2D, fr2D, fnAct, fnAlt

    def mtfDefocus(self, fr2D, defocus, focal, D):
        """
        Defocus MTF
        :param fr2D: 2D relative frequencies (f/fc), where fc is the optics cut-off frequency
        :param defocus: Defocus coefficient (defocus/(f/N)). 0-2 low defocusing
        :param focal: focal length [m]
        :param D: Telescope diameter [m]
        :return: Defocus MTF
        """
        #TODO
        x = math.pi * defocus * fr2D * (1 - fr2D)
        Hdefoc = (2 * j1(x)) / x
        return Hdefoc


    def mtfWfeAberrations(self, fr2D, lambd, kLF, wLF, kHF, wHF):
        """
        Wavefront Error Aberrations MTF
        :param fr2D: 2D relative frequencies (f/fc), where fc is the optics cut-off frequency
        :param lambd: central wavelength of the band [m]
        :param kLF: Empirical coefficient for the aberrations MTF for low-frequency wavefront errors [-]
        :param wLF: RMS of low-frequency wavefront errors [m]
        :param kHF: Empirical coefficient for the aberrations MTF for high-frequency wavefront errors [-]
        :param wHF: RMS of high-frequency wavefront errors [m]
        :return: WFE Aberrations MTF
        """
        #TODO
        Hwfe = np.exp((-fr2D) * (1 - fr2D) * ((kLF * ((wLF / lambd)**2)) + (kHF * ((wHF / lambd)**2))))
        return Hwfe

    def mtfDiffract(self, fr2D):
        """
        Optics Diffraction MTF
        :param fr2D: 2D relative frequencies (f/fc), where fc is the optics cut-off frequency
        :return: diffraction MTF
        """
        #TODO
        Hdiff = (2 / math.pi) * (np.arccos(fr2D) - (fr2D * np.sqrt(1 - (fr2D**2))))
        return Hdiff

    def mtfDetector(self, fn2D):
        """
        Detector MTF
        :param fnD: 2D normalised frequencies (f/(1/w))), where w is the pixel width
        :return: detector MTF
        """
        #TODO
        Hdet = np.abs(np.sinc(fn2D))
        return Hdet

    def mtfSmearing(self, fnAlt, ncolumns, ksmear):
        """
        Smearing MTF
        :param ncolumns: Size of the image ACT
        :param fnAlt: 1D normalised frequencies 2D ALT (f/(1/w))
        :param ksmear: Amplitude of low-frequency component for the motion smear MTF in ALT [pixels]
        :return: Smearing MTF
        """
        #TODO
        Hsmear_1D = np.sinc(ksmear * fnAlt)
        Hsmear = np.tile(Hsmear_1D[:, np.newaxis], (1, ncolumns))
        return Hsmear

    def mtfMotion(self, fn2D, kmotion):
        """
        Motion blur MTF
        :param fnD: 2D normalised frequencies (f/(1/w))), where w is the pixel width
        :param kmotion: Amplitude of high-frequency component for the motion smear MTF in ALT and ACT
        :return: detector MTF
        """
        #TODO
        Hmotion = np.sinc(kmotion * fn2D)
        return Hmotion

    def plotMtf(self, Hdiff, Hdefoc, Hwfe, Hdet, Hsmear, Hmotion, Hsys, nlines, ncolumns, fnAct, fnAlt, directory, band):
        """
        Plotting the system MTF and all of its contributors
        :param Hdiff: Diffraction MTF
        :param Hdefoc: Defocusing MTF
        :param Hwfe: Wavefront electronics MTF
        :param Hdet: Detector MTF
        :param Hsmear: Smearing MTF
        :param Hmotion: Motion blur MTF
        :param Hsys: System MTF
        :param nlines: Number of lines in the TOA
        :param ncolumns: Number of columns in the TOA
        :param fnAct: normalised frequencies in the ACT direction (f/(1/w))
        :param fnAlt: normalised frequencies in the ALT direction (f/(1/w))
        :param directory: output directory
        :param band: band
        :return: N/A
        """
        #TODO
        # --- ACT slice (corte central en ALT) ---
        center_alt = nlines // 2
        Hdiff_act = Hdiff[center_alt, :]
        Hdefoc_act = Hdefoc[center_alt, :]
        Hwfe_act = Hwfe[center_alt, :]
        Hdet_act = Hdet[center_alt, :]
        Hsmear_act = Hsmear[center_alt, :]
        Hmotion_act = Hmotion[center_alt, :]
        Hsys_act = Hsys[center_alt, :]

        # Filtrar frecuencias positivas en ACT
        mask_act = fnAct >= 0
        fnAct_pos = fnAct[mask_act]
        Hdiff_act = Hdiff_act[mask_act]
        Hdefoc_act = Hdefoc_act[mask_act]
        Hwfe_act = Hwfe_act[mask_act]
        Hdet_act = Hdet_act[mask_act]
        Hsmear_act = Hsmear_act[mask_act]
        Hmotion_act = Hmotion_act[mask_act]
        Hsys_act = Hsys_act[mask_act]

        # --- ALT slice (corte central en ACT) ---
        center_act = ncolumns // 2
        Hdiff_alt = Hdiff[:, center_act]
        Hdefoc_alt = Hdefoc[:, center_act]
        Hwfe_alt = Hwfe[:, center_act]
        Hdet_alt = Hdet[:, center_act]
        Hsmear_alt = Hsmear[:, center_act]
        Hmotion_alt = Hmotion[:, center_act]
        Hsys_alt = Hsys[:, center_act]

        # Filtrar frecuencias positivas en ALT
        mask_alt = fnAlt >= 0
        fnAlt_pos = fnAlt[mask_alt]
        Hdiff_alt = Hdiff_alt[mask_alt]
        Hdefoc_alt = Hdefoc_alt[mask_alt]
        Hwfe_alt = Hwfe_alt[mask_alt]
        Hdet_alt = Hdet_alt[mask_alt]
        Hsmear_alt = Hsmear_alt[mask_alt]
        Hmotion_alt = Hmotion_alt[mask_alt]
        Hsys_alt = Hsys_alt[mask_alt]

        # ---------- FIGURA ACT ----------
        plt.figure(figsize=(8, 6))
        plt.plot(fnAct_pos, Hdiff_act, label="Diffraction MTF")
        plt.plot(fnAct_pos, Hdefoc_act, label="Defocus MTF")
        plt.plot(fnAct_pos, Hwfe_act, label="WFE Aberrations MTF")
        plt.plot(fnAct_pos, Hdet_act, label="Detector MTF")
        plt.plot(fnAct_pos, Hsmear_act, label="Smearing MTF")
        plt.plot(fnAct_pos, Hmotion_act, label="Motion blur MTF")
        plt.plot(fnAct_pos, Hsys_act, 'k', linewidth=2, label="System MTF")
        plt.axvline(0.5, color='k', linestyle='--', label="f Nyquist")

        plt.xlabel("Spatial frequencies f/(1/w) [-]")
        plt.ylabel("MTF")
        plt.title("System MTF - slice ACT")
        plt.legend(loc="best")
        plt.grid(True)

        if not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(os.path.join(directory, f"System_MTF_ACT_{band}.png"), dpi=300)
        plt.close()

        # ---------- FIGURA ALT ----------
        plt.figure(figsize=(8, 6))
        plt.plot(fnAlt_pos, Hdiff_alt, label="Diffraction MTF")
        plt.plot(fnAlt_pos, Hdefoc_alt, label="Defocus MTF")
        plt.plot(fnAlt_pos, Hwfe_alt, label="WFE Aberrations MTF")
        plt.plot(fnAlt_pos, Hdet_alt, label="Detector MTF")
        plt.plot(fnAlt_pos, Hsmear_alt, label="Smearing MTF")
        plt.plot(fnAlt_pos, Hmotion_alt, label="Motion blur MTF")
        plt.plot(fnAlt_pos, Hsys_alt, 'k', linewidth=2, label="System MTF")
        plt.axvline(0.5, color='k', linestyle='--', label="f Nyquist")

        plt.xlabel("Spatial frequencies f/(1/w) [-]")
        plt.ylabel("MTF")
        plt.title("System MTF - slice ALT")
        plt.legend(loc="best")
        plt.grid(True)

        plt.savefig(os.path.join(directory, f"System_MTF_ALT_{band}.png"), dpi=300)
        plt.close()