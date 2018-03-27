"""
    Tests for the complete CcsCal functionality, i.e. all of the steps performed in CcsCal/__main__.py using
    actual data (raw and pre-processed).

    2018/02/28
    Dylan H. Ross
"""


from CcsCal.input.RawData import RawData
from CcsCal.processing.Report import Report
from CcsCal.processing.GaussFit import GaussFit
from CcsCal.input.ParseInputFile import ParseInputFile
from CcsCal.processing.CcsCalibration import CcsCalibration


from numpy import array, abs


# paths to input files
INPUT_FILE_05 = "CcsCal/tests/files/test_input_file_05.txt"
# store the CcsCalibration instance from single_ccs_calibration() so that it can be used in further tests without
# having to wait for another instance to be generated. This is sloppy/bad form/sad, I know, but this kludge only
# exits in this test script so I am OK with it.
CCSCALIBRATION_01 = None


def single_ccs_calibration():
    """
ccscal_main.single_ccs_calibration
    description:
        Initializes a ParseInputFile object using CcsCal/tests/files/test_input_file_05.txt then initializes a
        CcsCalibration object using the input file parameters. Passes as long as there are no errors.
    parameters:
        no
    returns:
        passed (bool) - test passed
"""
    # initialize ParseInputFile object
    input_params = ParseInputFile(INPUT_FILE_05)
    # adjust selected parameters (that started off with dummy values)
    input_params.calDataFile = "CcsCal/tests/files/IM_polyala.txt"
    # create CcsCalibration object, DO NOT pre-process .txt data files and do not generate figures of the gaussian fits
    global CCSCALIBRATION_01   # store the instance in a global variable (starts off as None)
    CCSCALIBRATION_01 = CcsCalibration(input_params.calDataFile,
                                       input_params.calibrantData[0],
                                       input_params.calibrantData[1],
                                       mass_window=input_params.massWindow,
                                       edc=input_params.edc,
                                       pp=False,
                                       gauss_figs=False)
    # passes as long as there were no errors
    return True


def single_ccs_calibration_accuracy():
    """
ccscal_main.single_ccs_calibration_accuracy
    description:
        Tests the accuracy of the previously generated single CCS calibration. Absolute residual CCS must be below 3%
        for all calibrants.
    parameters:
        no
    returns:
        passed (bool) - test passed
"""
    if not CCSCALIBRATION_01:
        # this test either was run before the CcsCalibration was generated or generating the CcsCalibration failed
        print("\t\tError: Single CCS Calibration was not generated properly prior to testing for accuracy.")
        return False
    residuals = array(100. * (CCSCALIBRATION_01.calLitCcs - CCSCALIBRATION_01.calCalcCcs) / CCSCALIBRATION_01.calLitCcs)
    passed = True
    for residual, mass in zip(residuals, CCSCALIBRATION_01.calMasses):
        if abs(residual) > 3.:
            print("\t\tError: encountered residual CCS >3% " +
                  "({:.1f}%, m/z={:.4f}) in CCS Calibration".format(residual, mass))
            passed = False
    return passed


# *the primary method for running all of the tests*
def run():
    """
ccscal_main.run
    description:
        runs all of the (currently implemented) individual tests
    parameters:
        no
    returns:
        passed_all (bool) - all tests passed
"""
    print("\t(1 of 2) generating a single CCS calibration (no pre-processing)...")
    assert single_ccs_calibration()
    print("\t...PASS")

    print("\t(2 of 2) checking single CCS calibration accuracy (no pre-processing)...")
    assert single_ccs_calibration_accuracy()
    print("\t...PASS")

    # if everything passed return True for success
    return True
