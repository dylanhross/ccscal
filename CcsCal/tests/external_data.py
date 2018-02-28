"""
    Tests for the CcsCalibrationExt object, for processesing data from external sources using the same CCS
    calibration scheme

    2017/06/20
    Dylan H. Ross
"""


from CcsCal.processing.CcsCalibration import CcsCalibrationExt


from numpy import genfromtxt, abs, mean
from os import remove
from os.path import isfile


# define the path to the first external data file
EXTDATA1_PATH = "CcsCal/tests/files/external_data1.csv"
# define path to the second external data file
EXTDATA2_PATH = "CcsCal/tests/files/external_data2.csv"


def percent_diff(a, b):
    """
external_data.percent_diff
    description:
        determines the percent difference between two numbers a and b
    parameters:
        a, b (float) -- two numbers
    returns:
        percent_difference (float) -- percent difference of a and b
"""
    return 100. * abs(a - b) / mean([a, b])


def simple_test():
    """
external_data.simple_test
    description:
        a simple test to make sure the object can be initialized with data without errors
    parameters:
        no
    returns:
        passed (bool) - test passed
"""
    # load the external dataset
    ext_data = genfromtxt(EXTDATA1_PATH, delimiter=",", unpack=True)
    # initialize the CcsCalibrationExt object
    cce = CcsCalibrationExt(*ext_data)
    # passes as long as there were no errors
    return True


def test_ccs_cal_noauto():
    """
external_data.test_ccs_cal_noauto
    description:
        initialize the object without calling fitCalCurve(), then externally calls fitCalCurve() and then
        populates self.calCalcCcs. passes as long as there are no errors
    parameters:
        no
    returns:
        passed (bool) - test passed
"""
    # load the external dataset
    ext_data = genfromtxt(EXTDATA1_PATH, delimiter=",", unpack=True)
    # initialize the CcsCalibrationExt object without automatically doing the curve fitting
    cce = CcsCalibrationExt(*ext_data, do_fit=False)
    # try to do get calibrated CCS, should be an error
    try:
        cce.getCalibratedCcs(ext_data[0][0], ext_data[1][0])
        # if the above does not throw an error, then the test has failed
        print("\t\tError: getCalibratedCcs() cannot be called prior to curve fitting")
        return False
    except ValueError:
        pass
    # now call fitCalCurve
    cce.fitCalCurve()
    # populate calCalcCcs
    cce.calCalcCcs = cce.getCalibratedCcs(cce.calMasses, cce.calDriftTimes)
    # try getCalibratedCcs again
    cce.getCalibratedCcs(ext_data[0][0], ext_data[1][0])
    # passes as long as there were no errors
    return True


def test_get_cal_ccs():
    """
external_data.test_get_cal_ccs
    description:
        initialize the object normally, then test that getting calibrated ccs works properly and that
        the calibrated ccs for the test compounds are within 5% of previously obtained reference values
    parameters:
        no
    returns:
        passed (bool) - test passed
"""
    # load the external dataset
    ext_data = genfromtxt(EXTDATA1_PATH, delimiter=",", unpack=True)
    # initialize the CcsCalibrationExt object
    cce = CcsCalibrationExt(*ext_data)
    # load the compound dataset
    cmpd_data = genfromtxt(EXTDATA2_PATH, delimiter=",", unpack=True)
    for i in range(len(cmpd_data[0])):
        if percent_diff(cce.getCalibratedCcs(cmpd_data[0][i], cmpd_data[1][i]), cmpd_data[2][i]) > 5:
            print("\t\tError: compound with m/z", cmpd_data[0][i], "calibrated CCS more than 5% different from reference")
            return False
    # if it makes it through the entire list of compounds then it passes
    return True


def test_calibrant_resids():
    """
external_data.test_calibrant_resids
    description:
        initialize the object normally, then tests that the calibrated CCS of the calibrants are within 5% of the
        reference values
    parameters:
        no
    returns:
        passed (bool) - test passed
"""
    # load the external dataset
    ext_data = genfromtxt(EXTDATA1_PATH, delimiter=",", unpack=True)
    # initialize the CcsCalibrationExt object
    cce = CcsCalibrationExt(*ext_data)
    for i in range(len(cce.calCalcCcs)):
        if percent_diff(cce.calCalcCcs[i], cce.calLitCcs[i]) > 5:
            print("\t\tError: calibrant with m/z", cce.calMasses[i], "calibrated CCS more than 5% different from reference")
            return False
    # if it makes it through the entire list of compounds then it passes
    return True


def test_cal_curve_figure():
    """
external_data.test_cal_curve_figure
    description:
        initialize the object normally, then tests that the CCS calibration curve figure is generated properly
    parameters:
        no
    returns:
        passed (bool) - test passed
"""
    # load the external dataset
    ext_data = genfromtxt(EXTDATA1_PATH, delimiter=",", unpack=True)
    # initialize the CcsCalibrationExt object
    cce = CcsCalibrationExt(*ext_data)
    cce.saveCalCurveFig(figure_file_name="CcsCal/tests/files/test_cal_curve_figure.png")
    # if no errors, check that the image exists then delete it and return True
    if isfile("CcsCal/tests/files/test_cal_curve_figure.png"):
        remove("CcsCal/tests/files/test_cal_curve_figure.png")
        return True
    else:
        # anything goes wrong, FAIL
        print("\t\tError: could not find the calibration curve figure")
        return False


# *the primary method for running all of the tests*
def run():
    """
external_data.run
    description:
        runs all of the (currently implemented) individual tests
    parameters:
        no
    returns:
        passed_all (bool) - all tests passed
"""
    print("\trunning simple initialization test...")
    assert simple_test()
    print("\t...PASS")

    print("\trunning initialization test without automatic curve fitting...")
    assert test_ccs_cal_noauto()
    print("\t...PASS")

    print("\trunning CCS calibration test with known reference compounds...")
    assert test_get_cal_ccs()
    print("\t...PASS")

    print("\ttesting calibrant CCS calibration residuals...")
    assert test_get_cal_ccs()
    print("\t...PASS")

    print("\ttesting calibration curve figure generation...")
    assert test_cal_curve_figure()
    print("\t...PASS")

    # if everything passed return True for success
    return True
