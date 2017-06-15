"""
    Tests for the ParseInputFile object

    2017/06/01
    Dylan H. Ross
"""


from input.ParseInputFile import ParseInputFile


# define the paths to the input file(s)
TEST_PATH = "CcsCal/tests/files/"
TEST_INPUT_01 = TEST_PATH + "test_input_file_01.txt"
TEST_INPUT_02 = TEST_PATH + "test_input_file_02.txt"
TEST_INPUT_03 = TEST_PATH + "test_input_file_03.txt"
TEST_INPUT_04 = TEST_PATH + "test_input_file_04.txt"


def test_shuffled_parameters(print_params=False):
    """
input_parsing.test_shuffled_parameters
    description:
        uses three input files with identical parameters but in shuffled order, checks that all
        of the parameters are the same. The second file has two comment sections switched but
        in the same position relative to the list parameters while the second completely reorders
        the parameters

        *uses test input files 1-3*
    parameters:
        print_params (bool) -- Print the parameters from each of the input files [optional,
                                default=False]
    returns:
        pass (bool) - result of the test
"""
    # REFERENCE VALUES FOR PARAMETERS
    rfn = "/Users/DylanRoss/Desktop/Projects/ccscal-package/ccscal-report.txt"
    mwn = 0.5
    edc = 1.35
    tpi = 69.0
    sgw = 5
    sgp = 3
    cff = "/Users/DylanRoss/Desktop/Projects/ccscal-package/cal-curve.png"
    cdf = "/Users/DylanRoss/Desktop/Projects/ccscal-package/IM-polyala.txt"
    crd = "/Users/DylanRoss/Desktop/Projects/ccscal-package/"

    # initialize the three ParseInput objects
    Pif1 = ParseInputFile(TEST_INPUT_01)
    Pif2 = ParseInputFile(TEST_INPUT_02)
    Pif3 = ParseInputFile(TEST_INPUT_03)

    if (print_params):
        print "-----input-file-1------"
        print Pif1
        print "-----input-file-2------"
        print Pif2
        print "-----input-file-3------"
        print Pif3
        print "-----------------------"


    # test parameter by parameter against the reference values
    files = {"test file 1":Pif1, "test file 2":Pif2, "test file 3":Pif3}
    for file in files:
        if files[file].reportFileName != rfn:
            print "\t\tError: report file name in", file, "does not match reference"
            return False
        if files[file].massWindow != mwn:
            print "\t\tError: mass window in", file, "does not match reference"
            return False
        if files[file].edc != edc:
            print "\t\tError: EDC parameter in", file, "does not match reference"
            return False
        if files[file].TOFPusherInt != tpi:
            print "\t\tError: TOF pusher interval in", file, "does not match reference"
            return False
        if files[file].savgolWindow != sgw:
            print "\t\tError: Savitsky-Golay smooth window in", file, "does not match reference"
            return False
        if files[file].savgolPoly != sgp:
            print "\t\tError: Savitsky-Golay smooth polynomial order in", file, "does not match reference"
            return False
        if files[file].calCurveFileName != cff:
            print "\t\tError: calibration curve file name in", file, "does not match reference"
            return False
        if files[file].calDataFile != cdf:
            print "\t\tError: calibration data file in", file, "does not match reference"
            return False
        if files[file].compoundDataDir != crd:
            print "\t\tError: compound data directory in", file, "does not match reference"
            return False

    # if everything works return True for a pass
    return True


def test_terse_input():
    """
input_parsing.test_terse_input
    description:
        tests input file with only the minimum required parameters

        *uses test input file 4*
"""
    pass


# **the primary method for running all of the tests**
def run():
    """
input_parsing.run
    description:
        runs all of the (currently implemented) individual tests
    parameters:
        no
    returns:
        passed_all (bool) - all tests passed
"""
    print "\ttesting input file with shuffled parameters..."
    assert test_shuffled_parameters()
    print "\t...PASS"

    # if everything passed return True for success
    return True

