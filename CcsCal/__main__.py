"""
        This is the execution path to follow if this program is called directly through
        the command line.

        The following argument is required:
            -i, --input         full path to ccscal_input.txt
"""


from CcsCal.input.RawData import RawData
from CcsCal.processing.Report import Report
from CcsCal.processing.GaussFit import GaussFit
from CcsCal.input.ParseInputFile import ParseInputFile
from CcsCal.processing.CcsCalibration import CcsCalibration


import argparse
import time


if __name__ == '__main__':
    start_time = time.time()
    #
    #  PARSE THE COMMAND-LINE ARGUMENTS
    #
    print()
    # string containing program description
    pdesc = """This program refers to a specified input file and automatically
performs a CCS calibration then obtains calibrated CCS for all
specified masses, finally printing a full report containing the
results of the calibration and CCS of all compounds"""
    # create an ArgumentParser object
    parser = argparse.ArgumentParser(description=pdesc)
    # add arguments
    parser.add_argument('-i',
                        '--input',
                        required=False,
                        help='full path to ccscal_input.txt',
                        dest="path_to_input",
                        metavar='"/full/path/to/ccscal_input.txt"')
    parser.add_argument('--test',
                        required=False,
                        help='runs the included test suite',
                        dest='test',
                        action='store_true')
    # parse arguments
    args = parser.parse_args()
    # check for the test flag, if it's present run the test suite and do nothing else
    if args.test:
        from CcsCal.tests import all_tests
        all_tests.run()
        exit()
    # print the help message at the beginning of each run
    parser.print_help()
    # all of the command-line arguments are stored in args
    #
    # PARSE THE INPUT FILE
    #
    input_data = ParseInputFile(args.path_to_input)
    #
    # INITIALIZE THE REPORT GENERATOR
    #
    report = Report(input_data.reportFileName)
    #
    # PERFORM CCS CALIBRATION
    #
    print("\nPerforming CCS Calibration...")
    # create CcsCalibration object
    calibration = CcsCalibration(input_data.calDataFile,
                                 input_data.calibrantData[0],
                                 input_data.calibrantData[1],
                                 mass_window=input_data.massWindow,
                                 edc=input_data.edc)
    # save a graph of the fitted calibration curve
    calibration.saveCalCurveFig(figure_file_name=input_data.calCurveFileName)
    # write the calibration statistics to the report file
    report.writeCalibrationReport(calibration)
    print("...DONE")
    #
    # EXTRACT DRIFT TIMES OF COMPOUNDS AND GET THEIR CALIBRATED CCS
    #
    # write the header for the compound data table in the report
    report.writeCompoundDataTableHeader()
    # cycle through each compound input filename/mass pair and perform drift time extraction
    for n in range(len(input_data.compoundFileNames)):
        print("Extracting Drift Time for Mass:", input_data.compoundMasses[n],
                "from Data File:", input_data.compoundFileNames[n], "(" + str(n + 1),
                "of", str(len(input_data.compoundFileNames)) + ")...")
        # extract drift time and get calibrated CCS for the filename/mass pair
        driftTime = GaussFit(RawData((input_data.compoundDataDir + input_data.compoundFileNames[n]),
                                        input_data.compoundMasses[n],
                                        input_data.massWindow)).getDriftTime()
        print("Getting Calibrated CCS...")
        ccs =  calibration.getCalibratedCcs(input_data.compoundMasses[n], driftTime)
        report.writeCompoundDataTableLine(input_data.compoundFileNames[n], input_data.compoundMasses[n], driftTime, ccs)
    #
    # CLOSE THE REPORT FILE
    report.finish()
    #
    print("\nCcsCal Complete.")
    #
    # COMPLETE
    #
    # report the total time taken to the user
    end_time = time.time()
    print("\ntotal time: ", round((end_time - start_time)), "s")
