from CcsCal import globals


import time
import os


class Report():

    def __init__ (self, report_file_name):
        """
Report.__init__

Generates a report as a text file containing information about the run paramters, the CCS
calibration and analyte drift times and CCS values

Input(s):
    report_file_name    - path to the report file to generate (str)
"""
        self.report_file_name = report_file_name
        self.report_file = open(self.report_file_name, "w")
        self.writeHeader()


    def writeHeader(self):
        """
Report.writeHeader

Writes a header for report file with the name of the report file and the date it
was generated

Input(s):
    none
"""
        self.wLn(os.path.split(os.path.splitext(self.report_file_name)[0])[1])
        self.wLn("Generated by CcsCal on " + time.strftime("%c"))
        self.wLn("====================================================")
        self.wLn()
        self.wLn()


    def writeCalibrationReport(self, ccs_calibration_object):
        """
Report.writeCalibrationReport

Writes a full report on how the CCS calibration went. This includes:
    - A table of m/z values and their extracted drift times
    - The fit parameters for the CCS calibration curve

Input(s):
    ccs_calibration_object      - The CcsCalibration object containing all of the
                                    relevant information about the calibration
                                    (CcsCalibration)
"""
        self.wLn("+-----------------+")
        self.wLn("| CCS CALIBRATION |")
        self.wLn("+-----------------+")
        self.wLn()
        self.wLn("CCS calibrants extracted drift times:")
        self.writeDriftTimeTable(ccs_calibration_object.calMasses,\
                                 ccs_calibration_object.calDriftTimes)
        self.wLn()
        self.wLn("Optimized calibration curve fit parameters:")
        self.wLn("\tcorrected ccs = A * ((corrected drift time) + t0) ** B")
        self.wLn("\t\tA = " + str(ccs_calibration_object.optparams[0]))
        self.wLn("\t\tt0 = " + str(ccs_calibration_object.optparams[1]))
        self.wLn("\t\tB = " + str(ccs_calibration_object.optparams[2]))
        self.wLn()

        self.wLn("Calibrant CCS, calculated vs. literature:")
        self.writeCcsComparisonTable(ccs_calibration_object.calMasses,\
                                     ccs_calibration_object.calLitCcs,\
                                     ccs_calibration_object.calCalcCcs)
        self.wLn()


    def writeDriftTimeTable(self, masses, drift_times):
        """
Report.writeDriftTimeTable

Writes a table of m/z values and their drift times separated by tabs with
the following format:

    m/z         drift time (ms)
    ---------------------------
    mz 1        dt 1
    mz 2        dt 2
    ...             ...

Input(s):
    masses                      - m/z values (list)
    drift_times                 - drift time values (list)
"""
        self.wLn("m/z\t\tdrift time (ms)")
        self.wLn("---------------------------")
        for n in range (len(masses)):
            #outstr = str(round(masses[n], 3)) + "\t\t" + str(round(drift_times[n], 3))
            self.wLn("{: 10.4f}    {: 5.2f}".format(masses[n], drift_times[n]))
        self.wLn()


    def writeCcsComparisonTable(self, masses, literature_ccs, calculated_ccs):
        """
Report.writeCcsComparisonTable

Writes a table of m/z values, their literature ccs values, the calculated ccs and residual
ccs with the following format:

    m/z         lit ccs (Ang^2)     calc ccs (Ang^2)    residual ccs (Ang^2, %)
    ---------------------------------------------------------------------------
    mz 1        lit_ccs 1           calc_ccs 1          resid 1,    resid% 1
    mz 2        lit_ccs 2           calc_ccs 2          resid 2,    resid% 2
    ...         ...                 ...                 ...,        ...

Input(s):
    masses                      - m/z values (list)
    literature_ccs              - ccs literature values (list)
    calculated_ccs              - calculated ccs values (list)
"""
        self.wLn("m/z        lit ccs (Ang^2)     calc ccs (Ang^2)      residual ccs (Ang^2, %)")
        self.wLn("----------------------------------------------------------------------------")
        for n in range (len(masses)):
            self.wLn("{: 10.4f}   {: 6.3f}             {: 6.3f}             {: 6.3f}    {: 6.3f}".format(\
                        masses[n], \
                        literature_ccs[n], \
                        calculated_ccs[n], \
                        (literature_ccs[n] - calculated_ccs[n]), \
                        (100.0 *(literature_ccs[n] - calculated_ccs[n]) / (literature_ccs[n]))))
        self.wLn()


    def writeCompoundDataTableHeader(self):
        """
Report.writeCompoundDataTableHeader

Writes the header for a table displaying the extracted drift time and calibrated
CCS for the datafile/mass pairs with the following format:

    data file name      m/z     drift time (ms)     ccs (Ang^2)
    -----------------------------------------------------------
    data_file_1.txt     mz 1        dt 1            ccs 1
    data_file_1.txt     mz 1        dt 1            ccs 1
    ...                 ...         ...             ...

Input(s):
    none
"""
        self.wLn("+---------------+")
        self.wLn("| COMPOUND DATA |")
        self.wLn("+---------------+")
        self.wLn()
        self.wLn("Compounds extracted drift times and calibrated CCS:")
        self.wLn("data file name                     m/z       drift time (ms)     ccs (Ang^2)")
        self.wLn("----------------------------------------------------------------------------")


    def writeCompoundDataTableLine(self, data_file_name, mz, dt, ccs):
        """
Report.writeCompoundDataTableLine

Writes a single line for a table displaying the extracted drift time and calibrated
CCS for the datafile/mass pairs with the following format:

    data file name      m/z     drift time (ms)     ccs (Ang^2)
    -----------------------------------------------------------
    data_file_1.txt     mz 1        dt 1            ccs 1
    data_file_1.txt     mz 1        dt 1            ccs 1
    ...                 ...         ...             ...

Input(s):
    data_file_name              - name of the data file (string)
    mz                          - mass to charge of compound (float)
    dt                          - extracted drift time of the compound (float)
    ccs                         - calculated ccs value (float)
"""
        self.wLn("{:32s} {: 9.4f}      {: 6.3f}         {: 6.3f}".format(data_file_name, mz, dt, ccs))


    def wLn(self, line_to_write=""):
        """
Report.wLn

convenient shorthand for self.report_file.write("..." + "\n")

Input(s):
    [optional] line_to_write    - line to write to file (string)
"""
        self.report_file.write(line_to_write + "\n")


    def finish(self):
        """
Report.finish

Closes the report file

Input(s):
    none
"""
        self.report_file.close()