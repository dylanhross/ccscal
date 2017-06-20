from CcsCal import globals
from CcsCal.input.RawData import RawData
from CcsCal.processing.GaussFit import GaussFit


import numpy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
from scipy.optimize import curve_fit


class CcsCalibration():

    def __init__ (self,
                  data_file,\
                  cal_masses,\
                  cal_lit_ccs_vals,\
                  mass_window,\
                  edc=globals.DEFAULT_EDC,\
                  dtbin_to_dt=globals.DEFAULT_DTBIN_TO_DT):
        """
CcsCalibration -- Class

Makes use of a GaussFit object to extract the drift times for a list of
calibrant masses. Then, using a list of calibrant literature ccs values, a
ccs calibration curve is generated. Once the curve has been fit, the
CcsCalibration.getCalibratedCcs method can be used to get a calibrated ccs for a
given mass and drift time

Input(s):
    data_file               - name of raw data file (string)
    cal_masses              - calibrant m/z values (list)
    cal_lit_ccs             - calibrant literature ccs values (list)
    mass_window             - specify a mass window to extract values from (float)
    [optional edc           - edc delay coefficient (float) [default = globals.DEFAULT_EDC]
    [optional] dtbin_to_dt  - specify a different dtbin equivalent to use other than
                                the default (float) [default = globals.DEFAULT_DTBIN_TO_DT]
"""
        # store some calculation constants
        self.edc = edc
        self.n2_mass = globals.N2_MASS
        self.he_mass = globals.HE_MASS
        # maximum iterations for curve fitting
        self.max_fev = globals.CURVE_FIT_MAXFEV
        # make an array with calibrant masses
        self.calMasses = numpy.array(cal_masses)
        # make an array with calibrant lit ccs values
        self.calLitCcs = numpy.array(cal_lit_ccs_vals)
        # make an array with calibrant drift times
        self.calDriftTimes = numpy.zeros([len(self.calMasses)])
        for n in range(len(self.calMasses)):
            self.calDriftTimes[n - 1] = GaussFit(RawData(data_file, \
                                                 self.calMasses[n - 1], \
                                                 mass_window)).getDriftTime()
        # make an array with corrected drift time
        self.correctedDt = self.correctedDriftTime(self.calDriftTimes, self.calMasses)
        # make an array with corrected lit ccs
        self.correctedLitCcs = self.calLitCcs * numpy.sqrt(self.reducedMass(self.calMasses))
        # Optimized parameters A, t0, B
        self.optparams = [globals.INIT_A, globals.INIT_T0, globals.INIT_B]
        #perform the calibration
        self.fitCalCurve()
        # make an array with calibrant calculated ccs
        self.calCalcCcs = self.getCalibratedCcs(self.calMasses, self.calDriftTimes)


    def reducedMass(self, mass, mode='N2'):
        """
CcsCalibration.reducedMass

Calculates reduced mass of an ion using the mass of nitrogen

Input(s):
    mass          - the m/z to use for the calculation (float)
    [mode]         - calculate reduced mass for N2 or He (str, optional default='n2')

Returns:
                            - reduced mass (float)
"""
        if mode == 'N2':
            return (mass * self.n2_mass) / (mass + self.n2_mass)
        elif mode == 'He':
            return (mass * self.he_mass) / (mass + self.he_mass)
        else:
            raise ValueError('CcsCalibration: reducedMass: error, mode must be either "N2" or "He"')


    def correctedDriftTime(self, dt, mass):
        """
CcsCalibration.correctedDriftTime

Calculates a drift time corrected for mass-dependent flight time

Input(s):
    dt                      - original uncorrected drift time (float)
    mass                    - the m/z to use for the calculation (float)

Returns:
                            - corrected drift time (float)
"""
        return dt - ((numpy.sqrt(mass) * self.edc) / 1000.0)


    def baseCalCurve (self, dt, A, t0, B):
        """
    CcsCalibration.baseCalCurve

    Basic power function for calibration curve

    Input(s):
        dt                      - drift time (float)
        A, t0, B                - curve parameters (float, float, float)

    Returns:
                                - ccs (float)
    """
        return (A  * (dt + t0)**B)


    def fitCalCurve(self):
        """
CcsCalibration.fitCalCurve

Performs least squares fit of the power equation CcsCalibration.baseCalCurve(...) to
the corrected literature ccs data and corrected drift time values

Input(s):
    none
"""
        self.fit_Failed = False
        try:
            self.optparams,self.covar=\
            curve_fit(\
            self.baseCalCurve,\
            self.correctedDt,\
            self.correctedLitCcs,\
            p0=self.optparams,\
            maxfev=self.max_fev)
        except RuntimeError:
            self.fit_failed = True
            print "CCS CALIBRATION CURVE FIT FAILED WITH RUNTIME ERROR..."


    def getCalibratedCcs(self, mass, dt):
        """
CcsCalibration.getCalibratedCcs

Uses the fitted parameters for the ccs calibration curve and returns a calibrated
ccs given a m/z and drift time

Input(s):
    mz                      - m/z (float)
    dt                      - drift time (float)

Returns:
                            - ccs (float)
"""
        if not self.fit_Failed:
            ### DEBUG
            #print "opt_params[0] / sqrt(reduced mass) =", (self.optparams[0] / numpy.sqrt(self.reducedMass(mass)))
            #print "corrected drift time =", self.correctedDriftTime(dt, mass)
            return (self.optparams[0] / numpy.sqrt(self.reducedMass(mass))) * ((self.correctedDriftTime(dt, mass) + self.optparams[1])**self.optparams[2])
        else:
            raise ValueError ("optimized fit parameters have not been generated,\
                              \nfitCalCurve() must be successfully run first!")


    def saveCalCurveFig(self, figure_file_name="cal_curve.png"):
        """
CcsCalibration.saveCalCurveFig

Outputs a Figure showing the CCS calibration curve fitted to the CCS
calibration data

Input(s):
    [optional] figure_file_name - choose a different filename to save the
                                  calibration curve fit figure (string) [default
                                  = "cal_curve.png"]
"""
        if not self.fit_Failed:
            g = gs.GridSpec(2,1,height_ratios=[globals.HEIGHT_RATIO_1, globals.HEIGHT_RATIO_2])
            plt.subplot(g[0])
            plt.plot(self.correctedDt,\
                   self.correctedLitCcs, \
                   'ko' , \
                   fillstyle='none', \
                   markeredgewidth=1.0, \
                   label="calibrants")
            plt.plot(self.correctedDt,
                    self.baseCalCurve(self.correctedDt,\
                                        self.optparams[0],\
                                        self.optparams[1],\
                                        self.optparams[2]),\
                    'black', \
                    label="fitted curve")
            plt.legend(loc="best")
            plt.title("CCS Calibration")
            plt.ylabel("corrected CCS")
            plt.subplot(g[1])
            plt.bar(self.correctedDt, \
                    numpy.array((100 * (self.calLitCcs - self.calCalcCcs) / self.calLitCcs)),
                    0.25, \
                    color='black', \
                    align='center')
            plt.xlabel("corrected drift time (ms)")
            plt.ylabel("residual CCS (%)")
            plt.axhline(y=0, color='black')
            plt.savefig(figure_file_name, bbox_inches='tight', dpi=500)
            plt.close()
        else:
            raise ValueError ("optimized fit parameters have not been generated,\
                              \nfitCalCurve() must be successfully run first!")


class CcsCalibrationExt(CcsCalibration):
    """
CcsCalibrationExt

An interface to the CcsCalibration object that can be used by just supplying CCS calibrant masses, drift times,
and reference CCS values. This way, a user may construct a calibration curve, create a curve figure, and obtain
calibrated CCS values in their own programs without using all of the other machinery for obtaining and
structuring inputs/outputs
"""

    def __init__(self, calibrant_mz, calibrant_dt, calibrant_ccs, \
                 init_params=(500, 0, 0.5), edc=1.35, max_fev=5000, do_fit=True):
        """
CcsCalibrationExt.__init__

Initializes all of the internal parameters needed to perform the CCS calibration

Input(s):
    calibrant_mz            - list of calibrant m/z values (list(float))
    calibrant_dt            - list of calibrant drift times (list(float))
    calibrant_ccs           - list of calibrant ccs values (list(float))
    [optional] init_params  -
    [optional] edc          -
    [optional] max_fev      -
    [optional] do_fit       -
"""
        # store some calculation constants
        self.edc = edc
        self.n2_mass = 28.0134
        ### TODO: implement helium option
        self.he_mass = 4.0026
        self.max_fev = max_fev
        self.optparams = init_params
        # make numpy arrays with calibrant m/z, dt, and CCS
        self.calMasses, self.calDriftTimes, self.calLitCcs = \
                    numpy.array(calibrant_mz), numpy.array(calibrant_dt), numpy.array(calibrant_ccs)
        # make arrays with corrected drift time and CCS
        self.correctedDt = self.correctedDriftTime(self.calDriftTimes, self.calMasses)
        self.correctedLitCcs = self.calLitCcs * numpy.sqrt(self.reducedMass(self.calMasses))
        # automatically perform calibration if asked to do so
        if do_fit:
            # perform the calibration
            self.fitCalCurve()
            # make an array with calibrant calculated ccs
            self.calCalcCcs = self.getCalibratedCcs(self.calMasses, self.calDriftTimes)

