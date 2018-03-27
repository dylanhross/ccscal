"""
"""


from CcsCal import globals


from os.path import split, splitext
from numpy import amax, sum, array, exp
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter


class GaussFit:

    def __init__(self, raw_data, smooth=False, gen_fig=True):
        """
GaussFit.__init__

Initializes a GaussFit object used for fitting a dtbin vs. intensity spectrum with a gaussian
function to determine an accurate drift time

Input(s):
    raw_data    - the object containing the raw data (RawData)
    [smooth     - use Savitsky-Golay filter to remove high frequency variation from the data
                    optional, default=True]
    [gen_fig    - whether to generate the gaussian fit figure. optional, default = True]
"""
        # generate the initial parameters
        self.initparams = (amax(raw_data.dtBinAndIntensity[1]),
                           sum(raw_data.dtBinAndIntensity[0] *
                                raw_data.dtBinAndIntensity[1]) /
                                sum(raw_data.dtBinAndIntensity[1]),
                           globals.INIT_GAUSS_SIGMA)
        # set fit failed flag
        fitFailed = False
        # make internal copies of the specified mass and data filename
        self.mass = raw_data.specifiedMass
        self.filename = raw_data.ppFileName
        # fit the distribution on raw_data
        # perform smoothing of raw data using Savitsky-Golay filter
        self.smooth = smooth
        if self.smooth:
            raw_data.dtBinAndIntensity[1] = savgol_filter(raw_data.dtBinAndIntensity[1],
                                                            globals.SG_SMOOTH_WINDOW,
                                                            globals.SG_SMOOTH_ORDER)
        # fit the data
        self.doFit(raw_data)
        if not fitFailed:
            self.opt_mean = self.optparams[1]
        # create an array with the raw dtbin and intensity values
        # and fitted intensity values
        self.rawandfitdata = array([raw_data.dtBinAndIntensity[0],
                                            raw_data.dtBinAndIntensity[1],
                                            raw_data.dtBinAndIntensity[1]])
        self.rawandfitdata[2] = self.gaussFunc(raw_data.dtBinAndIntensity[0],
                                                self.optparams[0],
                                                self.optparams[1],
                                                self.optparams[2])
        # generate a figure of the gaussian fit if requested
        if gen_fig:
            self.saveGaussFitFig(self.filename, raw_data)

    def gaussFunc(self,x, A, mu, sigma):
        """
GaussFit.gaussFunc

Gaussian function of variable x with parameters for amplitude, mu, and sigma

Input(s):
    x                   - dtbin (float)
    A                   - Gaussian amplitude parameter (float)
    mu                  - Gaussian mu parameter (float)
    sigma               - Gaussian sigma parameter (float)

Returns:
                        - intensity (float)
"""
        return A*exp(-(x-mu)**2/(2.*sigma**2))

    def doFit(self, raw_data):
        """
GaussFit.doFit

Fits dt histogram with Gaussian function using curve_fit from scipy.optimize. A
try/except clause is used to catch an exception that arises when a sufficiently
good fit is not reached within a maximum number of optimization steps,
specifically within 1000 steps. Stores the optimized mu parameter for easy
reference by other objects:
    GaussFit.opt_mean       - optimized mean dtbin (float)

Input(s):
    raw_data                - object containing the dt distribution to be fit with
                                Gaussian function (GetData)
"""
        try:
            self.optparams,self.covar = curve_fit(self.gaussFunc,
                                                    raw_data.dtBinAndIntensity[0],
                                                    raw_data.dtBinAndIntensity[1],
                                                    p0=self.initparams,
                                                    maxfev=globals.CURVE_FIT_MAXFEV)
        except RuntimeError:
            # if fit was not achieved..
            self.fit_failed = True
            self.opt_mean = self.initparams[1]
            self.optparams = self.initparams
            print("failed to fit gaussian for mass", self.mass, "in", self.filename)

    def saveGaussFitFig(self, figure_file_name, raw_data):
        """
GaussFit.saveGaussFitFig

Outputs a Figure showing the CCS calibration curve fitted to the CCS
calibration data

Input(s):
    figure_file_name        - choose a filename to save the figure under (string)
    raw_data                - object containing the dt distribution to be fit with
                                Gaussian function (RawData)
"""
        if self.smooth:
            d_label = "raw data\n(smoothed)"
        else:
            d_label = "raw data"
        plt.plot(self.rawandfitdata[0],
                self.rawandfitdata[1],
                color='blue',
                ls='--',
                marker='o',
                ms=5,
                mec='blue',
                mfc='blue',
                label=d_label)
        plt.plot(self.rawandfitdata[0],
                self.rawandfitdata[2],
                color='black',
                ls='-',
                label="gaussian fit")
        plt.legend(loc="best")
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        plt.xlabel("dt bin")
        plt.ylabel("intensity")
        title = split(splitext(figure_file_name)[0])[1] + "\nmass: " + str(self.mass)
        plt.title(title)
        fname = splitext(figure_file_name)[0] + "_mass-" + str(int(self.mass)) + ".png"
        plt.savefig(fname, bbox_inches='tight', dpi=500)
        plt.close()

    def getDriftTime(self, dtbin_to_dt=globals.DEFAULT_DTBIN_TO_DT):
        """
GaussFit.getDriftTime

returns the fitted drift time converted from drift time bins to milliseconds

Input(s):
    [dtbin_to_dt    - conversion factor for converting dtbin to dt
                        optional, default = globals.DEFAULT_DTBIN_TO_DT]
"""
        return self.opt_mean * dtbin_to_dt
